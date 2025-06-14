from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class AnonymousQuestionCreate(BaseModel):
    topic: str = Field(..., min_length=1, max_length=255, description="Tema da dúvida")
    question: str = Field(..., min_length=1, description="Pergunta do usuário")


class AnonymousQuestionResponse(BaseModel):
    id: int
    topic: str
    question: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnonymousQuestionStats(BaseModel):
    """Schema para estatísticas das dúvidas por tema"""
    topic: str
    question_count: int
    latest_question_date: Optional[datetime] = None


class AnonymousQuestionsList(BaseModel):
    """Schema para listagem paginada de dúvidas"""
    questions: list[AnonymousQuestionResponse]
    total: int
    page: int
    per_page: int 