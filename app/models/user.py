import enum
from datetime import datetime

from sqlalchemy import Enum as SQLAlchemyEnum, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    avatar_url: Mapped[str] = mapped_column()
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole),
        default=UserRole.USER,
        server_default=UserRole.USER.value,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        onupdate=func.now(), nullable=True
    )
    refresh_token: Mapped[str] = mapped_column()

    documents = relationship(
        'Document', back_populates='user', cascade='all, delete-orphan'
    )
    
    chat_histories = relationship(
        'ChatHistory', back_populates='user', cascade='all, delete-orphan'
    )
