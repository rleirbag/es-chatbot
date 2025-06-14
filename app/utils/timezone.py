"""
Utilitários para gerenciamento de fuso horário
Configurado para UTC-3 (Horário de Brasília)
"""

from datetime import datetime, timezone, timedelta
from typing import Optional


# Fuso horário de Brasília (UTC-3)
BRAZIL_TIMEZONE = timezone(timedelta(hours=-3))


def now_brazil() -> datetime:
    """
    Retorna a data/hora atual no fuso horário de Brasília (UTC-3)
    
    Returns:
        datetime: Data/hora atual em UTC-3
    """
    return datetime.now(BRAZIL_TIMEZONE)


def to_brazil_timezone(dt: datetime) -> datetime:
    """
    Converte uma datetime para o fuso horário de Brasília
    
    Args:
        dt: Datetime a ser convertida
        
    Returns:
        datetime: Datetime convertida para UTC-3
    """
    if dt.tzinfo is None:
        # Se não tem timezone, assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.astimezone(BRAZIL_TIMEZONE)


def get_brazil_hour_and_day(dt: Optional[datetime] = None) -> tuple[int, int]:
    """
    Retorna a hora do dia (0-23) e dia da semana (0-6) no fuso horário de Brasília
    
    Args:
        dt: Datetime específica (opcional, usa agora se não fornecida)
        
    Returns:
        tuple: (hora_do_dia, dia_da_semana) em UTC-3
    """
    if dt is None:
        dt = now_brazil()
    else:
        dt = to_brazil_timezone(dt)
    
    return dt.hour, dt.weekday()


def format_brazil_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M:%S") -> str:
    """
    Formata uma datetime no fuso horário de Brasília
    
    Args:
        dt: Datetime a ser formatada
        format_str: String de formato (padrão brasileiro)
        
    Returns:
        str: Data formatada em UTC-3
    """
    brazil_dt = to_brazil_timezone(dt)
    return brazil_dt.strftime(format_str)


def get_day_name_pt(day_of_week: int) -> str:
    """
    Retorna o nome do dia da semana em português
    
    Args:
        day_of_week: Dia da semana (0=segunda, 6=domingo)
        
    Returns:
        str: Nome do dia em português
    """
    days = [
        "Segunda-feira",
        "Terça-feira", 
        "Quarta-feira",
        "Quinta-feira",
        "Sexta-feira",
        "Sábado",
        "Domingo"
    ]
    return days[day_of_week] if 0 <= day_of_week <= 6 else "Desconhecido"


def get_hour_period_pt(hour: int) -> str:
    """
    Retorna o período do dia em português
    
    Args:
        hour: Hora do dia (0-23)
        
    Returns:
        str: Período do dia em português
    """
    if 5 <= hour < 12:
        return "Manhã"
    elif 12 <= hour < 18:
        return "Tarde"
    elif 18 <= hour < 22:
        return "Noite"
    else:
        return "Madrugada" 