"""Observability adapter.

A no-op tracer by default so the app runs with zero observability backends. This
is the integration point for OpenTelemetry GenAI semantic conventions / Langfuse
/ LangSmith. The ``traced`` context manager logs span timing at DEBUG level.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

from app.core.logging import get_logger

logger = get_logger("observability")


@contextmanager
def traced(span_name: str, **attributes: object) -> Iterator[None]:
    start = time.perf_counter()
    logger.debug("span.start name=%s attrs=%s", span_name, attributes)
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.debug("span.end name=%s elapsed_ms=%.2f", span_name, elapsed_ms)
