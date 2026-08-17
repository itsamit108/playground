"""Health / readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.ai.models.factory import get_llm_client
from app.api.deps import SettingsDep
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(settings: SettingsDep) -> HealthResponse:
    provider = getattr(get_llm_client(settings), "name", "unknown")
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        llm_provider=provider,
        offline_mode=not settings.has_llm_key,
    )


@router.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}
