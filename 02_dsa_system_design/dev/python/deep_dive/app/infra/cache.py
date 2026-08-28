"""Cache adapter.

In-memory TTL cache as the offline default; swap for Redis in production behind
the same ``get/set`` interface.
"""

from __future__ import annotations

import threading
import time
from typing import Any


class InMemoryCache:
    def __init__(self) -> None:
        self._data: dict[str, tuple[float | None, Any]] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        expires = time.time() + ttl if ttl else None
        with self._lock:
            self._data[key] = (expires, value)

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return default
            expires, value = entry
            if expires is not None and time.time() > expires:
                self._data.pop(key, None)
                return default
            return value

    def delete(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)


_cache: InMemoryCache | None = None


def get_cache() -> InMemoryCache:
    global _cache
    if _cache is None:
        _cache = InMemoryCache()
    return _cache
