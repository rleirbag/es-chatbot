import logging
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.config.database import get_all, get_by_attribute
from app.models.question import Question
from app.models.user import User
from app.schemas.error import Error
from app.schemas.question import QuestionList

logger = logging.getLogger(__name__)

class ListQuestionsUseCase:
    @staticmethod
    def execute(
        db: Session,
        user_email: str,
        page: int,
        page_size: int,
        order_by: str = "created_at"
    ) -> Tuple[Optional[QuestionList], Optional[Error]]:
        try:
            logger.info(
                f'buscando dúvidas - página: {page}, itens por página: {page_size}'
            )

            # Busca o usuário pelo email
            user, error = get_by_attribute(db, User, 'email', user_email)
            if error:
                logger.error(f'Usuário não encontrado: {user_email}')
                return None, error

            # Busca as dúvidas no banco usando get_all
            questions, total = get_all(
                db,
                Question,
                page,
                page_size,
                [Question.user_id == user.id]  # Filtra apenas as dúvidas do usuário
            )

            logger.info(f'Total de dúvidas encontradas: {total}')

            # Calculando o total de páginas
            total_pages = (total + page_size - 1) // page_size

            question_list = QuestionList(
                items=questions,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                order_by=order_by
            )

            logger.info(
                f'Lista de dúvidas retornada com sucesso - '
                f'total: {total}, páginas: {total_pages}'
            )

            return question_list, None
        
        except Exception as e: 
            logger.error(f'Erro inesperado ao listar as dúvidas: {str(e)}')
            return None, Error(
                error_code=500,
                error_message=f'Erro inesperado: {str(e)}'
            )