from typing import AsyncGenerator
import chromadb

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.config.database import get_db
from app.schemas.chat import ChatRequest
from app.schemas.chat_history import ChatHistoryCreate, ChatHistoryUpdate
from app.services.chat_history import ChatHistoryService
from app.services.llm.llm_service import LLMService
from app.services.rag.rag_service import RagService
from app.services.users.get_user_by_email_use_case import GetUserByEmailUseCase
from app.services.anonymous_questions.anonymous_question_service import AnonymousQuestionService
from app.utils.security import get_current_user


router = APIRouter()


@router.post('/chat')
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
) -> StreamingResponse:
    chat_history_service = ChatHistoryService(db)
    user_email = current_user.get('email')

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials, email not found.',
        )

    user = GetUserByEmailUseCase.execute(db, email=user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with email {user_email} not found.',
        )

    user_id = user.id

    if request.chat_history_id:
        history = chat_history_service.get_chat_history(
            request.chat_history_id
        )
        if history and history.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You do not have permission to access this chat history.',
            )
    else:
        history = None

    if not history:
        chat_history_create = ChatHistoryCreate(
            chat_messages={'messages': []},
            user_id=user_id
        )
        history = chat_history_service.create_chat_history(
            user_id=user_id, chat_history=chat_history_create
        )

    history_id = history.id
    
    chat_messages = (
        history.chat_messages.get('messages', [])
        if history.chat_messages
        else []
    )

    prompt_messages = []
    for msg in chat_messages:
        prompt_messages.append({'role': msg['role'], 'content': msg['content']})

    user_message = request.message
    llm_message = user_message
    context = ''
    source_links = []
    
    # Detecta e salva dúvida anônima
    try:
        anonymous_service = AnonymousQuestionService(db)
        detected_question = anonymous_service.detect_and_save_question(
            message=user_message,
            context=""  # Ainda não temos o contexto aqui
        )
        if detected_question:
            print(f"Dúvida anônima salva: {detected_question.topic} - {detected_question.question[:50]}...")
    except Exception as e:
        print(f"Erro ao salvar dúvida anônima: {e}")
        # Não falhamos o chat por causa disso
    
    try:
        if not user_message.startswith('/desafio'):
            rag_service = RagService()
            search_results = rag_service.search(query=user_message)
            
            # Extract content and collect unique source links
            context_parts = []
            seen_links = set()
            
            for result in search_results:
                context_parts.append(result["content"])
                
                # Collect unique Google Drive links
                metadata = result.get("metadata", {})
                drive_link = metadata.get("drive_link")
                source_name = metadata.get("source")
                
                if drive_link and drive_link not in seen_links:
                    seen_links.add(drive_link)
                    source_links.append({
                        "name": source_name,
                        "link": drive_link
                    })
            
            context = '\n'.join(context_parts)
    finally:
        chromadb.api.client.SharedSystemClient.clear_system_cache()

    if user_message.startswith('/desafio'):
        topic = user_message.replace('/desafio', '').strip()
        if topic:
            llm_message = f'Crie um desafio sobre o seguinte tópico: {topic}'
        else:
            llm_message = 'Crie um desafio com base no contexto da nossa conversa até agora.'
    elif context:
        llm_message = f"""
        Baseado no seguinte contexto, responda a pergunta.

        Contexto:
        {context}

        Pergunta: {user_message}
        """

    async def stream_response() -> AsyncGenerator[str, None]:
        prompt_messages.append({'role': 'user', 'content': llm_message})

        prompt_text = '\n'.join(
            [f"{m['role']}: {m['content']}" for m in prompt_messages]
        )

        llm_service = LLMService()
        response_iterator = llm_service.execute(prompt=prompt_text)

        llm_response_content = ''
        async for chunk in response_iterator:
            llm_response_content += chunk
            yield chunk

        # Add source links at the end of the response
        if source_links and not user_message.startswith('/desafio'):
            links_section = "\n\n**Fontes consultadas:**\n"
            for source in source_links:
                links_section += f"- [{source['name']}]({source['link']})\n"
            
            # Yield the links section
            for char in links_section:
                yield char
            
            # Add links to the response content for storage
            llm_response_content += links_section

        chat_messages.append({'role': 'user', 'content': request.message})
        chat_messages.append(
            {'role': 'assistant', 'content': llm_response_content}
        )

        update_data = ChatHistoryUpdate(
            chat_messages={'messages': chat_messages}
        )
        
        # Cria uma nova instância do serviço com uma nova sessão para evitar problemas de concorrência
        from app.config.database import SessionLocal
        with SessionLocal() as new_db:
            new_chat_history_service = ChatHistoryService(new_db)
            new_chat_history_service.update_chat_history(
                chat_history_id=history_id,
                chat_history=update_data,
            )

    return StreamingResponse(stream_response(), media_type='text/event-stream') 