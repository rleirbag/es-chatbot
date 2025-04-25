from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class Document(Base):
    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    shared_link: Mapped[str] = mapped_column()
    g_file_id: Mapped[str] = mapped_column(unique=True)
    g_folder_id: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user = relationship('User', back_populates='documents')

    __table_args__ = (
        UniqueConstraint('user_id', 'g_file_id', name='_user_document_uc'),
    )
