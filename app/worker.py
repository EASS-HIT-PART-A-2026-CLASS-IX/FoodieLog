from arq import cron
from arq.connections import RedisSettings

from app.config import Settings


async def startup(ctx: dict) -> None:
    ctx["settings"] = Settings()


async def shutdown(ctx: dict) -> None:
    ctx.pop("settings", None)


async def refresh_restaurants(ctx: dict) -> str:
    """Background job: update Redis heartbeat to signal worker is alive."""
    settings: Settings = ctx["settings"]
    from app.cache import get_redis
    redis = get_redis(settings.redis_url)
    await redis.set("worker:last_run", "ok", ex=3600)
    return "refreshed"


class WorkerSettings:
    redis_settings = RedisSettings.from_url(Settings().redis_url)
    functions = [refresh_restaurants]
    on_startup = startup
    on_shutdown = shutdown
    cron_jobs = [cron(refresh_restaurants, hour={0, 6, 12, 18})]
