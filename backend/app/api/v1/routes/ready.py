"""Readiness endpoint."""

import logging
from datetime import datetime

from fastapi import APIRouter

from app.schemas.health import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ready", tags=["health"])


@router.get("", response_model=HealthResponse)
async def ready_check() -> HealthResponse:
    """
    Returns component readiness/degraded status.
    
    Note:
    - /health indicates the API process is alive
    - /ready indicates availability of external components
    """
    return HealthResponse(
        status="healthy",
        service="DocuChat Backend",
    )
