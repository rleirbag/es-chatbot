from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory
from app.config.database import commit, delete


class DeleteChatHistoryUseCase:
    @staticmethod
    @commit
    def execute(db: Session, chat_history_id: int):
        chat_history, error = delete(db, ChatHistory, chat_history_id)

        if error:
            return None, error

        return chat_history, None 