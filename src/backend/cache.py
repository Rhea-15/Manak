import json
import logging
import os

import redis

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_client = None


def get_redis_client():
    """Return a reusable Redis client with short connection timeouts."""
    global _client

    if _client is None:
        _client = redis.Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
            health_check_interval=30,
        )

    return _client


def cache_get(key: str):
    """Return a cached JSON value, or None if unavailable or missing."""
    try:
        value = get_redis_client().get(key)

        if value is None:
            return None

        return json.loads(value)

    except (redis.RedisError, json.JSONDecodeError, TypeError, ValueError):
        logger.warning("Redis cache read failed for key %s", key)
        return None


def cache_set(key: str, value, ttl: int = 60) -> bool:
    """Store a JSON-serializable value with a TTL."""
    try:
        serialized = json.dumps(value, default=str)

        get_redis_client().setex(
            key,
            ttl,
            serialized,
        )

        return True

    except (redis.RedisError, TypeError, ValueError):
        logger.warning("Redis cache write failed for key %s", key)
        return False


def cache_delete(key: str) -> bool:
    """Delete a cache entry."""
    try:
        get_redis_client().delete(key)
        return True

    except redis.RedisError:
        logger.warning("Redis cache deletion failed for key %s", key)
        return False


def cache_delete_pattern(pattern: str) -> bool:
    """Delete keys matching a pattern, such as manak:graph:*."""
    try:
        client = get_redis_client()

        for key in client.scan_iter(match=pattern, count=100):
            client.delete(key)

        return True

    except redis.RedisError:
        logger.warning("Redis cache invalidation failed for %s", pattern)
        return False
