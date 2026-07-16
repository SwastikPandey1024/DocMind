import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.api.v1.routes import auth_router, documents_router, health_router
from app.api.v1.routes.chat import set_services as set_chat_services
from app.api.v1.routes import chat_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.database.engine import engine
from app.middleware import setup_cors, setup_exceptions, setup_request_logging
from app.schemas.health import HealthResponse
from app.startup import validate_startup
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService, OllamaProvider
from app.services.rag_service import RAGService
from app.services.vectorstore_service import FAISSVectorStore

logger = logging.getLogger(__name__)
settings = get_settings()
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    
    # Startup
    logger.info(f"Starting DocMind Backend (env={settings.environment})")
    
    # Run startup validation
    try:
        await validate_startup()
    except RuntimeError as e:
        logger.error(f"✗ Startup validation failed: {e}")
        raise
    
    # Verify database connection
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✓ Database connection verified")
    except OperationalError as e:
        logger.error(f"✗ Database connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"✗ Startup error: {e}")
        raise
    
    # Initialize RAG and LLM services
    try:
        logger.info("Initializing RAG and LLM services")
        
        # Initialize embedding service
        embedding_service = EmbeddingService(
            model_name=settings.embedding_model,
            device="cpu",
            batch_size=32,
        )
        logger.info(f"✓ Embedding service ready: {settings.embedding_model}")
        
        # Initialize vector store
        vectorstore_path = Path(settings.storage_path) / "vectorstore"
        vectorstore_path.mkdir(parents=True, exist_ok=True)
        
        vector_store = FAISSVectorStore(
            vector_dim=embedding_service.embedding_dim,
            index_type="l2",
        )
        logger.info(f"✓ Vector store ready at {vectorstore_path}")
        
        # Initialize RAG service
        rag_service = RAGService(
            embedding_service=embedding_service,
            vector_store=vector_store,
        )
        logger.info("✓ RAG service ready")
        
        # Initialize LLM service with Ollama fallback
        llm_provider = OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )
        llm_service = LLMService(
            primary_provider=llm_provider,
            fallback_provider=None,
        )
        logger.info(f"✓ LLM service ready: {settings.ollama_model}")
        
        # Register services in chat router
        set_chat_services(rag_service, llm_service)
        
        logger.info("✓ All startup checks passed")
        
    except Exception as e:
        logger.error(f"✗ Service initialization error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down DocMind Backend")
    engine.dispose()
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

# Setup middleware (order matters - exceptions first, then logging, then CORS)
setup_exceptions(app)
setup_request_logging(app)
setup_cors(app)

# Include API routers
app.include_router(auth_router, prefix="/api/v1", tags=["authentication"])
app.include_router(documents_router, prefix="/api/v1", tags=["documents"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])
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
