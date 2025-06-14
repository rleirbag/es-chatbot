from pydantic import BaseModel

from app.models.user import UserRole


class UserCreate(BaseModel):
    id: int
    name: str
    email: str
    refresh_token: str
    avatar_url: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    avatar_url: str
    role: UserRole

    class Config:
        from_attributes = True
