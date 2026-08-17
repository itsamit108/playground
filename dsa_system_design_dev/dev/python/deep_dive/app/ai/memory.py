"""Conversation / session memory.

In-memory default keyed by session id, with a pluggable interface so it can be
swapped for Redis (see ``infra/cache.py``) or a durable store later.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any


class ConversationMemory:
    def __init__(self, max_messages: int = 50):
        self._store: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._lock = threading.Lock()
        self._max = max_messages

    def append(self, session_id: str, message: dict[str, Any]) -> None:
        with self._lock:
            history = self._store[session_id]
            history.append(message)
            if len(history) > self._max:
                del history[: len(history) - self._max]

    def extend(self, session_id: str, messages: list[dict[str, Any]]) -> None:
        for m in messages:
            self.append(session_id, m)

    def get(self, session_id: str) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._store.get(session_id, []))

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._store.pop(session_id, None)


_memory: ConversationMemory | None = None


def get_memory() -> ConversationMemory:
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
    return _memory
