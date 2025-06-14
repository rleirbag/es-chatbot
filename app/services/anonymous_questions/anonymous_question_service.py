import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.anonymous_question import AnonymousQuestion
from app.schemas.anonymous_question import (
    AnonymousQuestionCreate, 
    AnonymousQuestionStats
)
from app.services.anonymous_questions.topic_classification_agent import SoftwareEngineeringTopicAgent

logger = logging.getLogger(__name__)


class AnonymousQuestionService:
    def __init__(self, db: Session):
        self.db = db
        self.topic_agent = SoftwareEngineeringTopicAgent()

    def create_question(self, question_data: AnonymousQuestionCreate) -> AnonymousQuestion:
        """Salva uma nova dúvida anônima"""
        try:
            db_question = AnonymousQuestion(
                topic=question_data.topic.strip(),
                question=question_data.question.strip()
            )
            
            self.db.add(db_question)
            self.db.commit()
            self.db.refresh(db_question)
            
            logger.info(f"Dúvida anônima criada: ID={db_question.id}, Tema='{db_question.topic}'")
            return db_question
            
        except Exception as e:
            logger.error(f"Erro ao criar dúvida anônima: {e}")
            self.db.rollback()
            raise

    def get_questions(
        self, 
        topic: Optional[str] = None,
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[List[AnonymousQuestion], int]:
        """Lista dúvidas com paginação e filtro opcional por tema"""
        try:
            query = self.db.query(AnonymousQuestion)
            
            if topic:
                query = query.filter(AnonymousQuestion.topic.ilike(f"%{topic}%"))
            
            # Total de registros
            total = query.count()
            
            # Paginação
            offset = (page - 1) * per_page
            questions = query.order_by(desc(AnonymousQuestion.created_at)).offset(offset).limit(per_page).all()
            
            return questions, total
            
        except Exception as e:
            logger.error(f"Erro ao buscar dúvidas: {e}")
            raise

    def get_question_stats(self) -> List[AnonymousQuestionStats]:
        """Retorna estatísticas de dúvidas por tema, incluindo todos os tópicos possíveis"""
        try:
            # Busca estatísticas dos tópicos que já têm dúvidas registradas
            existing_stats = self.db.query(
                AnonymousQuestion.topic,
                func.count(AnonymousQuestion.id).label('question_count'),
                func.max(AnonymousQuestion.created_at).label('latest_question_date')
            ).group_by(AnonymousQuestion.topic).all()
            
            # Cria um dicionário com as estatísticas existentes
            stats_dict = {
                stat.topic: {
                    'question_count': stat.question_count,
                    'latest_question_date': stat.latest_question_date
                }
                for stat in existing_stats
            }
            
            # Obtém todos os tópicos possíveis do agente
            all_topics = self.topic_agent.get_all_topics()
            
            # Cria lista completa de estatísticas
            complete_stats = []
            for topic_info in all_topics:
                topic_name = topic_info['name']
                
                if topic_name in stats_dict:
                    # Tópico com dúvidas existentes
                    complete_stats.append(AnonymousQuestionStats(
                        topic=topic_name,
                        question_count=stats_dict[topic_name]['question_count'],
                        latest_question_date=stats_dict[topic_name]['latest_question_date']
                    ))
                else:
                    # Tópico sem dúvidas ainda
                    complete_stats.append(AnonymousQuestionStats(
                        topic=topic_name,
                        question_count=0,
                        latest_question_date=None
                    ))
            
            # Ordena por quantidade de dúvidas (decrescente) e depois por nome
            complete_stats.sort(key=lambda x: (-x.question_count, x.topic))
            
            return complete_stats
            
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            raise

    def get_most_common_topics(self, limit: int = 10) -> List[str]:
        """Retorna os temas mais comuns"""
        try:
            topics = self.db.query(
                AnonymousQuestion.topic,
                func.count(AnonymousQuestion.id).label('count')
            ).group_by(AnonymousQuestion.topic).order_by(func.count(AnonymousQuestion.id).desc()).limit(limit).all()
            
            return [topic.topic for topic in topics]
            
        except Exception as e:
            logger.error(f"Erro ao buscar temas comuns: {e}")
            raise

    def detect_and_save_question(self, message: str, context: str = "") -> Optional[AnonymousQuestion]:
        """
        Detecta se uma mensagem é uma dúvida e extrai o tema automaticamente usando o agente especializado
        Retorna a dúvida salva se detectada, None caso contrário
        """
        try:
            # Palavras-chave que indicam dúvidas (melhoradas)
            question_indicators = [
                "como", "o que", "por que", "porque", "quando", "onde", 
                "qual", "quais", "quem", "dúvida", "duvida", "pergunta",
                "não entendo", "nao entendo", "pode explicar", "me ajuda",
                "não sei", "nao sei", "como funciona", "o que é", "o que eh",
                "explique", "esclareça", "tenho dificuldade", "preciso de ajuda",
                "como fazer", "como usar", "como implementar", "o que significa"
            ]
            
            message_lower = message.lower()
            
            # Verifica se a mensagem contém indicadores de dúvida
            is_question = (
                message.endswith("?") or 
                any(indicator in message_lower for indicator in question_indicators) or
                # Padrões adicionais usando regex
                any(pattern in message_lower for pattern in ["como \\w+", "o que \\w+", "qual \\w+"])
            )
            
            if not is_question:
                return None
            
            # Usa o agente especializado para classificar o tema
            topic = self.topic_agent.classify_topic(message, context)
            
            # Salva a dúvida
            question_data = AnonymousQuestionCreate(
                topic=topic,
                question=message
            )
            
            return self.create_question(question_data)
            
        except Exception as e:
            logger.error(f"Erro ao detectar e salvar dúvida: {e}")
            return None

    def get_available_topics(self) -> List[dict]:
        """Retorna todos os tópicos disponíveis do agente especializado"""
        return self.topic_agent.get_all_topics()
    
    def get_topic_suggestions(self, partial_text: str, limit: int = 5) -> List[str]:
        """Retorna sugestões de tópicos baseado em texto parcial"""
        return self.topic_agent.get_topic_suggestions(partial_text, limit)
    
    def get_topic_details(self, topic_name: str) -> Optional[dict]:
        """Retorna detalhes de um tópico específico"""
        return self.topic_agent.get_topic_details(topic_name) 