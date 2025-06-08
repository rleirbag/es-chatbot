from fastapi import APIRouter, Depends, HTTPException, status

from app.config.database import DbSession
from app.schemas.user import UserResponse
from app.models.user import User
from app.utils.security import get_current_user

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