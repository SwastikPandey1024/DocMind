"""Readiness endpoint.

This endpoint must never return 500 simply because AI dependencies are unavailable.
"""

import logging
from datetime import datetime

from fastapi import APIRouter

from app.api.v1.schemas.health_ready import ReadinessResponse
from app.schemas.health import HealthResponse



logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ready", tags=["health"])


@router.get("", response_model=ReadinessResponse)
async def ready_check() -> ReadinessResponse:

    """
    Returns component readiness/degraded status.

    Note:
    - /health indicates the API process is alive
    - /ready indicates availability of external components
    """

    # If services were marked during lifespan, use those.
    # If not present, return degraded.
    try:
        # Main process state is attached in app.state by backend/app/main.py
        from app.main import app as fastapi_app  # local import to avoid hard dependency

        ollama_status = getattr(fastapi_app.state, "ollama_status", "unknown")
        embedding_status = getattr(fastapi_app.state, "embedding_status", "unknown")
        vectorstore_status = getattr(fastapi_app.state, "vectorstore_status", "unknown")
        storage_status = getattr(fastapi_app.state, "storage_status", "unknown")

        # Database is considered healthy if app booted far enough.
        # If DB migrations/queries are wrong, other endpoints will degrade.
        database_status = "healthy"

        overall = "healthy"
        if any(
            s in {"unavailable", "not_loaded", "empty", "unknown"}
            for s in [ollama_status, embedding_status, vectorstore_status, storage_status]
        ):
            overall = "degraded"

        return HealthResponse(
            status=overall,
            service="DocMind Backend",
            timestamp=datetime.utcnow().isoformat(),
            error=None
            if overall == "healthy"
            else "One or more dependencies are unavailable",
        )

    except Exception as e:
        logger.warning(f"Readiness check failed (degraded): {e}")
        return HealthResponse(
            status="degraded",
            service="DocMind Backend",
            timestamp=datetime.utcnow().isoformat(),
            error=str(e),
        )

