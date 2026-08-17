"""Health / readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.api.deps import SettingsDep
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=__version__,
        llm_provider=settings.llm_provider,
    )


@router.get("/ready", response_model=HealthResponse)
async def ready(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(
        status="ready",
        service=settings.app_name,
        version=__version__,
        llm_provider=settings.llm_provider,
    )
