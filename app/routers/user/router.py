from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.config.database import DbSession
from app.schemas.user import UserResponse, UserRoleUpdate
from app.models.user import User, UserRole
from app.utils.security import get_current_user, get_current_admin_user
from app.services.users.update_user_role_use_case import UpdateUserRoleUseCase

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def read_users_me(
    db: DbSession,
    user_data: dict = Depends(get_current_user),
):
    """
    Get current user.
    """
    user = db.query(User).filter(User.email == user_data['email']).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("/admin/all", response_model=List[UserResponse])
def list_all_users(
    db: DbSession,
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Lista todos os usuários do sistema.
    Apenas administradores podem usar esta rota.
    """
    users = db.query(User).all()
    return users


@router.patch("/admin/grant", response_model=UserResponse)
def grant_admin_role(
    user_role_update: UserRoleUpdate,
    db: DbSession,
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Concede direitos de administrador a um usuário.
    Apenas administradores podem usar esta rota.
    """
    user, error = UpdateUserRoleUseCase.execute(
        db, 
        user_role_update.user_id, 
        user_role_update.role
    )
    
    if error:
        raise HTTPException(
            status_code=error.error_code,
            detail=error.error_message
        )
    
    return user


@router.patch("/admin/revoke/{user_id}", response_model=UserResponse)
def revoke_admin_role(
    user_id: int,
    db: DbSession,
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Remove direitos de administrador de um usuário.
    Apenas administradores podem usar esta rota.
    """
    user, error = UpdateUserRoleUseCase.execute(
        db, 
        user_id, 
        UserRole.USER
    )
    
    if error:
        raise HTTPException(
            status_code=error.error_code,
            detail=error.error_message
        )
    
    return user 