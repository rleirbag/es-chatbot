from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatStatisticsCreate(BaseModel):
    """Schema para criar uma nova estatística de chat"""
    user_id: Optional[int] = None
    user_email_hash: Optional[str] = None
    message_length: int = Field(..., ge=0)
    message_hash: Optional[str] = None
    detected_topic: Optional[str] = None
    is_question: bool = False
    message_type: str = Field(..., pattern="^(question|statement|command)$")
    response_time_ms: Optional[float] = None
    rag_context_found: bool = False
    llm_provider: Optional[str] = None
    hour_of_day: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)


class ChatStatisticsResponse(BaseModel):
    """Schema para resposta de estatísticas de chat"""
    id: int
    user_id: Optional[int]
    user_email_hash: Optional[str]
    message_length: int
    message_hash: Optional[str]
    detected_topic: Optional[str]
    is_question: bool
    message_type: str
    response_time_ms: Optional[float]
    rag_context_found: bool
    llm_provider: Optional[str]
    created_at: datetime
    hour_of_day: int
    day_of_week: int
    
    class Config:
        from_attributes = True


class ChatStatisticsSummary(BaseModel):
    """Schema para resumo de estatísticas"""
    total_messages: int
    total_questions: int
    total_statements: int
    total_commands: int
    average_message_length: float
    average_response_time_ms: Optional[float]
    unique_users: int
    messages_with_rag_context: int
    most_common_topics: List[Dict[str, Any]]


class ChatStatisticsByTime(BaseModel):
    """Schema para estatísticas por tempo"""
    hour_of_day: int
    day_of_week: int
    message_count: int
    question_count: int
    average_response_time: Optional[float]


class ChatStatisticsByTopic(BaseModel):
    """Schema para estatísticas por tópico"""
    topic: str
    message_count: int
    question_count: int
    average_message_length: float
    latest_message_date: Optional[datetime]


class ChatStatisticsByUser(BaseModel):
    """Schema para estatísticas por usuário (anonimizado)"""
    user_hash: str
    total_messages: int
    total_questions: int
    average_message_length: float
    first_message_date: datetime
    last_message_date: datetime


class ChatStatisticsFilters(BaseModel):
    """Schema para filtros de consulta"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    message_type: Optional[str] = None
    topic: Optional[str] = None
    has_rag_context: Optional[bool] = None
    min_message_length: Optional[int] = None
    max_message_length: Optional[int] = None


class ChatStatisticsDashboard(BaseModel):
    """Schema para dashboard completo de estatísticas"""
    summary: ChatStatisticsSummary
    by_hour: List[ChatStatisticsByTime]
    by_day: List[ChatStatisticsByTime]
    by_topic: List[ChatStatisticsByTopic]
    recent_activity: List[ChatStatisticsResponse] 