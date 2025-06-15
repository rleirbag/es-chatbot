from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.error import Error


class UpdateUserRoleUseCase:
    @staticmethod
    def execute(db: Session, user_id: int, new_role: UserRole) -> tuple[User | None, Error | None]:
        """
        Atualiza o role de um usuário.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário a ser atualizado
            new_role: Novo role a ser atribuído
            
        Returns:
            Tuple contendo o usuário atualizado ou erro
        """
        try:
            # Busca o usuário pelo ID
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return None, Error(
                    error_code=404,
                    error_message="Usuário não encontrado"
                )
            
            # Atualiza o role do usuário
            user.role = new_role
            db.commit()
            db.refresh(user)
            
            return user, None
            
        except Exception as e:
            db.rollback()
            return None, Error(
                error_code=500,
                error_message=f"Erro interno do servidor: {str(e)}"
            ) 