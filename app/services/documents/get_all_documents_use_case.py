import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.document import Document
from app.models.user import User
from app.schemas.error import Error

logger = logging.getLogger(__name__)


class GetAllDocumentsUseCase:
    @staticmethod
    def execute(
        db: Session, 
        page: int = 1, 
        page_size: int = 100
    ) -> Tuple[Optional[List[dict]], Optional[Error]]:
        """
        Busca todos os documentos cadastrados no sistema com paginação.
        
        Args:
            db: Sessão do banco de dados
            page: Número da página (padrão: 1)
            page_size: Quantidade de itens por página (padrão: 100)
            
        Returns:
            Tuple contendo lista de documentos e erro (se houver)
        """
        try:
            logger.info(f"Buscando documentos - página {page}, tamanho {page_size}")
            
            # Calcula o offset baseado na página
            offset = (page - 1) * page_size
            
            # Query para buscar documentos com informações do usuário
            documents_query = (
                db.query(Document)
                .join(User)
                .options(joinedload(Document.user))
                .order_by(Document.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            
            documents = documents_query.all()
            
            # Converte os documentos para dicionário incluindo email do usuário
            documents_list = []
            for doc in documents:
                doc_dict = {
                    'id': doc.id,
                    'name': doc.name,
                    'shared_link': doc.shared_link,
                    'g_file_id': doc.g_file_id,
                    'g_folder_id': doc.g_folder_id,
                    'created_at': doc.created_at,
                    'user_id': doc.user_id,
                    'user_email': doc.user.email if doc.user else None
                }
                documents_list.append(doc_dict)
            
            logger.info(f"Encontrados {len(documents_list)} documentos")
            return documents_list, None
            
        except Exception as e:
            logger.error(f"Erro ao buscar documentos: {str(e)}", exc_info=True)
            return None, Error(
                error_code=500,
                error_message=f"Erro interno ao buscar documentos: {str(e)}"
            )
    
    @staticmethod
    def get_total_count(db: Session) -> Tuple[Optional[int], Optional[Error]]:
        """
        Busca o total de documentos cadastrados.
        
        Args:
            db: Sessão do banco de dados
            
        Returns:
            Tuple contendo total de documentos e erro (se houver)
        """
        try:
            total = db.query(Document).count()
            return total, None
        except Exception as e:
            logger.error(f"Erro ao contar documentos: {str(e)}", exc_info=True)
            return None, Error(
                error_code=500,
                error_message=f"Erro interno ao contar documentos: {str(e)}"
            ) 