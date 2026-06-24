from functools import lru_cache

import redis.asyncio as aioredis


@lru_cache(maxsize=1)
def get_redis(redis_url: str) -> aioredis.Redis:
    return aioredis.from_url(redis_url, decode_responses=True)
