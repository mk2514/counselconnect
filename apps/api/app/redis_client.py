"""
Redis connection management.
"""

from collections.abc import AsyncIterator
from typing import Any

import redis.asyncio as aioredis

from app.config import settings

redis_pool: Any = aioredis.from_url(
    settings.redis_url,
    decode_responses=True,
)


async def get_redis() -> AsyncIterator[Any]:
    """Dependency that yields a Redis connection."""
    yield redis_pool
