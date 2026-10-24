"""Application exception types + FastAPI exception handlers."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for application errors mapped to HTTP responses."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    detail: str = "Application error"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Resource conflict"


class AuthError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication failed"


class GuardrailError(AppError):
    """Raised when input/output fails a safety guardrail."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Request blocked by guardrail"


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers that turn AppError subclasses into JSON responses."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        headers = (
            {"WWW-Authenticate": "Bearer"}
            if isinstance(exc, AuthError)
            else None
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers,
        )
