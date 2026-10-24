"""FastAPI application factory + lifespan.

Wires the v1 router under /api/v1, configures logging, registers exception
handlers, and on startup creates DB tables and ensures the S3 bucket.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.infra.db import init_db
from app.infra.storage import get_storage

_log = get_logger("overtake.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables + ensure S3 bucket. Shutdown: nothing special."""
    settings = get_settings()
    setup_logging(settings.log_level)

    init_db()
    _log.info("db ready")

    # Best-effort bucket creation; the app still serves AI features without S3.
    try:
        get_storage(settings).ensure_bucket()
        _log.info("s3 bucket ready", extra={"extra_fields": {"bucket": settings.s3_bucket_name}})
    except Exception as exc:  # noqa: BLE001
        _log.warning(
            "s3 bucket setup skipped",
            extra={"extra_fields": {"error": str(exc)}},
        )

    yield


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan,
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
