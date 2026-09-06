from __future__ import annotations

import logging
import time
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Thread-safe, zero-dependency in-memory TTL cache replacing Redis."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            val, expiry = entry
            if expiry and time.time() > expiry:
                self._store.pop(key, None)
                return None
            return val

    def setex(self, key: str, ttl_seconds: int, value: Any) -> None:
        with self._lock:
            expiry = time.time() + ttl_seconds
            self._store[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def mget(self, keys: list[str]) -> list[Any | None]:
        return [self.get(k) for k in keys]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


_cache_instance = InMemoryCache()


def get_cache(settings: Any = None) -> InMemoryCache:
    """Returns the application in-memory cache singleton."""
    return _cache_instance


def is_cache_available(settings: Any = None) -> bool:
    """In-memory cache is always online."""
    return True