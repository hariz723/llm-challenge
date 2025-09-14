from src.models.database import Base
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from uuid import UUID
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as psqlUuid


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(
        psqlUuid(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[UUID] = mapped_column(
        psqlUuid(as_uuid=True), ForeignKey("users.id")
    )
    title: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(
        psqlUuid(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    conversation_id: Mapped[UUID] = mapped_column(
        psqlUuid(as_uuid=True), ForeignKey("conversations.id")
    )
    sender: Mapped[str] = mapped_column(String)  # e.g., "user", "bot"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(
        psqlUuid(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[UUID] = mapped_column(
        psqlUuid(as_uuid=True), ForeignKey("users.id")
    )
    filename: Mapped[str] = mapped_column(String, index=True)
    blob_url: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")
