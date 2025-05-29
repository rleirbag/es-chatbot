from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class QuestionBase(BaseModel):
    """
    Schema base para questões/duvidas. 

    Atributos:
        theme: Tema principal da dúvida
        question: Texto completo da dúvida
"""
    theme: str = Field(
        min_length=3,
        max_length=100,
        description= "Tema da Dúvida"
    )
    question: str = Field(
        min_length=10,
        description="Texto da Dúvida"
    )

    class Config:
        schema_extra = {
            "example": {
                "theme": "Python",
                "question": "Como funciona o Pydantic?"
            }
        }

class QuestionCreate(QuestionBase):
    user_id: int = Field(
        gt=0,
        description="ID do usuário que está fazendo a pergunta"
    )

    class Config: 
        schema_extra = {
            "example": {
                "theme": "Python",
                "question": "Para que serve o Base Model?",
                "user_id": 1
            }
        }

class QuestionResponse(QuestionBase):
    """
    Atributos:
        id: Identificador unico da duvida
        user_id: ID do usuário que criou a duvida
        created_at: Hora que foi criado
        updated_at: Hora que foi atualizado
        theme: Tema da dúvida(herdado de QuestionBase)
        question: Texto da dúvida (herdado de QuestionBase)
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = Field(
        default=None
    )

    class Config: 
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "theme": "Python",
                "question": "Como usar um dicionario em Python?",
                "created_at": "2024-03-20T10:00:00",
                "updated_at": "2024-03-20T10:00:00"
            }
        }

class QuestionList(BaseModel):
    """
    Atributos: 
        items: Lista de dúvidas
        total: Total de dúvidas
        page: Página atual
        page_size: Quantidade de itens por página
        total_pages: Total de páginas
"""
    items: list[QuestionResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_pages: int = Field(ge=0)
    order_by: str = Field(
        default="created_at",
        description="Campo para Ordenacao"
    )

    class Config: 
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "theme": "Python",
                        "question": "Python é uma linguagem orientada a objetos?",
                        "created_at": "2024-03-20T10:00:00",
                        "updated_at": "2024-03-20T10:00:00"
                    },
                    { 
                        "id": 2,
                        "user_id": 1,
                        "theme": "FastAPI",
                        "question": "Como implementar autenticação?",
                        "created_at": "2024-03-20T10:00:00",
                        "updated_at": "2024-03-20T10:00:00"
                    }
                ],
                "total": 2,
                "page": 1,
                "page_size": 10,
                "total_pages": 1
            }
        }

    