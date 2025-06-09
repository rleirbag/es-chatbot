import logging
from typing import Optional, Tuple

from app.config.database import delete, get_by_attribute
from app.models.question import Question
from app.schemas.error import Error
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class DeleteQuestionUseCase:
    @staticmethod
    def execute(
        db: Session,
        question_id: int,
        user_email: str
    ) -> Tuple[Optional[bool], Optional[Error]]:
        try:
            logger.info(f'Tentando deletar dúvida com ID: {question_id}')

            # Verificando se a questão existe
            existing_question, error = get_by_attribute(db, Question, 'id', question_id)

            if error:
                logger.info(f'Dúvida não encontrada: {question_id}')
                return None, error
            
            # Deleta a questão
            _, error = delete(db, Question, question_id)

            if error:
                logger.error(f'Erro ao deletar dúvida: {error}')
                return None, error
            
            logger.info(f'Dúvida deletada com sucesso: {question_id}')
            return True, None
        
        except Exception as e:
            logger.error(f'Erro inesperado ao deletar dúvida: {str(e)}')
            return None, Error(
                error_code=500,
                error_message=f'Erro inesperado: {str(e)}'
            )