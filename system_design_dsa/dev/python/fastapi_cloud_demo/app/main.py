"""FastAPI application factory + lifespan.

Entrypoint ``app.main:app`` (referenced by ``[tool.fastapi]`` and the
``.fastapicloud/`` deploy config). The app factory wires the v1 API router,
exception handlers, logging, and the background counter lifecycle.

Original demo behavior is preserved as first-class features:
- ``/`` , ``/health`` , ``/counter`` , ``/specs`` still work (root + /api/v1).
- the counter runs as a background task started in the lifespan.
- system specs come from the system service (psutil/GPU logic).
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.schemas.system import RootResponse, SystemSpecsResponse
from app.services.counter_service import counter_service
from app.services.system_service import system_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(level=settings.log_level, json_logs=settings.log_json)
    logger = get_logger("app.main")

    # Configure and start the background counter (preserved demo behavior).
    counter_service.configure(
        start=settings.counter_start,
        interval_seconds=settings.counter_interval_seconds,
    )
    counter_service.start()
    logger.info("%s v%s started", settings.app_name, settings.app_version)

    try:
        yield
    finally:
        await counter_service.stop()
        logger.info("Shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    # Versioned API.
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # --- Preserved root endpoints (backwards compatible) ---
    @app.get("/", response_model=RootResponse, tags=["root"])
    def home() -> RootResponse:
        return RootResponse(
            message="Counter is running",
            count=counter_service.count,
            system_specs=SystemSpecsResponse(**system_service.specs()),
        )

    @app.get("/health", tags=["health"])
    def root_health() -> dict:
        return {
            "status": "ok",
            "count": counter_service.count,
            "system_specs": system_service.specs(),
        }

    @app.get("/counter", tags=["counter"])
    def root_counter() -> dict:
        return {"count": counter_service.count}

    @app.get("/specs", tags=["specs"])
    def root_specs() -> dict:
        return system_service.specs()

    return app


app = create_app()
