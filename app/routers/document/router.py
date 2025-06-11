from fastapi import APIRouter, File, HTTPException, Security, UploadFile

from app.config.database import DbSession
from app.schemas.document import DocumentResponse
from app.services.documents.create_document_use_case import (
    CreateDocumentUseCase,
)
from app.services.documents.delete_document_use_case import (
    DeleteDocumentUseCase,
)
from app.services.rag.rag_service import RagService
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


@router.get('/list-chromadb')
async def list_chromadb_documents(
    limit: int = 100,
    user: dict = Security(get_current_user),
):
    """List all documents stored in ChromaDB."""
    try:
        rag_service = RagService()
        documents = rag_service.list_documents(limit=limit)
        collection_info = rag_service.get_collection_info()
        
        return {
            "collection_info": collection_info,
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.get('/chromadb-info')
async def get_chromadb_info(
    user: dict = Security(get_current_user),
):
    """Get ChromaDB collection information."""
    try:
        rag_service = RagService()
        info = rag_service.get_collection_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting collection info: {str(e)}")


@router.delete('/chromadb/delete-by-file-id')
async def delete_chromadb_by_file_id(
    g_file_id: str,
    user: dict = Security(get_current_user),
):
    """Delete document from ChromaDB by Google Drive file ID."""
    try:
        rag_service = RagService()
        result = rag_service.delete_by_g_file_id(g_file_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting from ChromaDB: {str(e)}")


@router.delete('/chromadb/delete-all')
async def delete_all_chromadb_documents(
    user: dict = Security(get_current_user),
):
    """Delete ALL documents from ChromaDB collection."""
    try:
        rag_service = RagService()
        result = rag_service.delete_all_documents()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting all documents: {str(e)}")
