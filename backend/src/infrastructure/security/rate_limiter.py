from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from src.config import Settings, get_settings


class RateLimiter:
    """In-memory sliding-window rate limiter (zero Redis dependency)."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        """Check if request under `key` is allowed within `window_seconds`."""
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        with self._lock:
            # Purge timestamps older than the sliding window
            timestamps = [t for t in self._requests[key] if t > cutoff_time]
            if len(timestamps) >= max_requests:
                self._requests[key] = timestamps
                return False

            timestamps.append(current_time)
            self._requests[key] = timestamps
            return True