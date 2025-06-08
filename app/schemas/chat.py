from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: str
    chat_history_id: int | None = None
    message: str 