import logging
from typing import Optional, Tuple

from app.config.database import get_by_id
from app.models.question import Question
from app.schemas.error import Error
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class GetQuestonUseCase:
    @staticmethod
    def execute (
        db: Session, question_id: str
    ) -> Tuple[Optional[Question], Optional[Error]]:
        try: 
            logger.info(f'Tentando buscar dúvida com ID: {question_id}')

            question = get_by_id(db, Question, question_id)

            if not question:
                logger.info(f'Dúvida nao encontrada: {question_id}')
                return None, Error(
                    error_code = 404,
                    error_message=f'Dúvida com ID {question_id} nao encontrada'
                )
            
            logger.info(f'Dúvida encontrada: {question.__dict__}')
            return question, None
        
        except Exception as e:
            logger.error(f'Error inesperado ao buscar dúvida: {str(e)}')
            return None, Error(
                error_code=500,
                error_message=f'Erro inesperado: {str(e)}'
            )