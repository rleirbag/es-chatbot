from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.config.database import Base


class ChatHistory(Base):
    __tablename__ = 'chat_histories'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamento com o usuário
    user = relationship('User', back_populates='chat_histories') 