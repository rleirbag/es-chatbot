from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatHistoryBase(BaseModel):
    question: str
    answer: str


class ChatHistoryCreate(ChatHistoryBase):
    user_id: str


class ChatHistoryRead(ChatHistoryBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryUpdate(ChatHistoryBase):
    """Schema para atualização de ChatHistory."""
    pass


class ChatHistory(ChatHistoryBase):
    """Schema completo de ChatHistory com todos os campos."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        """Configuração do Pydantic."""
        from_attributes = True  # Permite converter objetos SQLAlchemy para Pydantic 