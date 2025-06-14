import logging
from typing import Optional, Tuple

from app.config.database import commit, create
from app.models.question import Question
from app.schemas.question import QuestionCreate
from sqlalchemy.orm import Session
from app.schemas.error import Error

logger = logging.getLogger(__name__)

class CreateQuestionUseCase:
    @staticmethod
    @commit
    def execute(
        db: Session, question: QuestionCreate
    ) -> Tuple[Optional[Question], Optional[Error]]:
        try:
            logger.info(
                f'Tentando criar uma dúvida para o usuário: {question.user_id}'
            )

            question_create = Question(
                theme=question.theme,
                question=question.question,
                user_id=question.user_id
            )
            
            logger.info(f'Dúvida criada: {question_create.__dict__}')

            created_question, error = create(db, question_create)
            logger.info(f'Resultado da criacao: question={created_question}')
            
            if error:
                logger.error(f'Erro ao criar dúvida: {error}')
                return None, error
            
            logger.info(f'Dúvida criada com sucesso: {created_question.__dict__}')
            return created_question, None

        except Exception as e:
            logger.error(f'Erro inesperado ao criar dúvida: {str(e)}')
            return None, Error(
                error_code=500, error_message=f'Erro inesperado: {str(e)}'
            )