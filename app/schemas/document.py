from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    g_file_id: str
    name: str
    shared_link: str

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    id: int
    name: str
    shared_link: str
    g_file_id: str
    g_folder_id: str
    created_at: datetime
    user_id: int
    user_email: str

    class Config:
        from_attributes = True


class DocumentsPaginatedResponse(BaseModel):
    documents: List[DocumentListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


class SystemDeletionDetail(BaseModel):
    deleted: int
    errors: List[str]


class DeletionSummary(BaseModel):
    total_deleted: int
    total_errors: int
    success: bool
    systems_processed: int
    folder_used: str


class DeleteAllDocumentsResponse(BaseModel):
    database: SystemDeletionDetail
    chromadb: SystemDeletionDetail
    google_drive: SystemDeletionDetail
    summary: DeletionSummary

    class Config:
        from_attributes = True
