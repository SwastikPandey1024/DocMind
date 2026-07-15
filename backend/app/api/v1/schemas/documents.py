from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    filename: str
    status: str = "Uploaded"


class DocumentListItem(BaseModel):
    document_id: UUID
    filename: str
    pages: Optional[int] = None
    status: str


class DocumentDetailResponse(BaseModel):
    document_id: UUID
    filename: str
    uploaded_at: datetime
    pages: Optional[int] = None
    status: str
