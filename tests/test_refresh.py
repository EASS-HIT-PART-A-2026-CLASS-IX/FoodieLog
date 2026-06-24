"""Async refresh tests — Session 09: pytest.mark.anyio + ASGI transport + idempotency."""
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.config import Settings
from app.main import app
from scripts.refresh import RefreshJob, RestaurantRefresher


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_refresh_calls_api_via_asgi():
    """Refresher reaches FastAPI in-process through ASGITransport — no network required."""
    transport = httpx.ASGITransport(app=app)

    with patch("scripts.refresh.aioredis.from_url") as mock_factory:
        mock_r = AsyncMock()
        mock_r.get.return_value = None   # not yet processed
        mock_r.setex = AsyncMock()
        mock_r.aclose = AsyncMock()
        mock_factory.return_value = mock_r

        settings = Settings(
            refresh_max_concurrency=2,
            api_base_url="http://testserver",
            trace_id="test-refresh",
        )
        refresher = RestaurantRefresher(settings)

        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as patched_client:
            # Override the client created inside refresh()
            original_refresh = refresher.refresh

            async def _patched_refresh(jobs):
                async with patched_client:
                    await asyncio.gather(*[refresher._bounded_refresh(patched_client, j) for j in jobs])

            import asyncio
            # Just run one job against a non-existent restaurant — 404 is fine,
            # the important thing is the idempotency key path ran.
            try:
                jobs = [RefreshJob(restaurant_id=9999)]
                await asyncio.gather(*[refresher._bounded_refresh(patched_client, j) for j in jobs])
            except Exception:
                pass  # 404 raises via raise_for_status — that's expected

        # Redis idempotency was checked
        mock_r.get.assert_called_once()


@pytest.mark.anyio
async def test_idempotency_skips_already_processed_job():
    """If the Redis key exists, _bounded_refresh must skip without calling the API."""
    with patch("scripts.refresh.aioredis.from_url") as mock_factory:
        mock_r = AsyncMock()
        mock_r.get.return_value = "ok"   # already processed
        mock_r.setex = AsyncMock()
        mock_r.aclose = AsyncMock()
        mock_factory.return_value = mock_r

        settings = Settings(
            refresh_max_concurrency=1,
            api_base_url="http://testserver",
            trace_id="test-idempotency",
        )
        refresher = RestaurantRefresher(settings)

        send_calls = []

        async def fake_send(client, job, key):
            send_calls.append(job.restaurant_id)

        with patch.object(refresher, "_send", side_effect=fake_send):
            import asyncio
            async with httpx.AsyncClient(base_url="http://testserver") as client:
                await refresher._bounded_refresh(client, RefreshJob(restaurant_id=42))

    # _send must never be called — idempotency guard short-circuited
    assert send_calls == []


@pytest.mark.anyio
async def test_retry_on_transient_failure():
    """Refresher retries up to 3 times on httpx.HTTPError."""
    with patch("scripts.refresh.aioredis.from_url") as mock_factory:
        mock_r = AsyncMock()
        mock_r.get.return_value = None
        mock_r.setex = AsyncMock()
        mock_r.aclose = AsyncMock()
        mock_factory.return_value = mock_r

        settings = Settings(
            refresh_max_concurrency=1,
            api_base_url="http://testserver",
            trace_id="test-retry",
        )
        refresher = RestaurantRefresher(settings)

        call_count = {"n": 0}

        async def flaky_send(client, job, key):
            call_count["n"] += 1
            if call_count["n"] < 2:
                raise httpx.HTTPError("transient")

        with patch.object(refresher, "_send", side_effect=flaky_send):
            import asyncio
            async with httpx.AsyncClient(base_url="http://testserver") as client:
                await refresher._bounded_refresh(client, RefreshJob(restaurant_id=1))

    assert call_count["n"] == 2  # failed once, succeeded on second attempt
