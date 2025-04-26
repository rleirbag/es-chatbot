from fastapi import APIRouter, File, HTTPException, Security, UploadFile

from app.config.database import DbSession
from app.schemas.document import DocumentResponse
from app.services.documents.create_document_use_case import (
    CreateDocumentUseCase,
)
from app.services.documents.delete_document_use_case import (
    DeleteDocumentUseCase,
)
from app.utils.security import get_current_user

router = APIRouter(tags=['Document'])


@router.post(
    '/upload',
    response_model=DocumentResponse,
)
async def upload_document(
    db: DbSession,
    file: UploadFile = File(...),
    user_info: dict = Security(get_current_user),
):
    document, error = CreateDocumentUseCase.execute(
        db, user_info['email'], file
    )

    if error:
        raise HTTPException(
            detail=error.error_message,
            status_code=error.error_code,
        )

    return document


@router.delete('/delete')
async def delete_document(
    db: DbSession,
    g_file_id: str,
    user: dict = Security(get_current_user),
):
    _, error = DeleteDocumentUseCase.execute(db, g_file_id)

    if error:
        raise HTTPException(
            detail=error.error_message,
            status_code=error.error_code,
        )
