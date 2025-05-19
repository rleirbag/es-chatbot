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
    user_id: int

    class Config:
        schema_extra = {
            "example": {
                "chat_messages": {
                    "messages": [
                        {"role": "user", "content": "Oi ola"},
                        {"role": "assistant", "content": "opa"}
                    ]
                }
            }
        }


class ChatHistoryRead(ChatHistoryBase):
    id: int
    user_id: int
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