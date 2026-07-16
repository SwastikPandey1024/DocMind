from typing import Optional

from pydantic import BaseModel


class ReadinessResponse(BaseModel):
    """Readiness/degraded status response."""

    status: str  # healthy|degraded
    service: str  # DocMind Backend

    database: str  # healthy|unavailable
    storage: str  # healthy|unavailable
    ollama: str  # available|unavailable
    embedding_model: str  # loaded|not_loaded|unavailable
    vectorstore: str  # ready|empty|unavailable

    timestamp: Optional[str] = None
    error: Optional[str] = None

