"""Cache adapter — in-process dict by default, pluggable for Redis."""

from __future__ import annotations

from typing import Any


class InMemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value


_cache = InMemoryCache()


def get_cache() -> InMemoryCache:
    return _cache
