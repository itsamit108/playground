"""Auth helpers.

The demo runs open by default. When ``settings.api_key`` is configured, the
``require_api_key`` dependency enforces an ``X-API-Key`` header. Otherwise it is
a no-op so the app works out of the box.
"""

from __future__ import annotations

from fastapi import Header

from app.core.config import Settings, get_settings
from app.core.exceptions import AppError


class AuthError(AppError):
    status_code = 401
    error_code = "unauthorized"


def verify_api_key(provided: str | None, settings: Settings) -> None:
    """Validate an API key against settings. No-op if no key is configured."""
    if not settings.api_key:
        return
    if provided != settings.api_key:
        raise AuthError("Invalid or missing API key")


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """FastAPI dependency enforcing the API key when configured."""
    verify_api_key(x_api_key, get_settings())
