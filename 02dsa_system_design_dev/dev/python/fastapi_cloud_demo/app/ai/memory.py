"""Conversation/session memory.

In-memory default keyed by session id. Pluggable: swap ``ConversationMemory``
for a Redis/DB-backed implementation with the same interface.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.ai.models.base import Role, make_message


class ConversationMemory:
    """Stores chat history per session id, in memory."""

    def __init__(self, max_messages: int = 50) -> None:
        self._store: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._max = max_messages

    def add(self, session_id: str, role: Role, content: str) -> None:
        history = self._store[session_id]
        history.append(make_message(role, content))
        if len(history) > self._max:
            del history[: len(history) - self._max]

    def history(self, session_id: str) -> list[dict[str, Any]]:
        return list(self._store[session_id])

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
