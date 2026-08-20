from typing import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

settings = get_settings()


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware based on environment."""
    
    # Parse allowed origins from environment or use defaults
    if settings.environment == "production":
        allowed_origins = [
            "https://docuchat.example.com",
            "https://app.docuchat.example.com",
        ]
    else:
        # Development: allow all localhost variants
        allowed_origins = [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8000",
            "http://127.0.0.1",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
            "http://frontend",  # Docker network
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
        max_age=3600,
    )
