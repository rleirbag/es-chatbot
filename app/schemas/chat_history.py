from datetime import datetime
from pydantic import BaseModel


class ChatHistoryBase(BaseModel):
    """Schema base para ChatHistory com campos comuns."""
    message: str
    response: str


class ChatHistoryCreate(ChatHistoryBase):
    """Schema para criação de ChatHistory."""
    pass


class ChatHistoryUpdate(ChatHistoryBase):
    """Schema para atualização de ChatHistory."""
    pass


class ChatHistory(ChatHistoryBase):
    """Schema completo de ChatHistory com todos os campos."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        """Configuração do Pydantic."""
        from_attributes = True  # Permite converter objetos SQLAlchemy para Pydantic 