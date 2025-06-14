import logging
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, case

from app.models.chat_statistics import ChatStatistics
from app.schemas.chat_statistics import (
    ChatStatisticsCreate, 
    ChatStatisticsSummary,
    ChatStatisticsByTime,
    ChatStatisticsByTopic,
    ChatStatisticsByUser,
    ChatStatisticsFilters,
    ChatStatisticsDashboard
)
from app.services.anonymous_questions.topic_classification_agent import SoftwareEngineeringTopicAgent
from app.utils.timezone import now_brazil, get_brazil_hour_and_day

logger = logging.getLogger(__name__)


class ChatStatisticsService:
    def __init__(self, db: Session):
        self.db = db
        self.topic_agent = SoftwareEngineeringTopicAgent()

    def create_message_statistic(
        self, 
        message: str, 
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        response_time_ms: Optional[float] = None,
        rag_context_found: bool = False,
        llm_provider: Optional[str] = None
    ) -> ChatStatistics:
        """Cria uma nova estatística para uma mensagem enviada"""
        try:
            # Gera hashes para privacidade
            message_hash = hashlib.sha256(message.encode()).hexdigest()[:16]
            user_email_hash = None
            if user_email:
                user_email_hash = hashlib.sha256(user_email.encode()).hexdigest()[:16]
            
            # Classifica a mensagem
            detected_topic = self.topic_agent.classify_topic(message)
            is_question = self._is_question(message)
            message_type = self._classify_message_type(message)
            
            # Informações temporais (UTC-3 - Horário de Brasília)
            hour_of_day, day_of_week = get_brazil_hour_and_day()
            
            # Cria a estatística
            statistic = ChatStatistics(
                user_id=user_id,
                user_email_hash=user_email_hash,
                message_length=len(message),
                message_hash=message_hash,
                detected_topic=detected_topic,
                is_question=is_question,
                message_type=message_type,
                response_time_ms=response_time_ms,
                rag_context_found=rag_context_found,
                llm_provider=llm_provider,
                hour_of_day=hour_of_day,
                day_of_week=day_of_week
            )
            
            self.db.add(statistic)
            self.db.commit()
            self.db.refresh(statistic)
            
            logger.info(f"Estatística criada: tipo={message_type}, tópico={detected_topic}")
            return statistic
            
        except Exception as e:
            logger.error(f"Erro ao criar estatística: {e}")
            self.db.rollback()
            raise

    def get_summary_statistics(self, filters: Optional[ChatStatisticsFilters] = None) -> ChatStatisticsSummary:
        """Retorna resumo geral das estatísticas"""
        try:
            query = self.db.query(ChatStatistics)
            
            # Aplica filtros se fornecidos
            if filters:
                query = self._apply_filters(query, filters)
            
            # Contadores básicos
            total_messages = query.count()
            total_questions = query.filter(ChatStatistics.is_question == True).count()
            total_statements = query.filter(ChatStatistics.message_type == 'statement').count()
            total_commands = query.filter(ChatStatistics.message_type == 'command').count()
            
            # Médias
            avg_length = query.with_entities(func.avg(ChatStatistics.message_length)).scalar() or 0.0
            avg_response_time = query.filter(ChatStatistics.response_time_ms != None).with_entities(
                func.avg(ChatStatistics.response_time_ms)
            ).scalar()
            
            # Usuários únicos
            unique_users = query.filter(ChatStatistics.user_id != None).with_entities(
                func.count(func.distinct(ChatStatistics.user_id))
            ).scalar() or 0
            
            # Mensagens com contexto RAG
            messages_with_rag = query.filter(ChatStatistics.rag_context_found == True).count()
            
            # Tópicos mais comuns
            common_topics = query.filter(ChatStatistics.detected_topic != None).with_entities(
                ChatStatistics.detected_topic,
                func.count(ChatStatistics.id).label('count')
            ).group_by(ChatStatistics.detected_topic).order_by(desc('count')).limit(10).all()
            
            most_common_topics = [
                {"topic": topic, "count": count} for topic, count in common_topics
            ]
            
            return ChatStatisticsSummary(
                total_messages=total_messages,
                total_questions=total_questions,
                total_statements=total_statements,
                total_commands=total_commands,
                average_message_length=round(avg_length, 2),
                average_response_time_ms=round(avg_response_time, 2) if avg_response_time else None,
                unique_users=unique_users,
                messages_with_rag_context=messages_with_rag,
                most_common_topics=most_common_topics
            )
            
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas resumo: {e}")
            raise

    def get_statistics_by_time(self, filters: Optional[ChatStatisticsFilters] = None) -> Dict[str, List[ChatStatisticsByTime]]:
        """Retorna estatísticas agrupadas por tempo"""
        try:
            query = self.db.query(ChatStatistics)
            
            if filters:
                query = self._apply_filters(query, filters)
            
            # Por hora do dia
            by_hour = query.with_entities(
                ChatStatistics.hour_of_day,
                func.count(ChatStatistics.id).label('message_count'),
                func.sum(case((ChatStatistics.is_question == True, 1), else_=0)).label('question_count'),
                func.avg(ChatStatistics.response_time_ms).label('avg_response_time')
            ).group_by(ChatStatistics.hour_of_day).order_by(ChatStatistics.hour_of_day).all()
            
            # Por dia da semana
            by_day = query.with_entities(
                ChatStatistics.day_of_week,
                func.count(ChatStatistics.id).label('message_count'),
                func.sum(case((ChatStatistics.is_question == True, 1), else_=0)).label('question_count'),
                func.avg(ChatStatistics.response_time_ms).label('avg_response_time')
            ).group_by(ChatStatistics.day_of_week).order_by(ChatStatistics.day_of_week).all()
            
            return {
                "by_hour": [
                    ChatStatisticsByTime(
                        hour_of_day=hour,
                        day_of_week=0,  # Não aplicável
                        message_count=count,
                        question_count=q_count or 0,
                        average_response_time=avg_time
                    )
                    for hour, count, q_count, avg_time in by_hour
                ],
                "by_day": [
                    ChatStatisticsByTime(
                        hour_of_day=0,  # Não aplicável
                        day_of_week=day,
                        message_count=count,
                        question_count=q_count or 0,
                        average_response_time=avg_time
                    )
                    for day, count, q_count, avg_time in by_day
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas por tempo: {e}")
            raise

    def get_statistics_by_topic(self, filters: Optional[ChatStatisticsFilters] = None) -> List[ChatStatisticsByTopic]:
        """Retorna estatísticas agrupadas por tópico"""
        try:
            query = self.db.query(ChatStatistics).filter(ChatStatistics.detected_topic != None)
            
            if filters:
                query = self._apply_filters(query, filters)
            
            stats = query.with_entities(
                ChatStatistics.detected_topic,
                func.count(ChatStatistics.id).label('message_count'),
                func.sum(case((ChatStatistics.is_question == True, 1), else_=0)).label('question_count'),
                func.avg(ChatStatistics.message_length).label('avg_length'),
                func.max(ChatStatistics.created_at).label('latest_date')
            ).group_by(ChatStatistics.detected_topic).order_by(desc('message_count')).all()
            
            return [
                ChatStatisticsByTopic(
                    topic=topic,
                    message_count=count,
                    question_count=q_count or 0,
                    average_message_length=round(avg_length, 2),
                    latest_message_date=latest_date
                )
                for topic, count, q_count, avg_length, latest_date in stats
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas por tópico: {e}")
            raise

    def get_dashboard_data(self, filters: Optional[ChatStatisticsFilters] = None) -> ChatStatisticsDashboard:
        """Retorna dados completos para dashboard"""
        try:
            summary = self.get_summary_statistics(filters)
            time_stats = self.get_statistics_by_time(filters)
            topic_stats = self.get_statistics_by_topic(filters)
            
            # Atividade recente
            recent_query = self.db.query(ChatStatistics)
            if filters:
                recent_query = self._apply_filters(recent_query, filters)
            
            recent_activity = recent_query.order_by(desc(ChatStatistics.created_at)).limit(20).all()
            
            return ChatStatisticsDashboard(
                summary=summary,
                by_hour=time_stats["by_hour"],
                by_day=time_stats["by_day"],
                by_topic=topic_stats,
                recent_activity=recent_activity
            )
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do dashboard: {e}")
            raise

    def _is_question(self, message: str) -> bool:
        """Detecta se a mensagem é uma pergunta"""
        question_indicators = [
            "como", "o que", "por que", "porque", "quando", "onde", 
            "qual", "quais", "quem", "dúvida", "duvida", "pergunta",
            "não entendo", "nao entendo", "pode explicar", "me ajuda",
            "não sei", "nao sei", "como funciona", "o que é", "o que eh",
            "explique", "esclareça", "tenho dificuldade", "preciso de ajuda"
        ]
        
        return (
            message.endswith("?") or 
            any(indicator in message.lower() for indicator in question_indicators)
        )

    def _classify_message_type(self, message: str) -> str:
        """Classifica o tipo da mensagem"""
        if message.startswith('/'):
            return 'command'
        elif self._is_question(message):
            return 'question'
        else:
            return 'statement'

    def _apply_filters(self, query, filters: ChatStatisticsFilters):
        """Aplica filtros à query"""
        if filters.start_date:
            query = query.filter(ChatStatistics.created_at >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(ChatStatistics.created_at <= filters.end_date)
        
        if filters.message_type:
            query = query.filter(ChatStatistics.message_type == filters.message_type)
        
        if filters.topic:
            query = query.filter(ChatStatistics.detected_topic == filters.topic)
        
        if filters.has_rag_context is not None:
            query = query.filter(ChatStatistics.rag_context_found == filters.has_rag_context)
        
        if filters.min_message_length:
            query = query.filter(ChatStatistics.message_length >= filters.min_message_length)
        
        if filters.max_message_length:
            query = query.filter(ChatStatistics.message_length <= filters.max_message_length)
        
        return query 