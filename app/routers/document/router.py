from fastapi import APIRouter, File, UploadFile

from app.services.documents.create_document_use_case import (
    CreateDocumentUseCase,
)

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    return await CreateDocumentUseCase.execute(file)
