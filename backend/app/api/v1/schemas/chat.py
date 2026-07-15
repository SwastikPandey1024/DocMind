from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    document_id: UUID
    question: str


class SourceReference(BaseModel):
    page: int
    chunk: int


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference]


class ChatHistoryItem(BaseModel):
    question: str
    answer: str
