from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.config.database import commit, get_by_attribute
from app.models.chat_history import ChatHistory
from app.models.user import User
from app.schemas.error import Error

class GetChatHistoryUseCase: 
    @staticmethod
    @commit
    def execute(db: Session, user_email: str) -> Tuple[Optional[List[ChatHistory]], Optional[Error]]:
        user, error = get_by_attribute(db, User, 'email', user_email)
        if error or not user:
            return None, Error(error_code=404, error_message="Usuário não encontrado")
        try:
            chat_histories = db.query(ChatHistory).filter(ChatHistory.user_id == user.id).all()
            return chat_histories, None
        except Exception as e:
            return None, Error(error_code=500, error_message=str(e))

    @staticmethod
    @commit
    def get_by_id(db: Session, chat_history_id: int, user_email: str) -> Tuple[Optional[ChatHistory], Optional[Error]]:
        user, error = get_by_attribute(db, User, 'email', user_email)
        if error or not user:
            return None, Error(error_code=404, error_message="Usuário não encontrado")
        try:
            chat_history = db.query(ChatHistory).filter(ChatHistory.id == chat_history_id, ChatHistory.user_id == user.id).first()
            if not chat_history:
                return None, Error(error_code=404, error_message="Registro de chat não encontrado ou acesso não autorizado")
            return chat_history, None
        except Exception as e:
            return None, Error(error_code=500, error_message=str(e))
