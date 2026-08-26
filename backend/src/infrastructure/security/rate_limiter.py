from __future__ import annotations

import time
from src.config import Settings, get_settings
from src.infrastructure.cache.redis_client import get_redis_client


class RateLimiter:
    """Sliding-window rate limiter utilizing Redis."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        """Check if request under `key` is allowed within `window_seconds`."""
        client = get_redis_client(self._settings)
        if client is None:
            # Graceful fallback: allow request if Redis is unavailable
            return True

        current_time = time.time()
        cutoff_time = current_time - window_seconds
        redis_key = f"ratelimit:{key}"

        try:
            pipe = client.pipeline()
            # Remove timestamps outside window
            pipe.zremrangebyscore(redis_key, 0, cutoff_time)
            # Count requests in window
            pipe.zcard(redis_key)
            # Add current timestamp
            pipe.zadd(redis_key, {str(current_time): current_time})
            # Set key expiry
            pipe.expire(redis_key, window_seconds + 5)
            results = pipe.execute()

            request_count = results[1]
            return bool(request_count < max_requests)
        except Exception:
            # Fallback to allow if Redis operation fails
            return True