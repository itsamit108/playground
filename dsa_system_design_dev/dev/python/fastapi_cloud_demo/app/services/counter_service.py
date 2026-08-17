"""Counter service.

Preserves the original demo's continuously-incrementing in-memory counter,
refactored into a service with an explicit background task lifecycle that the
app lifespan starts and stops.
"""

from __future__ import annotations

import asyncio

from app.core.logging import get_logger

logger = get_logger(__name__)


class CounterService:
    """Owns the in-memory counter and its background increment task."""

    def __init__(self, *, start: int = 0, interval_seconds: float = 1.0) -> None:
        self._count = start
        self._interval = interval_seconds
        self._task: asyncio.Task | None = None

    @property
    def count(self) -> int:
        return self._count

    def configure(self, *, start: int, interval_seconds: float) -> None:
        """Reconfigure the singleton (called from the app lifespan)."""
        self._count = start
        self._interval = interval_seconds

    async def _run(self) -> None:
        try:
            while True:
                await asyncio.sleep(self._interval)
                self._count += 1
        except asyncio.CancelledError:  # pragma: no cover - shutdown path
            logger.info("Counter task cancelled at count=%s", self._count)
            raise

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())
            logger.info("Counter task started")

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None


# Module-level singleton; configured/started in the app lifespan.
counter_service = CounterService()
