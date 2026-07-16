from functools import lru_cache
from typing import Literal

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import Environment


class Settings(BaseSettings):
    app_name: str = Field(default="DocMind", validation_alias="APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    environment: Literal["development", "testing", "production"] = Field(
        default=Environment.DEVELOPMENT,
        validation_alias="APP_ENV",
    )
    debug: bool = Field(default=False, validation_alias="DEBUG")
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@postgres:5432/docmind",
        validation_alias="DATABASE_URL"
    )
    jwt_secret: str = Field(default="change-me-in-production", validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")
    upload_dir: str = Field(default="/app/storage/uploads", validation_alias="UPLOAD_DIR")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    
    # AI/ML Services
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    ollama_base_url: str = Field(default="http://ollama:11434", validation_alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama2", validation_alias="OLLAMA_MODEL")
    embedding_model: str = Field(default="bge-small", validation_alias="EMBEDDING_MODEL")
    ocr_language: str = Field(default="en", validation_alias="OCR_LANGUAGE")
    
    # Storage and limits
    max_upload_size_mb: int = Field(default=50, validation_alias="MAX_UPLOAD_SIZE_MB")
    storage_path: str = Field(default="/app/storage", validation_alias="STORAGE_PATH")
    vectorstore_path: str = Field(default="/app/storage/vectorstore", validation_alias="VECTORSTORE_PATH")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: str, info: ValidationInfo) -> str:
        if info.data.get("environment") == Environment.PRODUCTION and value in {"change-me-in-production", ""}:
            raise ValueError("JWT_SECRET must be set in production")
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith(("postgresql://", "postgresql+psycopg2://", "sqlite:///")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL or SQLite connection string")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
