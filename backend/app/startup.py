"""Startup validation checks."""

import logging
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def validate_startup() -> None:
    """Run all startup validation checks."""
    
    settings = get_settings()
    logger.info("Running startup validation checks...")
    
    # Check environment
    logger.info(f"  Environment: {settings.environment}")
    logger.info(f"  Debug mode: {settings.debug}")
    
    # Check upload directory
    upload_dir = Path(settings.upload_dir)
    try:
        upload_dir.mkdir(parents=True, exist_ok=True)
        test_file = upload_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        logger.info(f"  ✓ Upload directory writable: {settings.upload_dir}")
    except Exception as e:
        logger.error(f"  ✗ Upload directory not writable: {e}")
        raise RuntimeError(f"Cannot write to upload directory: {settings.upload_dir}")
    
    # Check JWT configuration
    if settings.environment == "production":
        if settings.jwt_secret in ("change-me-in-production", ""):
            raise RuntimeError("JWT_SECRET must be set in production")
        logger.info(f"  ✓ JWT secret configured")
    
    # Check database URL format
    if not settings.database_url.startswith(("postgresql://", "postgresql+psycopg2://", "sqlite:///")):
        raise RuntimeError(f"Invalid DATABASE_URL: {settings.database_url}")
    logger.info(f"  ✓ Database URL format valid")
    
    logger.info("✓ All startup checks passed")
