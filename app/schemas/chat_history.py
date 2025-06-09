from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatHistoryBase(BaseModel):
    chat_messages: Dict[str, Any] = Field(
        ...,
        example={
            "messages": [
                {"role": "user", "content": "Oi ola"},
                {"role": "assistant", "content": "opa"}
            ]
        }
    )


class ChatHistoryCreate(ChatHistoryBase):
    user_id: Optional[int] = None
    pass


class ChatHistoryRead(ChatHistoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryUpdate(BaseModel):
    """Schema para atualização de ChatHistory."""

    chat_messages: Dict[str, Any] = Field(
        ...,
        example={
            "messages": [
                {"role": "user", "content": "Oi ola"},
                {"role": "assistant", "content": "opa"},
            ]
        },
    )


class ChatHistory(ChatHistoryBase):
    """Schema completo de ChatHistory com todos os campos."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        """Configuração do Pydantic."""

        from_attributes = True  # Permite converter objetos SQLAlchemy para Pydantic 