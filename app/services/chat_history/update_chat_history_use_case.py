from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory
from app.config.database import commit, get_by_attribute, update


class UpdateChatHistoryUseCase:
    @staticmethod
    @commit
    def execute(db: Session, chat_history_id: int, update_data: dict):
        chat_history, error = update(db, ChatHistory, chat_history_id, update_data)

        if error:
            return None, error

        return chat_history, None 