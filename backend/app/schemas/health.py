from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str  # "healthy", "degraded", "unhealthy"
    service: str  # "DocuChat Backend"
    timestamp: Optional[str] = None  # ISO 8601 timestamp
    error: Optional[str] = None  # Error message if status != healthy
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "DocuChat Backend",
                "timestamp": "2024-01-15T10:30:00.000000",
            }
        }
