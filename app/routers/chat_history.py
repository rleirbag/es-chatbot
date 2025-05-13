from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db, get_by_attribute
from app.models.user import User
from app.schemas.chat_history import ChatHistory, ChatHistoryCreate, ChatHistoryUpdate
from app.services.chat_history import ChatHistoryService
from app.utils.security import get_current_user

router = APIRouter(prefix="/chat-history", tags=["Chat History"])


@router.get("", response_model=List[ChatHistory])
async def get_user_chat_history(
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna todo o histórico de chat do usuário autenticado.
    """
    user, error = get_by_attribute(db, User, 'email', user_info['email'])
    if error or not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    chat_history_service = ChatHistoryService(db)
    return chat_history_service.get_user_chat_history(user.id)


@router.get("/{chat_history_id}", response_model=ChatHistory)
async def get_chat_history(
    chat_history_id: int,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna um registro específico do histórico de chat.
    """
    user, error = get_by_attribute(db, User, 'email', user_info['email'])
    if error or not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    chat_history_service = ChatHistoryService(db)
    chat_history = chat_history_service.get_chat_history(chat_history_id)
    
    if not chat_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de chat não encontrado"
        )
    
    if chat_history.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este registro"
        )
    
    return chat_history


@router.post("", response_model=ChatHistory, status_code=status.HTTP_201_CREATED)
async def create_chat_history(
    chat_history: ChatHistoryCreate,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo registro no histórico de chat.
    """
    user, error = get_by_attribute(db, User, 'email', user_info['email'])
    if error or not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    chat_history_service = ChatHistoryService(db)
    return chat_history_service.create_chat_history(user.id, chat_history)


@router.put("/{chat_history_id}", response_model=ChatHistory)
async def update_chat_history(
    chat_history_id: int,
    chat_history: ChatHistoryUpdate,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza um registro do histórico de chat.
    """
    user, error = get_by_attribute(db, User, 'email', user_info['email'])
    if error or not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    chat_history_service = ChatHistoryService(db)
    existing_chat = chat_history_service.get_chat_history(chat_history_id)
    
    if not existing_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de chat não encontrado"
        )
    
    if existing_chat.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este registro"
        )
    
    updated_chat = chat_history_service.update_chat_history(chat_history_id, chat_history)
    if not updated_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erro ao atualizar registro de chat"
        )
    
    return updated_chat


@router.delete("/{chat_history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_history(
    chat_history_id: int,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove um registro do histórico de chat.
    """
    user, error = get_by_attribute(db, User, 'email', user_info['email'])
    if error or not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    chat_history_service = ChatHistoryService(db)
    existing_chat = chat_history_service.get_chat_history(chat_history_id)
    
    if not existing_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de chat não encontrado"
        )
    
    if existing_chat.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este registro"
        )
    
    if not chat_history_service.delete_chat_history(chat_history_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erro ao deletar registro de chat"
        ) 