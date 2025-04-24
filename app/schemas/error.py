from pydantic import BaseModel


class Error(BaseModel):
    error_code: int
    error_message: str
