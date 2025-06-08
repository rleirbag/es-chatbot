from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from app.config.database import get_by_attribute, get_db
from app.models.user import User
from app.schemas.chat_history import (
    ChatHistory,
    ChatHistoryCreate,
    ChatHistoryUpdate,
)
from app.services.chat_history.create_chat_history_use_case import (
    CreateChatHistoryUseCase,
)
from app.services.chat_history.delete_chat_history_use_case import (
    DeleteChatHistoryUseCase,
)
from app.services.chat_history.get_chat_history_use_case import (
    GetChatHistoryUseCase,
)
from app.services.chat_history.update_chat_history_use_case import (
    UpdateChatHistoryUseCase,
)
from app.utils.security import get_current_user

router = APIRouter(prefix='/chat-history', tags=['Chat History'])


@router.get('', response_model=List[ChatHistory])
async def get_user_chat_history(
    user_info: dict = Security(get_current_user), db: Session = Depends(get_db)
):
    """
    Retorna todo o histórico de chat do usuário autenticado.
    """
    use_case = GetChatHistoryUseCase()
    chat_histories, error = use_case.execute(db, user_info['email'])
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.error_message
        )
    return chat_histories


@router.get('/{chat_history_id}', response_model=ChatHistory)
async def get_chat_history(
    chat_history_id: int,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna um registro específico do histórico de chat.
    """
    use_case = GetChatHistoryUseCase()
    chat_history, error = use_case.get_by_id(
        db, chat_history_id, user_info['email']
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.error_message
        )
    return chat_history


@router.post(
    '', response_model=ChatHistory, status_code=status.HTTP_201_CREATED
)
async def create_chat_history(
    chat_history: ChatHistoryCreate,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cria um novo registro no histórico de chat.
    """
    user, error = get_by_attribute(db, User, 'email', user_info['email'])
    if error or not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Usuário não encontrado',
        )

    # Atualiza o user_id no chat_history
    chat_history.user_id = user.id

    use_case = CreateChatHistoryUseCase()
    chat_history_created, error = use_case.execute(db, chat_history)  # type: ignore

    if error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        )

    return chat_history_created


@router.put('/{chat_history_id}', response_model=ChatHistory)
async def update_chat_history(
    chat_history_id: int,
    chat_history: ChatHistoryUpdate,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualiza um registro do histórico de chat.
    """
    update_use_case = UpdateChatHistoryUseCase()
    updated_chat, error = update_use_case.execute(
        db, chat_history_id, chat_history, user_info['email']
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.error_message
        )
    return updated_chat


@router.delete('/{chat_history_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_history(
    chat_history_id: int,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove um registro do histórico de chat.
    """
    delete_use_case = DeleteChatHistoryUseCase()
    _, error = delete_use_case.execute(db, chat_history_id, user_info['email'])
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.error_message
        )

