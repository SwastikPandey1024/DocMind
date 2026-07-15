from __future__ import annotations

# Backward-compatible re-export layer.
# The actual implementations live in app/auth/* to keep auth logic centralized.

from app.auth.dependencies import (  # noqa: F401
    bearer_scheme,
    get_admin_user,
    get_auth_service,
    get_current_active_user,
    get_current_user,
    get_user_repository,
)

__all__ = [
    "bearer_scheme",
    "get_user_repository",
    "get_auth_service",
    "get_current_user",
    "get_current_active_user",
    "get_admin_user",
]

