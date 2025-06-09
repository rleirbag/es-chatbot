import logging
from typing import Optional, Tuple

from app.config.database import get_by_attribute
from app.models.question import Question
from app.schemas.error import Error
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class GetQuestionUseCase:
    @staticmethod
    def execute(
        db: Session, question_id: int, user_email: str
    ) -> Tuple[Optional[Question], Optional[Error]]:
        try: 
            logger.info(f'Tentando buscar dúvida com ID: {question_id}')

            question, error = get_by_attribute(db, Question, 'id', question_id)

            if error:
                logger.info(f'Dúvida não encontrada: {question_id}')
                return None, error
            
            logger.info(f'Dúvida encontrada: {question.__dict__}')
            return question, None
        
        except Exception as e:
            logger.error(f'Error inesperado ao buscar dúvida: {str(e)}')
            return None, Error(
                error_code=500,
                error_message=f'Erro inesperado: {str(e)}'
            )