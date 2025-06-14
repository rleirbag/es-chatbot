from fastapi import APIRouter, Depends, HTTPException, Security, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db, get_by_attribute
from app.models.user import User
from app.schemas.question import QuestionResponse, QuestionCreate, QuestionList
from app.services.questions.create_question_use_case import CreateQuestionUseCase
from app.services.questions.get_question_use_case import GetQuestionUseCase
from app.services.questions.list_questions_use_case import ListQuestionsUseCase
from app.services.questions.update_question_use_case import UpdateQuestionUseCase
from app.services.questions.delete_question_use_case import DeleteQuestionUseCase
from app.utils.security import get_current_user

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("/", response_model=QuestionList)
def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    order_by: str = "created_at",
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user)
):
    """
    Retorna a lista de dúvidas do usuário autenticado.
    """
    use_case = ListQuestionsUseCase()
    questions, error = use_case.execute(db, user_info['email'], page, page_size, order_by)
    
    if error:
        raise HTTPException(
            status_code=error.error_code,
            detail=error.error_message
        )
    
    return questions


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna uma dúvida específica.
    """
    use_case = GetQuestionUseCase()
    question, error = use_case.execute(db, question_id, user_info['email'])
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.error_message
        )
    return question


@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question: QuestionCreate,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova dúvida.
    """
    user, error = get_by_attribute(db, User, 'email', user_info['email'])
    if error or not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualiza o user_id na question
    question.user_id = user.id
    
    use_case = CreateQuestionUseCase()
    question_created, error = use_case.execute(db, question)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )
    
    return question_created


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question: QuestionCreate,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma dúvida existente.
    """
    update_use_case = UpdateQuestionUseCase()
    updated_question, error = update_use_case.execute(db, question_id, question, user_info['email'])
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.error_message
        )
    return updated_question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    user_info: dict = Security(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove uma dúvida.
    """
    delete_use_case = DeleteQuestionUseCase()
    _, error = delete_use_case.execute(db, question_id, user_info['email'])
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.error_message
        ) 