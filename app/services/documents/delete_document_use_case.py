import logging
from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import commit, delete, get_by_attribute
from app.models.document import Document
from app.schemas.error import Error
from app.services.rag.rag_service import RagService
from app.utils.google_drive import authenticate_google_drive

logger = logging.getLogger(__name__)


class DeleteDocumentUseCase:
    @staticmethod
    @commit
    def execute(db: Session, g_file_id: str) -> Tuple[None, Optional[Error]]:
        try:
            # Delete from Google Drive
            drive_service = authenticate_google_drive()
            drive_service.files().delete(fileId=g_file_id).execute()
            logger.info(f"File {g_file_id} deleted from Google Drive")
        except Exception as e:
            logger.error(f'Error deleting file from Google Drive: {e}')
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail='Erro ao deletar arquivo no Drive',
            )

        # Delete from ChromaDB
        try:
            rag_service = RagService()
            delete_result = rag_service.delete_by_g_file_id(g_file_id)
            logger.info(f"ChromaDB deletion result: {delete_result}")
        except Exception as e:
            logger.error(f'Error deleting file from ChromaDB: {e}')
            # Continue with database deletion even if ChromaDB fails

        # Delete from local database
        document, error = get_by_attribute(
            db, Document, 'g_file_id', g_file_id
        )
        if error:
            return None, error

        assert document
        _, error = delete(db, Document, document.id)
        if error:
            return None, error

        logger.info(f"Document {g_file_id} deleted successfully from all systems")
        return None, None
