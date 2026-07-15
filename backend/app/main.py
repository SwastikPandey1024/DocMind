from fastapi import FastAPI

from app.api.v1.routes import auth_router, health_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.schemas.health import HealthResponse

settings = get_settings()
setup_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

from app.api.v1.routes import auth_router, documents_router, health_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")



@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="healthy", service="DocMind Backend")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "DocMind API is running"}
