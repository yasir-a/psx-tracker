from __future__ import annotations

import logging
from typing import Any
import redis
from redis.exceptions import ConnectionError, TimeoutError

from src.config import Settings, get_settings

logger = logging.getLogger(__name__)
_redis_client: redis.Redis | None = None


def get_redis_client(settings: Settings | None = None) -> redis.Redis | None:
    """Retrieve or initialize the Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        cfg = settings or get_settings()
        try:
            _redis_client = redis.Redis.from_url(
                cfg.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1.0,
                socket_timeout=1.0,
            )
        except Exception as e:
            logger.warning("Failed to initialize Redis client: %s", str(e))
            return None
    return _redis_client


def is_redis_available(settings: Settings | None = None) -> bool:
    """Check if Redis connection is alive."""
    client = get_redis_client(settings)
    if client is None:
        return False
    try:
        return bool(client.ping())
    except (ConnectionError, TimeoutError, Exception) as e:
        logger.debug("Redis ping failed: %s", str(e))
        return False