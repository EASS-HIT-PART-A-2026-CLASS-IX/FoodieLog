"""
Async restaurant-status refresh — Session 09.

Demonstrates:
  - bounded concurrency via asyncio.Semaphore
  - retries with exponential jitter via tenacity
  - Redis-backed idempotency keys
  - pytest.mark.anyio coverage (see tests/test_refresh.py)

Usage:
    uv run python scripts/refresh.py run --limit 5
    uv run python scripts/refresh.py run --limit 5 --clear
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Iterable

import httpx
import redis.asyncio as aioredis
import typer
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from app.config import Settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("refresh")

cli = typer.Typer(help="Async restaurant-status refresh")


@dataclass
class RefreshJob:
    restaurant_id: int


class RestaurantRefresher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._semaphore = asyncio.Semaphore(settings.refresh_max_concurrency)
        self._token: str | None = None

    async def _login(self, client: httpx.AsyncClient) -> None:
        """Authenticate once so refresh calls carry a valid JWT (Session 11)."""
        try:
            resp = await client.post(
                "/auth/login",
                json={
                    "email": self.settings.refresh_user_email,
                    "password": self.settings.refresh_user_password,
                },
            )
            resp.raise_for_status()
            self._token = resp.json()["access_token"]
            log.info("Authenticated as %s", self.settings.refresh_user_email)
        except httpx.HTTPError as exc:
            log.warning("Refresh login failed (%s) — proceeding unauthenticated", exc)

    async def refresh(self, jobs: Iterable[RefreshJob]) -> None:
        job_list = list(jobs)
        log.info("Starting refresh: %d jobs (concurrency=%d)", len(job_list), self.settings.refresh_max_concurrency)
        async with httpx.AsyncClient(base_url=self.settings.api_base_url, timeout=10.0) as client:
            await self._login(client)
            await asyncio.gather(*[self._bounded_refresh(client, job) for job in job_list])
        log.info("Refresh complete")

    async def _bounded_refresh(self, client: httpx.AsyncClient, job: RefreshJob) -> None:
        async with self._semaphore:
            r = aioredis.from_url(self.settings.redis_url, decode_responses=True)
            try:
                key = f"refresh:restaurant:{job.restaurant_id}"

                # Idempotency guard — skip if already processed this run
                if await r.get(key):
                    log.info("[skip] restaurant %d already refreshed (idempotency)", job.restaurant_id)
                    return

                async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential_jitter(initial=0.5, max=5.0),
                    retry=retry_if_exception_type(httpx.HTTPError),
                ):
                    with attempt:
                        await self._send(client, job, key)

                await r.setex(key, 3600, "ok")
                log.info("[ok] restaurant %d refreshed  key=%s", job.restaurant_id, key)
            finally:
                await r.aclose()

    async def _send(self, client: httpx.AsyncClient, job: RefreshJob, key: str) -> None:
        headers = {
            "X-Trace-Id": self.settings.trace_id,
            "Idempotency-Key": key,
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        response = await client.get(f"/restaurants/{job.restaurant_id}", headers=headers)
        response.raise_for_status()


@cli.command()
def run(
    limit: int = typer.Option(10, help="Number of restaurant IDs to probe"),
    clear: bool = typer.Option(False, help="Clear Redis idempotency keys before running"),
) -> None:
    """Refresh restaurant statuses asynchronously with retries and Redis idempotency."""
    settings = Settings()

    async def _main() -> None:
        if clear:
            r = aioredis.from_url(settings.redis_url, decode_responses=True)
            keys = await r.keys("refresh:restaurant:*")
            if keys:
                await r.delete(*keys)
                log.info("Cleared %d idempotency keys", len(keys))
            await r.aclose()

        jobs = [RefreshJob(restaurant_id=i) for i in range(1, limit + 1)]
        await RestaurantRefresher(settings).refresh(jobs)

    asyncio.run(_main())


if __name__ == "__main__":
    cli()
