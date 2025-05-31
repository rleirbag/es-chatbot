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
                    user_data = user_create.model_dump()
                    user_data.pop('id', None)

                    logger.info(f'Dados para atualização: {user_data}')

                    user_updated, error = update(
                        db,
                        User,
                        existent_user.id,
                        **user_data,
                    )

                    if error:
                        logger.error(f'Erro ao atualizar usuário: {error}')
                        return None, error

                    if not user_updated:
                        logger.error('Usuário não foi atualizado')
                        return None, Error(
                            error_code=500,
                            error_message='Erro ao atualizar usuário',
                        )

                    logger.info(
                        f'Usuário atualizado com sucesso: {user_updated.__dict__}'
                    )
                    return user_updated, None

                return existent_user, None

            user, error = create(db, user)
            logger.info(f'Resultado da criação: user={user}, error={error}')

            if error:
                logger.error(f'Erro ao criar usuário: {error}')
                return None, error

            if not user:
                logger.error('Usuário não foi criado')
                return None, Error(
                    error_code=500, error_message='Erro ao criar usuário'
                )

            logger.info(f'Usuário criado com sucesso: {user.__dict__}')
            return user, None

        except Exception as e:
            logger.error(f'Erro inesperado ao criar usuário: {str(e)}')
            return None, Error(
                error_code=500, error_message=f'Erro inesperado: {str(e)}'
            )
