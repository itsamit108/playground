"""Observability hooks.

Seam for OpenTelemetry GenAI semantic conventions / Langfuse / LangSmith. The
default is a no-op span context manager + logging so the app runs with no
collector configured.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

from app.core.logging import get_logger

logger = get_logger("observability")


@contextmanager
def span(name: str, **attrs: object) -> Iterator[None]:
    """Lightweight timing span; replace with OTel spans in production."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.debug("span %s took %.1fms attrs=%s", name, elapsed_ms, attrs)
