"""Cache adapter.

Ships with a process-local in-memory cache (default, offline). Swap for Redis
in production by implementing the same `Cache` protocol.
"""

from __future__ import annotations

from typing import Any, Protocol


class Cache(Protocol):
    def get(self, key: str) -> Any | None: ...
    def set(self, key: str, value: Any) -> None: ...


class InMemoryCache:
    """Trivial dict-backed cache."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value


_cache = InMemoryCache()


def get_cache() -> InMemoryCache:
    """Return the shared in-memory cache."""
    return _cache
