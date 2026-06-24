"""Queue adapter.

The background counter runs as an asyncio task (see ``services/counter_service``).
For durable/distributed work this is where Celery / RQ / a broker would live.
"""

from __future__ import annotations

import asyncio
from typing import Any


class InMemoryQueue:
    """A thin wrapper around asyncio.Queue for in-process jobs."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Any] = asyncio.Queue()

    async def put(self, item: Any) -> None:
        await self._queue.put(item)

    async def get(self) -> Any:
        return await self._queue.get()

    def qsize(self) -> int:
        return self._queue.qsize()
