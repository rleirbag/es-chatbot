from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import UserRole
from app.schemas.chat_statistics import ChatStatisticsFilters
from app.services.chat_statistics.chat_statistics_service import ChatStatisticsService
from app.services.users.get_user_by_email_use_case import GetUserByEmailUseCase
from app.utils.security import get_current_user
from app.utils.timezone import get_day_name_pt, get_hour_period_pt, now_brazil

router = APIRouter(tags=["Statistics"])


def _verify_admin_access(current_user: dict, db: Session):
    """Verifica se o usuário é administrador"""
    user_email = current_user.get('email')
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials'
        )
    
    user = GetUserByEmailUseCase.execute(db, email=user_email)
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Apenas administradores podem acessar as estatísticas'
        )
    return user


@router.get(
    "/stats",
    response_model=dict,
    summary="Estatísticas do Chatbot",
    description="Retorna estatísticas essenciais do chatbot (apenas para admins)"
)
async def get_stats(
    days: int = Query(30, ge=1, le=365, description="Últimos X dias"),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user)
):
    """
    Retorna estatísticas essenciais do chatbot dos últimos X dias.
    
    Inclui:
    - Total de mensagens, perguntas e usuários
    - Tempo médio de resposta
    - Tópicos mais populares
    - Horário de maior uso
    - Dia da semana mais ativo
    """
    _verify_admin_access(current_user, db)
    
    try:
        service = ChatStatisticsService(db)
        
        # Calcula as datas do período baseado no parâmetro days
        end_date = now_brazil()
        start_date = end_date - timedelta(days=days)
        
        filters = ChatStatisticsFilters(start_date=start_date, end_date=end_date)
        
        summary = service.get_summary_statistics(filters)
        time_stats = service.get_statistics_by_time(filters)
        topic_stats = service.get_statistics_by_topic(filters)
        
        peak_hour = None
        peak_day = None
        
        if time_stats["by_hour"]:
            peak_hour_data = max(time_stats["by_hour"], key=lambda x: x.message_count)
            peak_hour = {
                "hour": peak_hour_data.hour_of_day,
                "period": get_hour_period_pt(peak_hour_data.hour_of_day),
                "messages": peak_hour_data.message_count
            }
        
        if time_stats["by_day"]:
            peak_day_data = max(time_stats["by_day"], key=lambda x: x.message_count)
            peak_day = {
                "day": get_day_name_pt(peak_day_data.day_of_week),
                "messages": peak_day_data.message_count
            }
        
        # Top 5 tópicos
        top_topics = [
            {"topic": topic.topic, "messages": topic.message_count}
            for topic in topic_stats[:5]
        ]
        
        return {
            "period": f"Últimos {days} dias",
            "timezone": "Horário de Brasília (UTC-3)",
            "totals": {
                "messages": summary.total_messages,
                "questions": summary.total_questions,
                "users": summary.unique_users,
                "avg_response_time_ms": summary.average_response_time_ms
            },
            "peak_usage": {
                "hour": peak_hour,
                "day": peak_day
            },
            "top_topics": top_topics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )


# Endpoint público simplificado
@router.get(
    "/stats/public",
    response_model=dict,
    summary="Estatísticas Públicas",
    description="Estatísticas básicas para exibição pública"
)
async def get_public_stats(db: Session = Depends(get_db)):
    """
    Retorna estatísticas básicas para exibição pública.
    Apenas dados agregados, sem informações sensíveis.
    """
    try:
        service = ChatStatisticsService(db)
        summary = service.get_summary_statistics()
        
        return {
            "total_messages": summary.total_messages,
            "total_questions": summary.total_questions,
            "most_discussed_topics": [
                topic["topic"] for topic in summary.most_common_topics[:3]
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar estatísticas públicas: {str(e)}"
        ) 