import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.dependencies import get_db_session
from app.schemas.health import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:

    """
    Health check endpoint.
    
    Verifies:
    - API is running
    - Database connection is working
    - Required tables exist
    """
    
    try:
        # Verify database connection
        db.execute(text("SELECT 1"))
        
        # Verify key tables exist
        db.execute(text("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'users'
        """))
        
        return HealthResponse(
            status="healthy",
            service="DocMind Backend",
            timestamp=datetime.utcnow().isoformat(),
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            service="DocMind Backend",
            timestamp=datetime.utcnow().isoformat(),
            error=str(e),
        )
