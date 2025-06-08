from sqlalchemy.orm import Session
from app.models.user import User


class GetUserByEmailUseCase:
    @staticmethod
    def execute(db: Session, email: str) -> User | None:
        """
        Busca um usuário pelo email.

        Args:
            db: Sessão do banco de dados
            email: Email do usuário a ser buscado

        Returns:
            Usuário se encontrado, None caso contrário
        """
        return db.query(User).filter(User.email == email).first() 