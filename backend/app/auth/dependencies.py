from __future__ import annotations

import uuid
from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt import TokenDecodeError, decode_token
from app.auth.service import AuthService
from app.database.dependencies import get_db_session
from app.models.user import User
from app.repositories.user import UserRepository


bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)


def get_auth_service(user_repository: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repository)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """Return the authenticated user.

    Backward compatibility: this keeps existing behavior/response codes.
    """
    if credentials is None or not credentials.credentials:
        print("=" * 80)
        print("CREDENTIALS OBJECT:", credentials)
        
        if credentials:
             print("SCHEME:", credentials.scheme)
             print("TOKEN:", credentials.credentials[:40] + "...")
        print("=" * 80)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials, expected_type="access")
        user_id = uuid.UUID(str(payload["sub"]))
    except (TokenDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = user_repository.get(user_id)
    if user is None or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Existing behavior treated inactive as 401. Preserve that behavior.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Enforce active user.

    This is effectively the same as get_current_user today (which already checks is_active).
    Kept as a separate dependency to satisfy the Epic and allow future divergence.
    """
    if not current_user.is_active or current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def get_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Admin-only dependency placeholder.

    Currently implements a simple role check.
    (If you later add real admin claims, this dependency is the single place to update.)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_user

