import logging
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.config.database import get_all
from app.models.question import Question
from app.schemas.error import Error
from app.schemas.question import QuestionList

logger = logging.getLogger(__name__)

class ListQuestionsUseCase:
    @staticmethod
    def execute (
        db: Session,
        page: int,
        page_size: int,
        order_by: str = "created_at"
    ) -> Tuple[Optional[QuestionList], Optional[Error]]:
        try:
            logger.info(
                f'buscando dúvias - página: {page}, itens por página: {page_size}'
            )

            #busca as dúvidas no banco usando get_all
            questions, total = get_all(
                db,
                Question,
                page,
                page_size,
                []
            )

            logger.info(f'Total de dúvidas encontradas: {total}')

            #calculando o total de paginas
            total_pages = (total + page_size - 1)

            question_list = QuestionList(
                items = questions,
                total = total,
                page = page,
                page_size = page_size,
                total_pages = total_pages,
                order_by=order_by
            )

            logger.info (
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