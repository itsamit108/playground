"""Health / readiness endpoints + preserved counter and specs routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_app_settings, get_counter_service, get_system_service
from app.core.config import Settings
from app.schemas.common import HealthResponse
from app.schemas.system import CounterResponse, SystemSpecsResponse
from app.services.counter_service import CounterService
from app.services.system_service import SystemService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(get_app_settings),
    counter: CounterService = Depends(get_counter_service),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        count=counter.count,
        app=settings.app_name,
        version=settings.app_version,
    )


@router.get("/counter", response_model=CounterResponse)
def counter(
    counter: CounterService = Depends(get_counter_service),
) -> CounterResponse:
    return CounterResponse(count=counter.count)


@router.get("/specs", response_model=SystemSpecsResponse)
def specs(
    system: SystemService = Depends(get_system_service),
) -> SystemSpecsResponse:
    return SystemSpecsResponse(**system.specs())
