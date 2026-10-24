"""Observability adapter.

A minimal tracing shim with the OpenTelemetry/Langfuse shape (spans as context
managers). The default is a no-op logger-backed tracer; wire OpenTelemetry or
Langfuse here in production per the architecture's ecosystem table.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

from app.core.logging import get_logger

_log = get_logger("overtake.trace")


@contextmanager
def span(name: str, **attributes: object) -> Iterator[None]:
    """Trace a unit of work; emits a structured log line with duration."""
    start = time.perf_counter()
    try:
        yield
    finally:
        dur_ms = round((time.perf_counter() - start) * 1000, 2)
        _log.info(
            "span", extra={"extra_fields": {"name": name, "ms": dur_ms, **attributes}}
        )
