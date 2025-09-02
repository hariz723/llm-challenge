from src.models.database import Base
from sqlalchemy import String, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from uuid import UUID
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as psqlUuid


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        psqlUuid(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user")
    documents = relationship("Document", back_populates="user")
