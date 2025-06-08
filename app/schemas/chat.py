from pydantic import BaseModel


class ChatRequest(BaseModel):
    chat_history_id: int | None = None
    message: str 