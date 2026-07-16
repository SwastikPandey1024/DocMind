import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

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
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService, OllamaProvider
from app.services.rag_memory_store import RAGMemoryStore
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)
settings = get_settings()
setup_logging()

# Global services
embedding_service: Optional[EmbeddingService] = None
rag_memory_store: Optional[RAGMemoryStore] = None
chat_service: Optional[ChatService] = None
llm_service: Optional[LLMService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""

    global embedding_service, rag_memory_store, chat_service, llm_service

    # Startup
    logger.info(f"Starting DocMind Backend (env={settings.environment})")

    # Run startup validation (ONLY database configuration should be fatal)
    try:
        await validate_startup()
    except RuntimeError as e:
        # Treat config errors as fatal (per requirement)
        logger.error(f"✗ Startup validation failed: {e}")
        raise

    # Verify database connection (fatal)
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✓ Database connection verified")
    except OperationalError as e:
        logger.error(f"✗ Database connection failed: {e}")
        raise

    # AI services MUST NOT block server boot.
    # Lazy-load them later on first request.
    try:
        app.state.ollama_status = "degraded"
        app.state.embedding_status = "not_loaded"
        app.state.vectorstore_status = "empty"
    except Exception:
        pass

    yield

    # Shutdown
    logger.info("Shutting down DocMind Backend")
    try:
        engine.dispose()
    except Exception:
        pass
    logger.info("✓ Resources cleaned up")



# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="OCR + RAG Document Chat System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# If AI dependencies are unavailable, we still want the server to boot.
# These flags are set during lazy initialization / degraded mode.
app.state.ollama_status = "unknown"
app.state.embedding_status = "unknown"
app.state.vectorstore_status = "unknown"
app.state.storage_status = "unknown"


# Setup middleware (order matters - exceptions first, then logging, then CORS)
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
    """Health check endpoint for load balancers and orchestration."""
    return HealthResponse(status="healthy", service="DocMind Backend")


@app.get("/", tags=["root"])
async def read_root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "DocMind API is running", "version": settings.app_version}


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



