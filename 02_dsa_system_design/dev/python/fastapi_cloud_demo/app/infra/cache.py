"""Cache adapter.

In-memory cache by default. Swap for Redis behind the same interface.
"""

from __future__ import annotations

from typing import Any


class InMemoryCache:
    """A trivial in-process cache."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


cache = InMemoryCache()
