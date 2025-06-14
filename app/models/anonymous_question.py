from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.config.database import Base


class AnonymousQuestion(Base):
    __tablename__ = 'anonymous_questions'

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False, index=True)  # Tema da dúvida
    question = Column(Text, nullable=False)  # Pergunta do usuário
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AnonymousQuestion(id={self.id}, topic='{self.topic}', created_at='{self.created_at}')>" 