"""Conversation / session memory (folded from chatbot/conversation.py history).

Default implementation is an in-memory store keyed by session id. The
``ConversationMemory`` protocol keeps it pluggable (e.g. Redis via
``infra/cache.py`` later).
"""

from __future__ import annotations

import threading
from typing import Any, Protocol


class ConversationMemory(Protocol):
    def get(self, session_id: str) -> list[dict[str, Any]]: ...
    def append(self, session_id: str, message: dict[str, Any]) -> None: ...
    def reset(self, session_id: str) -> None: ...


class InMemoryConversationMemory:
    """Thread-safe in-process conversation history store."""

    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, Any]]] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._store.get(session_id, []))

    def append(self, session_id: str, message: dict[str, Any]) -> None:
        with self._lock:
            self._store.setdefault(session_id, []).append(message)

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._store.pop(session_id, None)

    def turn_count(self, session_id: str) -> int:
        """Number of user turns recorded for a session."""
        with self._lock:
            return sum(
                1 for m in self._store.get(session_id, []) if m.get("role") == "user"
            )


# Process-wide default memory used by the chat service.
_default_memory = InMemoryConversationMemory()


def get_default_memory() -> InMemoryConversationMemory:
    """Return the shared in-memory conversation store."""
    return _default_memory
