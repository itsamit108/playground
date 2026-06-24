"""Auth helpers.

This app does not manage users, so security is a simple optional API-key check.
When ``settings.api_key`` is empty (the default / offline mode) auth is a no-op,
keeping every endpoint usable with zero configuration.
"""

from __future__ import annotations

from fastapi import Header

from app.core.config import Settings
from app.core.exceptions import AppError


class AuthError(AppError):
    status_code = 401
    code = "unauthorized"


def verify_api_key(settings: Settings, provided: str | None) -> None:
    """Raise ``AuthError`` if an API key is configured and the request lacks it."""
    if not settings.api_key:
        return  # offline / open mode
    if provided != settings.api_key:
        raise AuthError("Invalid or missing API key.")


def api_key_header(x_api_key: str | None = Header(default=None)) -> str | None:
    """FastAPI header extractor for the optional ``X-API-Key`` header."""
    return x_api_key
