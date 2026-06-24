from fastapi import HTTPException, Request

from app.cache import get_redis
from app.config import Settings


async def rate_limit_middleware(request: Request, call_next):
    settings = Settings()
    if settings.rate_limit_per_minute == 0 or request.client is None:
        return await call_next(request)
    try:
        redis = get_redis(settings.redis_url)
        key = f"rate:{request.client.host}:{request.url.path}"
        max_requests = settings.rate_limit_per_minute

        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, 60)

        if current > max_requests:
            raise HTTPException(status_code=429, detail="Too many requests")

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, max_requests - current))
        return response
    except HTTPException:
        raise
    except Exception:
        # Redis unavailable — fail open (no rate limiting)
        return await call_next(request)
