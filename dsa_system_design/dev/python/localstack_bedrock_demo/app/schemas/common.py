"""Shared/common schemas."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    version: str
    llm_provider: str


class ErrorDetail(BaseModel):
    code: str
    message: str
