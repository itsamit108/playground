"""Health / readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import SettingsDep
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(
        status="ok", service="overtake", version=settings.app_version
    )
