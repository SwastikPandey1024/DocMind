from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from app.core.settings import get_settings


def create_access_token(subject: str, expires_delta: int | None = None) -> str:
    settings = get_settings()
    if expires_delta is None:
        expires_delta = settings.access_token_expire_minutes

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_token_expiry_minutes() -> int:
    settings = get_settings()
    return settings.access_token_expire_minutes
