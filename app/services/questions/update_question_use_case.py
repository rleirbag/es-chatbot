import logging
from typing import Optional, Tuple

from app.config.database import update, get_by_id
from app.models.question import Question
from app.schemas.question import QuestionUpdate
from app.schemas.error import Error
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class UpdateQuestionUseCase:
    @staticmethod
    def execute(
        db: Session,
        question_id: str,
        question_update: QuestionUpdate
    ) -> Tuple[Optional[Question], Optional[Error]]:
        try:
            logger.info(f'Tentando atualizar a dúvida com ID: {question_id}')

            existing_question = get_by_id(db, Question, question_id)

            if not existing_question: 
                logger.info(f'Dúvida nao encontrada: {question_id}')
                return None, Error(
                    error_code=404,
                    error_message=f'Dúvida com ID {question_id} nao encontrada'
                )
            
            #atualizando os campos
            update_data = question_update.dict(exclude_unset = True)
            for field, value in update_data.items():
                setattr(existing_question, field, value)

            #salva as alteracoes
            updated_question, error = update(db, existing_question)

            if error:
                logger.error(f'Erro ao atualizar a dúvida: {error}')
                return None, error
            
            logger.info(f'Dúvida atualizada com sucesso: {updated_question.__dict__}')
            return updated_question, None
        
        except Exception as e:
            logger.error(f'Erro inesperado ao atualizar a dúvida: {str(e)}')
            return None, Error(
                error_code=500,
                error_message=f'Erro inesperado: {str(e)}'
            )