from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, func, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class ChatStatistics(Base):
    __tablename__ = 'chat_statistics'

    id = Column(Integer, primary_key=True, index=True)
    
    # Informações do usuário (opcional para manter privacidade)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user_email_hash = Column(String(64), nullable=True)  # Hash do email para privacidade
    
    # Informações da mensagem
    message_length = Column(Integer, nullable=False)  # Tamanho da mensagem
    message_hash = Column(String(64), nullable=True)  # Hash da mensagem para privacidade
    
    # Classificação da mensagem
    detected_topic = Column(String(255), nullable=True)  # Tópico detectado pelo agente
    is_question = Column(Boolean, default=False, nullable=False)  # Se é uma pergunta
    message_type = Column(String(50), nullable=False)  # 'question', 'statement', 'command'
    
    # Métricas de performance
    response_time_ms = Column(Float, nullable=True)  # Tempo de resposta em millisegundos
    rag_context_found = Column(Boolean, default=False, nullable=False)  # Se encontrou contexto RAG
    llm_provider = Column(String(50), nullable=True)  # Qual LLM foi usado
    
    # Informações temporais (UTC-3 - Horário de Brasília)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=-3))), nullable=False)
    hour_of_day = Column(Integer, nullable=False)  # Hora do dia (0-23) em UTC-3
    day_of_week = Column(Integer, nullable=False)  # Dia da semana (0-6) em UTC-3
    
    # Relacionamento com usuário
    user = relationship('User', back_populates='chat_statistics')
    
    def __repr__(self):
        return f"<ChatStatistics(id={self.id}, type='{self.message_type}', topic='{self.detected_topic}', created_at='{self.created_at}')>" 