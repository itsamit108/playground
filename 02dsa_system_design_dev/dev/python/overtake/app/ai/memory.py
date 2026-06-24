"""Conversation / session memory.

In-memory, per-session ring buffer of chat turns (default, offline). Pluggable:
back it with Redis or a DB by implementing the same `Memory` protocol.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Protocol

from app.ai.models.base import Message, msg


class Memory(Protocol):
    def append(self, session_id: str, role: str, content: str) -> None: ...
    def history(self, session_id: str) -> list[Message]: ...
    def clear(self, session_id: str) -> None: ...


class InMemoryConversationMemory:
    """Keeps the last N turns per session id."""

    def __init__(self, max_turns: int = 20) -> None:
        self._max = max_turns
        self._store: dict[str, deque[Message]] = defaultdict(
            lambda: deque(maxlen=self._max)
        )

    def append(self, session_id: str, role: str, content: str) -> None:
        self._store[session_id].append(msg(role, content))  # type: ignore[arg-type]

    def history(self, session_id: str) -> list[Message]:
        return list(self._store.get(session_id, deque()))

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)


_memory = InMemoryConversationMemory()


def get_memory() -> InMemoryConversationMemory:
    """Return the shared conversation memory."""
    return _memory
