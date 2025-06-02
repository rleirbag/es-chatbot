import logging
from typing import Optional, Tuple

from app.config.database import delete, get_by_id
from app.models.question import Question
from app.schemas.error import Error
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class DeleteQuestionUseCase:
    @staticmethod
    def execute(
        db: Session,
        question_id: str
    ) -> Tuple[Optional[bool], Optional[Error]]:
        try:
            logger.info(f'Tentando deletar dúvida com ID: {question_id}')

            #verificando se a questao existe
            existing_question = get_by_id(db, Question, question_id)

            if not existing_question:
                logger.info(f'Dúvida nao encontrada: {question_id}')
                return None, Error(
                    error_code=404,
                    error_message=f'Dúvida com ID {question_id} nao encontrada'
                )
            
            #deleta a questao
            success, error = delete(db, existing_question)

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