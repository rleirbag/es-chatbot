from sqlalchemy.orm import Session

from app.config.database import commit, get_by_attribute
from app.models.user import User

class GetChatHistoryUseCase: 
    @staticmethod
    @commit
    def get_chat_history(self, chat_history_id: int):
        chat_history, error = get_by_attribute(self.db, ChatHistory, "id", chat_history_id)
        if error: 
            return None, error
        return chat_history
