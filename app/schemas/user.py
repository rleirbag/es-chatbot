from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    refresh_token: str
    avatar_url: str

    class Config:
        from_attributes = True
