"""Task queue adapter.

The conversion endpoint uses FastAPI ``BackgroundTasks`` (in-process) by default.
For durable, distributed jobs this is the slot for Celery / RQ / arq behind the
same ``enqueue`` interface.
"""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable


async def enqueue(coro_fn: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> asyncio.Task:
    """Fire-and-forget an async task on the running event loop."""
    return asyncio.create_task(coro_fn(*args, **kwargs))
