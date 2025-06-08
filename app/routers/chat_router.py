from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.config.database import get_db
from app.schemas.chat import ChatRequest
from app.schemas.chat_history import ChatHistoryCreate, ChatHistoryUpdate
from app.services.chat_history import ChatHistoryService
from app.services.llm.llm_service import LLMService
from app.services.users.get_user_by_email_use_case import GetUserByEmailUseCase
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
            chat_messages={'messages': []}
        )
        history = chat_history_service.create_chat_history(
            user_id=user_id, chat_history=chat_history_create
        )

    chat_messages = (
        history.chat_messages.get('messages', [])
        if history.chat_messages
        else []
    )

    # Converte o histórico para o formato de prompt
    prompt_messages = []
    for msg in chat_messages:
        prompt_messages.append({'role': msg['role'], 'content': msg['content']})

    async def stream_response() -> AsyncGenerator[str, None]:
        # Adiciona a nova mensagem do usuário ao prompt
        prompt_messages.append({'role': 'user', 'content': request.message})

        # Constrói o prompt final como uma string
        prompt_text = '\n'.join(
            [f"{m['role']}: {m['content']}" for m in prompt_messages]
        )

        llm_service = LLMService()
        response_iterator = llm_service.execute(prompt=prompt_text)

        llm_response_content = ''
        async for chunk in response_iterator:
            llm_response_content += chunk
            yield chunk

        # Atualiza o histórico com a pergunta e a resposta
        chat_messages.append({'role': 'user', 'content': request.message})
        chat_messages.append(
            {'role': 'assistant', 'content': llm_response_content}
        )

        update_data = ChatHistoryUpdate(
            chat_messages={'messages': chat_messages}
        )
        chat_history_service.update_chat_history(
            chat_history_id=history.id,
            chat_history=update_data,
        )

    return StreamingResponse(stream_response(), media_type='text/event-stream') 