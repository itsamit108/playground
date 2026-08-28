"""System specs + counter schemas (preserves original demo behavior)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class CounterResponse(BaseModel):
    count: int


class SystemSpecsResponse(BaseModel):
    os: dict[str, Any]
    python: dict[str, Any]
    cpu: dict[str, Any]
    memory: dict[str, Any]
    disk: dict[str, Any]
    gpu: dict[str, Any]
    process: dict[str, Any]


class RootResponse(BaseModel):
    message: str
    count: int
    system_specs: SystemSpecsResponse
