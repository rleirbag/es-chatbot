from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config.database import DbSession
from app.services.documents.create_document_use_case import (
    CreateDocumentUseCase,
)
from app.services.documents.delete_document_use_case import (
    DeleteDocumentUseCase,
)

router = APIRouter()


@router.post('/upload')
async def upload_document(db: DbSession, file: UploadFile = File(...)):
    document, error = CreateDocumentUseCase.execute(db, file)

    if error:
        raise HTTPException(
            detail=error.error_message,
            status_code=error.error_code,
        )

    return document


@router.delete('/delete')
async def delete_document(db: DbSession, g_file_id: str):
    _, error = DeleteDocumentUseCase.execute(db, g_file_id)

    if error:
        raise HTTPException(
            detail=error.error_message,
            status_code=error.error_code,
        )
