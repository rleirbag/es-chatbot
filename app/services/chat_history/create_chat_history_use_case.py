import logging
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.config.database import commit, create
from app.models.chat_history import ChatHistory
from app.schemas.error import Error
from app.schemas.chat_history import ChatHistoryCreate

logger = logging.getLogger(__name__)


class CreateChatHistoryUseCase:
    @staticmethod
    @commit
    def execute(
        db: Session, chat_history_create: ChatHistoryCreate
    ) -> Tuple[Optional[ChatHistory], Optional[Error]] | None:
        try:
            logger.info(
                f'Tentando criar histórico de chat para o usuário: {chat_history_create.user_id}'
            )

            chat_history = ChatHistory(**chat_history_create.model_dump())
            logger.info(f'Histórico de chat criado: {chat_history.__dict__}')

            chat_history, error = create(db, chat_history)
            logger.info(f'Resultado da criação: chat_history={chat_history}, error={error}')

            if error:
                logger.error(f'Erro ao criar histórico de chat: {error}')
                return None, error

            logger.info(f'Histórico de chat criado com sucesso: {chat_history.__dict__}')
            return chat_history, None

        except Exception as e:
            logger.error(f'Erro inesperado ao criar histórico de chat: {str(e)}')
            return None, Error(
                error_code=500, error_message=f'Erro inesperado: {str(e)}'
            ) 