from sqlalchemy.orm import Session

from app.config.database import commit, get_by_attribute
from app.models.user import User


class GetUserUseCase:
    @staticmethod
    @commit
    def by_email(db: Session, email: str):
        user, error = get_by_attribute(db, User, 'email', email)

        if error:
            return None, error

        return user, None
