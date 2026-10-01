"""Task queue adapter (placeholder).

Seam for Celery / RQ / SQS (LocalStack provides SQS too). Not used by default.
"""

from __future__ import annotations

from collections import deque
from typing import Any


class InMemoryQueue:
    def __init__(self) -> None:
        self._q: deque[Any] = deque()

    def enqueue(self, item: Any) -> None:
        self._q.append(item)

    def dequeue(self) -> Any:
        return self._q.popleft() if self._q else None


_queue = InMemoryQueue()


def get_queue() -> InMemoryQueue:
    return _queue
