"""Application exception types + FastAPI exception handlers."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    code: str = "app_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ProviderError(AppError):
    """Raised when an LLM provider fails."""

    status_code = 502
    code = "provider_error"


class GuardrailError(AppError):
    """Raised when input/output fails a guardrail check."""

    status_code = 400
    code = "guardrail_error"


class NotFoundError(AppError):
    """Raised when a requested resource is missing."""

    status_code = 404
    code = "not_found"


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers that render AppError subclasses as JSON."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
