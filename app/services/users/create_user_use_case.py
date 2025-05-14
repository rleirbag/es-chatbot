import logging
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.config.database import commit, create, get_by_attribute, update
from app.models.user import User
from app.schemas.error import Error
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


class CreateUserUseCase:
    @staticmethod
    @commit
    def execute(
        db: Session, user_create: UserCreate
    ) -> Tuple[Optional[User], Optional[Error]] | None:
        try:
            logger.info(
                f'Tentando criar usuário com email: {user_create.email}'
            )

            user = User(**user_create.model_dump())
            logger.info(f'Usuário criado: {user.__dict__}')

            existent_user, _ = get_by_attribute(db, User, 'email', user.email)
            if existent_user:
                logger.info(f'Usuário já existe com email: {user.email}')

                if existent_user.refresh_token != user.refresh_token:
                    user_updated, error = update(
                        db,
                        User,
                        existent_user.id,
                        **user_create.model_dump(),
                    )

                    if error:
                        logger.error(f'Erro ao atualizar usuário: {error}')
                        return None, error

                    return user_updated, None

                return existent_user, None

            user, error = create(db, user)
            logger.info(f'Resultado da criação: user={user}, error={error}')

            if error:
                logger.error(f'Erro ao criar usuário: {error}')
                return None, error

            logger.info(f'Usuário criado com sucesso: {user.__dict__}')
            return user, None

        except Exception as e:
            logger.error(f'Erro inesperado ao criar usuário: {str(e)}')
            return None, Error(
                error_code=500, error_message=f'Erro inesperado: {str(e)}'
            )
