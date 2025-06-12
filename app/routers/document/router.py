from typing import List
from fastapi import APIRouter, File, HTTPException, Query, Security, UploadFile
import math

from app.config.database import DbSession
from app.schemas.document import (
    DocumentResponse, 
    DocumentListResponse, 
    DocumentsPaginatedResponse,
    DeleteAllDocumentsResponse
)
from app.services.documents.create_document_use_case import (
    CreateDocumentUseCase,
)
from app.services.documents.delete_document_use_case import (
    DeleteDocumentUseCase,
)
from app.services.documents.delete_all_documents_use_case import (
    DeleteAllDocumentsUseCase,
)
from app.services.documents.get_all_documents_use_case import (
    GetAllDocumentsUseCase,
)
from app.services.rag.rag_service import RagService
from app.utils.security import get_current_user

router = APIRouter(tags=['Document'])


@router.get(
    '/all',
    response_model=List[DocumentListResponse],
)
async def get_all_documents(
    db: DbSession,
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(100, ge=1, le=500, description="Quantidade de itens por página"),
    user_info: dict = Security(get_current_user),
):
    """
    Busca todos os documentos cadastrados no sistema com paginação.
    
    - **page**: Número da página (padrão: 1)
    - **page_size**: Quantidade de itens por página (padrão: 100, máximo: 500)
    
    Retorna uma lista de documentos ordenados por data de criação (mais recentes primeiro).
    """
    documents, error = GetAllDocumentsUseCase.execute(db, page, page_size)

    if error:
        raise HTTPException(
            detail=error.error_message,
            status_code=error.error_code,
        )

    return documents


@router.get(
    '',
    response_model=DocumentsPaginatedResponse,
)
async def get_documents_paginated(
    db: DbSession,
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(20, ge=1, le=100, description="Quantidade de itens por página"),
    user_info: dict = Security(get_current_user),
):
    """
    Busca documentos cadastrados no sistema com informações completas de paginação.
    
    - **page**: Número da página (padrão: 1)
    - **page_size**: Quantidade de itens por página (padrão: 20, máximo: 100)
    
    Retorna documentos com informações de paginação (total, páginas, etc.).
    """
    documents, error = GetAllDocumentsUseCase.execute(db, page, page_size)
    if error:
        raise HTTPException(
            detail=error.error_message,
            status_code=error.error_code,
        )

    total, total_error = GetAllDocumentsUseCase.get_total_count(db)
    if total_error:
        raise HTTPException(
            detail=total_error.error_message,
            status_code=total_error.error_code,
        )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return DocumentsPaginatedResponse(
        documents=documents,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


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


@router.delete(
    '/delete-all',
    response_model=DeleteAllDocumentsResponse,
)
async def delete_all_documents(
    db: DbSession,
    user_info: dict = Security(get_current_user),
):
    """
    DELETA TODOS OS DOCUMENTOS de forma INDEPENDENTE em cada sistema.
    
    ⚠️  **ATENÇÃO: Esta operação é IRREVERSÍVEL!**
    
    **Funcionamento independente:**
    
    🗂️  **Google Drive:** 
    - Deleta TODOS os arquivos dentro da pasta configurada (`GOOGLE_FOLDER_NAME`)
    - Não depende dos registros no banco de dados
    - Limpa arquivos que podem ter sido adicionados manualmente
    
    🧠 **ChromaDB:**
    - Remove TODOS os documentos/embeddings da collection
    - Não depende dos registros no banco de dados
    - Limpa vetores órfãos que podem ter ficado
    
    💾 **Banco de dados:**
    - Exclui TODOS os registros da tabela `documents`
    - Não depende da existência dos arquivos externos
    - Limpa registros órfãos
    
    **Vantagens:**
    - Funciona mesmo com dados inconsistentes entre sistemas
    - Limpa arquivos/dados órfãos
    - Cada sistema é processado independentemente
    - Continua funcionando mesmo se um sistema falhar
    
    Retorna um relatório detalhado com o resultado da deleção em cada sistema.
    """
    deletion_report, error = DeleteAllDocumentsUseCase.execute(db)

    if error:
        raise HTTPException(
            detail=error.error_message,
            status_code=error.error_code,
        )

    return deletion_report


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
