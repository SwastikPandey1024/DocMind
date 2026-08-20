import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

from app.api.v1.routes import auth_router, documents_router, health_router
from app.api.v1.routes.chat import set_services as set_chat_services
from app.api.v1.routes import chat_router
from app.api.v1.routes.ready import router as ready_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.database.engine import engine
from app.middleware import setup_cors, setup_exceptions, setup_request_logging
from app.schemas.health import HealthResponse
from app.startup import validate_startup

logger = logging.getLogger(__name__)
settings = get_settings()
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    logger.info(f"Starting DocuChat Backend (env={settings.environment})")

    # Validate startup configuration (ONLY database is fatal)
    try:
        await validate_startup()
    except RuntimeError as e:
        logger.error(f"✗ Startup validation failed: {e}")
        raise

    # Verify database connection (fatal)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection verified")
    except OperationalError as e:
        logger.error(f"✗ Database connection failed: {e}")
        raise

    # AI services initialized LAZILY on first request
    # Don't block server boot
    app.state.services_initialized = False
    app.state.embedding_service = None
    app.state.rag_memory_store = None
    app.state.chat_service = None
    app.state.llm_service = None

    logger.info("✓ Backend ready (AI services lazy-loaded)")

    yield

    # Shutdown
    logger.info("Shutting down DocuChat Backend")
    try:
        engine.dispose()
    except Exception:
        pass
    logger.info("✓ Resources cleaned up")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="OCR + RAG Document Chat System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Initialize state
app.state.services_initialized = False
app.state.embedding_service = None
app.state.rag_memory_store = None
app.state.chat_service = None
app.state.llm_service = None

# Setup middleware (order matters)
setup_exceptions(app)
setup_request_logging(app)
setup_cors(app)

# Include API routers
app.include_router(auth_router, prefix="/api/v1", tags=["authentication"])
app.include_router(documents_router, prefix="/api/v1", tags=["documents"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(ready_router, prefix="/api/v1", tags=["health"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Health check endpoint for load balancers."""
    return HealthResponse(status="healthy", service="DocuChat Backend")


@app.get("/", tags=["root"])
async def read_root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "DocuChat API is running", "version": settings.app_version}


def custom_openapi():
    """Custom OpenAPI schema with security scheme."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description="OCR + RAG Document Chat System",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer token from /api/v1/auth/login",
        }
    }

    # Mark protected endpoints
    for path, methods in openapi_schema.get("paths", {}).items():
        if "/auth/me" in path or "/documents" in path or "/chat" in path:
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    details["security"] = [{"Bearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
