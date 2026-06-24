"""Background task queue adapter.

Default is a synchronous, in-process executor so the app runs with no broker.
Replace with Celery/RQ/SQS by implementing the same `enqueue` contract.
"""

from __future__ import annotations

from typing import Any, Callable


class InProcessQueue:
    """Runs jobs immediately in-process (offline-friendly default)."""

    def enqueue(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)


_queue = InProcessQueue()


def get_queue() -> InProcessQueue:
    """Return the shared in-process queue."""
    return _queue
