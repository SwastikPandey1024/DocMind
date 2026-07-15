from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.auth.password import validate_password_strength


class TokenPayload(BaseModel):
    """Decoded JWT payload.

    Matches :func:`app.auth.jwt.decode_token` output fields.
    """

    sub: str
    type: str
    exp: datetime
    iat: datetime


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        try:
            validate_password_strength(value)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    name: str
    email: EmailStr
    role: str = "user"
    is_active: bool
    created_at: datetime


class MessageResponse(BaseModel):
    message: str


__all__ = [
    "LoginRequest",
    "MessageResponse",
    "RefreshTokenRequest",
    "RegisterRequest",
    "TokenPayload",
    "TokenResponse",
    "UserResponse",
]

