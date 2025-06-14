from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import UserRole
from app.schemas.anonymous_question import (
    AnonymousQuestionCreate,
    AnonymousQuestionResponse,
    AnonymousQuestionsList,
    AnonymousQuestionStats
)
from app.services.anonymous_questions.anonymous_question_service import AnonymousQuestionService
from app.services.users.get_user_by_email_use_case import GetUserByEmailUseCase
from app.utils.security import get_current_user

router = APIRouter(tags=["Questions"])


@router.post(
    "/anonymous-questions",
    response_model=AnonymousQuestionResponse,
    summary="Criar dúvida anônima",
    description="Cria uma nova dúvida anônima no sistema"
)
async def create_question(
    question: AnonymousQuestionCreate,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova dúvida anônima.
    
    Este endpoint permite que qualquer usuário submeta uma dúvida de forma anônima,
    especificando apenas o tema e a pergunta.
    """
    try:
        service = AnonymousQuestionService(db)
        created_question = service.create_question(question)
        return created_question
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar dúvida: {str(e)}"
        )


@router.get(
    "/anonymous-questions",
    response_model=AnonymousQuestionsList,
    summary="Listar dúvidas anônimas",
    description="Lista dúvidas anônimas com paginação e filtros (apenas para admins)"
)
async def get_questions(
    topic: Optional[str] = Query(None, description="Filtrar por tema"),
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user)
):
    """
    Lista dúvidas anônimas com paginação e filtros.
    
    Apenas usuários com role ADMIN podem acessar este endpoint.
    """
    # Verifica se o usuário é admin
    user_email = current_user.get('email')
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials'
        )
    
    user = GetUserByEmailUseCase.execute(db, email=user_email)
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Apenas administradores podem acessar as dúvidas'
        )
    
    try:
        service = AnonymousQuestionService(db)
        questions, total = service.get_questions(topic=topic, page=page, per_page=per_page)
        
        return AnonymousQuestionsList(
            questions=questions,
            total=total,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar dúvidas: {str(e)}"
        )


@router.get(
    "/anonymous-questions/stats",
    response_model=list[AnonymousQuestionStats],
    summary="Estatísticas das dúvidas",
    description="Retorna estatísticas das dúvidas agrupadas por tema (apenas para admins)"
)
async def get_question_stats(
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user)
):
    """
    Retorna estatísticas das dúvidas agrupadas por tema.
    
    Apenas usuários com role ADMIN podem acessar este endpoint.
    """
    # Verifica se o usuário é admin
    user_email = current_user.get('email')
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials'
        )
    
    user = GetUserByEmailUseCase.execute(db, email=user_email)
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Apenas administradores podem acessar as estatísticas'
        )
    
    try:
        service = AnonymousQuestionService(db)
        stats = service.get_question_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )


@router.get(
    "/anonymous-questions/topics",
    response_model=list[str],
    summary="Temas mais comuns",
    description="Retorna lista dos temas mais comuns das dúvidas (apenas para admins)"
)
async def get_common_topics(
    limit: int = Query(10, ge=1, le=50, description="Número máximo de temas a retornar"),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user)
):
    """
    Retorna os temas mais comuns das dúvidas.
    
    Apenas usuários com role ADMIN podem acessar este endpoint.
    """
    # Verifica se o usuário é admin
    user_email = current_user.get('email')
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials'
        )
    
    user = GetUserByEmailUseCase.execute(db, email=user_email)
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Apenas administradores podem acessar os temas'
        )
    
    try:
        service = AnonymousQuestionService(db)
        topics = service.get_most_common_topics(limit=limit)
        return topics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar temas: {str(e)}"
        )


@router.get(
    "/anonymous-questions/available-topics",
    response_model=list[dict],
    summary="Tópicos disponíveis",
    description="Retorna todos os tópicos de engenharia de software disponíveis para classificação"
)
async def get_available_topics(
    db: Session = Depends(get_db)
):
    """
    Retorna todos os tópicos de engenharia de software disponíveis.
    
    Este endpoint é público e pode ser usado para mostrar aos usuários
    quais tópicos estão disponíveis para classificação automática.
    """
    try:
        service = AnonymousQuestionService(db)
        topics = service.get_available_topics()
        return topics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar tópicos disponíveis: {str(e)}"
        )


@router.get(
    "/anonymous-questions/topic-suggestions",
    response_model=list[str],
    summary="Sugestões de tópicos",
    description="Retorna sugestões de tópicos baseado em texto parcial"
)
async def get_topic_suggestions(
    text: str = Query(..., description="Texto parcial para buscar sugestões"),
    limit: int = Query(5, ge=1, le=20, description="Número máximo de sugestões"),
    db: Session = Depends(get_db)
):
    """
    Retorna sugestões de tópicos baseado em texto parcial.
    
    Útil para implementar autocomplete ou sugestões em interfaces de usuário.
    """
    try:
        service = AnonymousQuestionService(db)
        suggestions = service.get_topic_suggestions(text, limit)
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar sugestões: {str(e)}"
        )


@router.get(
    "/anonymous-questions/topic-details/{topic_name}",
    response_model=dict,
    summary="Detalhes do tópico",
    description="Retorna detalhes específicos de um tópico"
)
async def get_topic_details(
    topic_name: str,
    db: Session = Depends(get_db)
):
    """
    Retorna detalhes específicos de um tópico.
    
    Inclui descrição, palavras-chave e padrões usados para classificação.
    """
    try:
        service = AnonymousQuestionService(db)
        details = service.get_topic_details(topic_name)
        
        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tópico '{topic_name}' não encontrado"
            )
        
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar detalhes do tópico: {str(e)}"
        ) 