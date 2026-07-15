from __future__ import annotations

import uuid

from fastapi import HTTPException, status

from app.auth.jwt import TokenDecodeError, create_access_token, create_refresh_token, decode_token
from app.auth.password import hash_password, verify_password
from app.auth.schemas import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse

from app.auth.logging import log_auth_failure, log_auth_success, log_security_event

from app.models.user import User

from app.repositories.user import UserRepository




class AuthService:

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository


    def register(self, payload: RegisterRequest) -> User:
        email = str(payload.email).lower()
        existing_user = self.user_repository.get_by_email(email)
        if existing_user is not None:
            log_auth_failure(
                "auth.register",
                reason="duplicate_email",
                email=email,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        user = self.user_repository.create(
            obj_in={
                "name": payload.name.strip(),
                "email": email,
                "password_hash": hash_password(payload.password),
                "is_active": True,
                "role": "user",
            }
        )
        log_auth_success(
            "auth.register",
            user_id=str(user.user_id),
            email=email,
        )
        return user


    def login(self, payload: LoginRequest) -> TokenResponse:
        email = str(payload.email).lower()
        user = self.user_repository.get_by_email(email)
        if user is None or not verify_password(payload.password, user.password_hash):
            log_auth_failure(
                "auth.login",
                reason="invalid_credentials",
                email=email,
            )
            log_security_event(
                "security.login_failed",
                email=email,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active or user.is_deleted:
            log_auth_failure(
                "auth.login",
                reason="inactive_or_deleted_user",
                user_id=str(user.user_id),
                email=email,
            )
            log_security_event(
                "security.login_forbidden",
                user_id=str(user.user_id),
                email=email,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        tokens = self._create_token_pair(user)
        log_auth_success(
            "auth.login",
            user_id=str(user.user_id),
            email=email,
        )
        return tokens


    def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        try:
            token_payload = decode_token(payload.refresh_token, expected_type="refresh")
            user_id = uuid.UUID(str(token_payload["sub"]))
        except (TokenDecodeError, ValueError) as exc:
            log_auth_failure(
                "auth.refresh",
                reason="invalid_refresh_token",
            )
            log_security_event(
                "security.refresh_failed",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        user = self.user_repository.get(user_id)
        if user is None or not user.is_active or user.is_deleted:
            log_auth_failure(
                "auth.refresh",
                reason="invalid_refresh_subject_or_inactive_user",
                user_id=str(user_id),
                email=getattr(user, "email", None),
            )
            log_security_event(
                "security.refresh_failed",
                user_id=str(user_id),
                email=getattr(user, "email", None),
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        tokens = self._create_token_pair(user)
        log_auth_success(
            "auth.refresh",
            user_id=str(user.user_id),
            email=user.email,
        )
        return tokens


    @staticmethod
    def _create_token_pair(user: User) -> TokenResponse:
        subject = str(user.user_id)
        return TokenResponse(
            access_token=create_access_token(subject),
            refresh_token=create_refresh_token(subject),
        )
