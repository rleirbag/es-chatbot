import logging
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import commit
from app.config.settings import Settings
from app.models.document import Document
from app.schemas.error import Error
from app.services.rag.rag_service import RagService
from app.utils.google_drive import authenticate_google_drive

logger = logging.getLogger(__name__)


class DeleteAllDocumentsUseCase:
    @staticmethod
    @commit
    def execute(db: Session) -> Tuple[Optional[Dict], Optional[Error]]:
        """
        Deleta todos os documentos do sistema de forma independente:
        - Google Drive: todos os arquivos da pasta configurada
        - ChromaDB: todos os documentos da collection
        - Banco de dados: todos os registros de documentos
        
        Args:
            db: Sessão do banco de dados
            
        Returns:
            Tuple contendo relatório de deleção e erro (se houver)
        """
        logger.warning("INICIANDO DELEÇÃO COMPLETA INDEPENDENTE DE TODOS OS DOCUMENTOS")
        
        deletion_report = {
            "database": {"deleted": 0, "errors": []},
            "chromadb": {"deleted": 0, "errors": []},
            "google_drive": {"deleted": 0, "errors": []}
        }
        
        try:
            # 1. DELETAR TODOS OS ARQUIVOS DO GOOGLE DRIVE (pela pasta configurada)
            logger.info("=== INICIANDO DELEÇÃO NO GOOGLE DRIVE ===")
            try:
                drive_service = authenticate_google_drive()
                logger.info("Serviço Google Drive autenticado com sucesso")
                
                # Buscar a pasta configurada
                folder_name = Settings().GOOGLE_FOLDER_NAME
                logger.info(f"Buscando pasta: {folder_name}")
                
                # Query para encontrar a pasta
                folder_query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                folder_results = drive_service.files().list(
                    q=folder_query, 
                    spaces='drive', 
                    fields='files(id, name)'
                ).execute()
                
                folders = folder_results.get('files', [])
                
                if folders:
                    folder_id = folders[0]['id']
                    logger.info(f"Pasta encontrada: {folder_name} (ID: {folder_id})")
                    
                    # Buscar todos os arquivos dentro da pasta
                    files_query = f"'{folder_id}' in parents and trashed=false"
                    files_results = drive_service.files().list(
                        q=files_query,
                        spaces='drive',
                        fields='files(id, name)',
                        pageSize=1000  # Máximo permitido pela API
                    ).execute()
                    
                    files = files_results.get('files', [])
                    logger.info(f"Encontrados {len(files)} arquivos na pasta {folder_name}")
                    
                    # Deletar cada arquivo
                    for file in files:
                        try:
                            drive_service.files().delete(fileId=file['id']).execute()
                            deletion_report["google_drive"]["deleted"] += 1
                            logger.info(f"Arquivo deletado: {file['name']} (ID: {file['id']})")
                        except Exception as e:
                            error_msg = f"Erro ao deletar arquivo {file['name']} ({file['id']}): {str(e)}"
                            logger.error(error_msg)
                            deletion_report["google_drive"]["errors"].append(error_msg)
                    
                    logger.info(f"Google Drive: {deletion_report['google_drive']['deleted']} arquivos deletados")
                else:
                    logger.warning(f"Pasta '{folder_name}' não encontrada no Google Drive")
                    deletion_report["google_drive"]["errors"].append(f"Pasta '{folder_name}' não encontrada")
                    
            except Exception as e:
                error_msg = f"Erro geral no Google Drive: {str(e)}"
                logger.error(error_msg)
                deletion_report["google_drive"]["errors"].append(error_msg)

            # 2. DELETAR TODOS OS DOCUMENTOS DO CHROMADB
            logger.info("=== INICIANDO DELEÇÃO NO CHROMADB ===")
            try:
                rag_service = RagService()
                logger.info("RagService inicializado com sucesso")
                
                # Obter informações antes da deleção
                collection_info = rag_service.get_collection_info()
                documents_before = collection_info.get('document_count', 0)
                logger.info(f"ChromaDB contém {documents_before} documentos antes da deleção")
                
                # Deletar todos os documentos
                result = rag_service.delete_all_documents()
                
                if "error" in result:
                    deletion_report["chromadb"]["errors"].append(result["error"])
                else:
                    deletion_report["chromadb"]["deleted"] = result.get("deleted_count", documents_before)
                    logger.info(f"ChromaDB: {deletion_report['chromadb']['deleted']} documentos deletados")
                    
            except Exception as e:
                error_msg = f"Erro geral no ChromaDB: {str(e)}"
                logger.error(error_msg)
                deletion_report["chromadb"]["errors"].append(error_msg)

            # 3. DELETAR TODOS OS REGISTROS DO BANCO DE DADOS
            logger.info("=== INICIANDO DELEÇÃO NO BANCO DE DADOS ===")
            try:
                # Contar documentos antes da deleção
                documents_count = db.query(Document).count()
                logger.info(f"Banco de dados contém {documents_count} registros antes da deleção")
                
                # Deletar todos os registros
                deleted_count = db.query(Document).delete()
                db.flush()  # O commit será feito pelo decorator @commit
                
                deletion_report["database"]["deleted"] = deleted_count
                logger.info(f"Banco de dados: {deleted_count} registros deletados")
                
            except Exception as e:
                error_msg = f"Erro ao deletar registros do banco: {str(e)}"
                logger.error(error_msg)
                deletion_report["database"]["errors"].append(error_msg)
                return None, Error(
                    error_code=500,
                    error_message=error_msg
                )

            # 4. GERAR RELATÓRIO FINAL
            total_deleted = (
                deletion_report["database"]["deleted"] + 
                deletion_report["chromadb"]["deleted"] + 
                deletion_report["google_drive"]["deleted"]
            )
            
            total_errors = (
                len(deletion_report["database"]["errors"]) + 
                len(deletion_report["chromadb"]["errors"]) + 
                len(deletion_report["google_drive"]["errors"])
            )
            
            deletion_report["summary"] = {
                "total_deleted": total_deleted,
                "total_errors": total_errors,
                "success": total_errors == 0,
                "systems_processed": 3,
                "folder_used": Settings().GOOGLE_FOLDER_NAME
            }
            
            logger.warning(f"DELEÇÃO INDEPENDENTE FINALIZADA - Total deletado: {total_deleted}, Erros: {total_errors}")
            
            return deletion_report, None
            
        except Exception as e:
            logger.error(f"Erro crítico durante deleção independente: {str(e)}", exc_info=True)
            return None, Error(
                error_code=500,
                error_message=f"Erro crítico durante deleção: {str(e)}"
            ) 