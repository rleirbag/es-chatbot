from pydantic import BaseModel


class DocumentResponse(BaseModel):
    g_file_id: str
    name: str
    shared_link: str

    class Config:
        from_attributes = True
