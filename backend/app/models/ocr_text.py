"""OCR Text model."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class OCRText(TimestampMixin, Base):
    """Extracted OCR text from document pages."""
    
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
    
    # OCR block details
    block_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocks_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    detected_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    document = relationship("Document", back_populates="ocr_texts")
