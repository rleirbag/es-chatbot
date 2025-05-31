from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory
from app.models.user import User
from app.config.database import commit, get_by_attribute, delete
from app.schemas.error import Error


class DeleteChatHistoryUseCase:
    @staticmethod
    @commit
    def execute(db: Session, chat_history_id: int, user_email: str):
        user, error = get_by_attribute(db, User, 'email', user_email)
        if error or not user:
            return None, Error(error_code=404, error_message="Usuário não encontrado")
        chat_history = db.query(ChatHistory).filter(ChatHistory.id == chat_history_id, ChatHistory.user_id == user.id).first()
        if not chat_history:
            return None, Error(error_code=404, error_message="Registro de chat não encontrado ou acesso não autorizado")
        chat_history, error = delete(db, ChatHistory, chat_history_id)
        if error:
            return None, error
        return chat_history, None 