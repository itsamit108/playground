"""Conversation / session memory.

In-memory, per-session ring buffer of chat turns (default, offline). Pluggable:
back it with Redis or a DB by implementing the same `Memory` protocol.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Protocol

from app.ai.models.base import msg


class Memory(Protocol):
    def append(self, session_id: str, role: str, content: str) -> None: ...
    def history(self, session_id: str) -> list[dict[str, Any]]: ...
    def clear(self, session_id: str) -> None: ...


class InMemoryConversationMemory:
    """Keeps the last N turns per session id."""

    def __init__(self, max_turns: int = 20) -> None:
        self._max = max_turns
        self._store: dict[str, deque[dict[str, Any]]] = defaultdict(
            lambda: deque(maxlen=self._max)
        )

    def append(self, session_id: str, role: str, content: str) -> None:
        self._store[session_id].append(msg(role, content))

    def history(self, session_id: str) -> list[dict[str, Any]]:
        return list(self._store.get(session_id, deque()))

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)


_memory = InMemoryConversationMemory()


def get_memory() -> InMemoryConversationMemory:
    """Return the shared conversation memory."""
    return _memory
