"""Chat request/response schemas."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CitationMetadata(BaseModel):
    """Citation metadata from a source chunk."""
    document_id: str
    chunk_index: int
    page_number: Optional[int] = None
    similarity_score: float = Field(ge=0, le=1)
    snippet: str


class ChatRequest(BaseModel):
    """Chat query request."""
    document_id: UUID
    question: str
    temperature: float = Field(0.7, ge=0, le=2.0)
    include_sources: bool = True


class ChatResponse(BaseModel):
    """Chat query response."""
    answer: str
    citations: list[CitationMetadata] = []
    response_time_ms: int = 0
    model: str = "gpt-3.5-turbo"


class ChatStreamChunk(BaseModel):
    """Streaming chunk of chat response."""
    chunk: str
    is_final: bool = False
    citations: Optional[list[CitationMetadata]] = None


class ChatHistoryItem(BaseModel):
    """Chat history entry."""
    chat_id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    question: str
    answer: str
    response_time_ms: Optional[int] = None
    created_at: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    """List of chat history items."""
    items: list[ChatHistoryItem]
    total: int
