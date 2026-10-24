"""Auth helpers.

This service uses a simple optional API-key scheme. When ``settings.api_key``
is unset (the offline/default case) auth is a no-op so the app and tests run
with zero configuration.
"""

from __future__ import annotations

from fastapi import Header

from app.core.config import Settings


def verify_api_key(settings: Settings, provided: str | None) -> bool:
    """Return True if the request is authorised.

    No key configured -> always authorised (no-op).
    """
    if not settings.api_key:
        return True
    return provided is not None and provided == settings.api_key


# Header alias re-exported for routers/deps that want the raw header.
ApiKeyHeader = Header(default=None, alias="X-API-Key")
