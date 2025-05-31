from pydantic import BaseModel


class UserCreate(BaseModel):
    id: int
    name: str
    email: str
    refresh_token: str
    avatar_url: str

    class Config:
        from_attributes = True
