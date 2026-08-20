from __future__ import annotations

import json
import logging
from collections.abc import Mapping

from app.core.logging import setup_logging

logger = logging.getLogger("docuchat.auth")


def _ensure_base_logging() -> None:
    # setup_logging() is called from app/main.py, but keeping this guard makes the module safe to import
    # in isolation (e.g., scripts, background tasks).
    if not logging.getLogger().handlers:
        setup_logging()


def _emit(event_payload: Mapping[str, object], *, level: int) -> None:
    # Emit a stable structured JSON line for auth-related events.
    _ensure_base_logging()
    msg = json.dumps(dict(event_payload), default=str, ensure_ascii=False)
    logger.log(level, msg)


def log_auth_success(
    event: str,
    *,
    user_id: str | None = None,
    email: str | None = None,
    extra: Mapping[str, object] | None = None,
) -> None:
    payload: dict[str, object] = {
        "event": event,
        "user_id": user_id,
        "email": email,
        "success": True,
    }
    if extra:
        payload.update(dict(extra))

    _emit(payload, level=logging.INFO)


def log_auth_failure(
    event: str,
    *,
    reason: str,
    user_id: str | None = None,
    email: str | None = None,
    extra: Mapping[str, object] | None = None,
) -> None:
    payload: dict[str, object] = {
        "event": event,
        "reason": reason,
        "user_id": user_id,
        "email": email,
        "success": False,
    }
    if extra:
        payload.update(dict(extra))

    _emit(payload, level=logging.WARNING)


def log_security_event(
    event: str,
    *,
    user_id: str | None = None,
    email: str | None = None,
    extra: Mapping[str, object] | None = None,
) -> None:
    payload: dict[str, object] = {
        "event": event,
        "user_id": user_id,
        "email": email,
        "success": False,
    }
    if extra:
        payload.update(dict(extra))

    _emit(payload, level=logging.WARNING)

