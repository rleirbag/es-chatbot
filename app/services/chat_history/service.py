from typing import List
from sqlalchemy.orm import Session

from app.models.chat_history import ChatHistory
from app.schemas.chat_history import ChatHistoryCreate, ChatHistoryUpdate


class ChatHistoryService:
    def __init__(self, db: Session):
        """Inicializa o serviço com uma sessão do banco de dados."""
        self.db = db

    def get_chat_history(self, chat_history_id: int) -> ChatHistory | None:
        """
        Busca um registro específico do histórico de chat.
        
        Args:
            chat_history_id: ID do registro a ser buscado
            
        Returns:
            ChatHistory se encontrado, None caso contrário
        """
        return self.db.query(ChatHistory).filter(ChatHistory.id == chat_history_id).first()

    def get_user_chat_history(self, user_id: str) -> List[ChatHistory]:
        """
        Busca todo o histórico de chat de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de registros do histórico
        """
        return self.db.query(ChatHistory).filter(ChatHistory.user_id == user_id).all()

    def create_chat_history(self, user_id: str, chat_history: ChatHistoryCreate) -> ChatHistory:
        """
        Cria um novo registro no histórico de chat.
        
        Args:
            user_id: ID do usuário
            chat_history: Dados do registro a ser criado
            
        Returns:
            Registro criado
        """
        db_chat_history = ChatHistory(
            **chat_history.model_dump(),
            user_id=user_id
        )
        self.db.add(db_chat_history)
        self.db.commit()
        self.db.refresh(db_chat_history)
        return db_chat_history

    def update_chat_history(
        self, chat_history_id: int, chat_history: ChatHistoryUpdate
    ) -> ChatHistory | None:
        """
        Atualiza um registro do histórico de chat.
        
        Args:
            chat_history_id: ID do registro a ser atualizado
            chat_history: Novos dados do registro
            
        Returns:
            Registro atualizado se encontrado, None caso contrário
        """
        db_chat_history = self.get_chat_history(chat_history_id)
        if not db_chat_history:
            return None

        for key, value in chat_history.model_dump().items():
            setattr(db_chat_history, key, value)

        self.db.commit()
        self.db.refresh(db_chat_history)
        return db_chat_history

    def delete_chat_history(self, chat_history_id: int) -> bool:
        """
        Remove um registro do histórico de chat.
        
        Args:
            chat_history_id: ID do registro a ser removido
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        db_chat_history = self.get_chat_history(chat_history_id)
        if not db_chat_history:
            return False

        self.db.delete(db_chat_history)
        self.db.commit()
        return True 