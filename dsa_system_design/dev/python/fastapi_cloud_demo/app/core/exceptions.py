"""Application exception types and FastAPI exception handlers."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    error_code: str = "app_error"

    def __init__(self, message: str, *, status_code: int | None = None,
                 error_code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"


class GuardrailError(AppError):
    """Raised when a guardrail blocks input or output."""

    status_code = 400
    error_code = "guardrail_blocked"


class ProviderError(AppError):
    """Raised when an LLM provider fails."""

    status_code = 502
    error_code = "provider_error"


def register_exception_handlers(app: FastAPI) -> None:
    """Attach exception handlers to the app."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.error_code, "message": exc.message}},
        )
