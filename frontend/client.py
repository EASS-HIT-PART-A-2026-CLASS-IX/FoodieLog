from __future__ import annotations

from functools import lru_cache
from typing import Any

import httpx

API_BASE_URL = "http://localhost:8000"


@lru_cache(maxsize=1)
def _client() -> httpx.Client:
    return httpx.Client(base_url=API_BASE_URL, timeout=5.0)


def list_restaurants() -> list[dict[str, Any]]:
    response = _client().get("/restaurants")
    response.raise_for_status()
    return response.json()


def create_restaurant(*, name: str, cuisine: str, city: str, rating: int, status: str) -> dict[str, Any]:
    response = _client().post(
        "/restaurants",
        json={"name": name, "cuisine": cuisine, "city": city, "rating": rating, "status": status},
    )
    response.raise_for_status()
    return response.json()


def delete_restaurant(restaurant_id: int) -> None:
    response = _client().delete(f"/restaurants/{restaurant_id}")
    response.raise_for_status()


def update_restaurant(restaurant_id: int, *, name: str, cuisine: str, city: str, rating: int, status: str) -> dict[str, Any]:
    response = _client().put(
        f"/restaurants/{restaurant_id}",
        json={"name": name, "cuisine": cuisine, "city": city, "rating": rating, "status": status},
    )
    response.raise_for_status()
    return response.json()
