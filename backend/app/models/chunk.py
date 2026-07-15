from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class OCRText(TimestampMixin, Base):
    __tablename__ = "ocr_text"

    text_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False, index=True
    )
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    clean_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    document = relationship("Document", back_populates="ocr_texts")


class Chunk(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "chunks"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_key: Mapped[str] = mapped_column(String(255), ForeignKey("embedding_metadata.embedding_key"), nullable=False, index=True)

    document = relationship("Document", back_populates="chunks")
    embedding_metadata = relationship("EmbeddingMetadata", back_populates="chunk")


class EmbeddingMetadata(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "embedding_metadata"

    embedding_key: Mapped[str] = mapped_column(String(255), primary_key=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)

    chunk = relationship("Chunk", back_populates="embedding_metadata", uselist=False)
