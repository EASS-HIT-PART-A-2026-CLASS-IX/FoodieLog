from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import httpx

# Read from the environment so Docker Compose can point the frontend at the
# `api` service (FOODIE_API_BASE_URL=http://api:8000); falls back to localhost.
API_BASE_URL = os.environ.get("FOODIE_API_BASE_URL", "http://localhost:8000")


@lru_cache(maxsize=1)
def _client() -> httpx.Client:
    return httpx.Client(base_url=API_BASE_URL, timeout=5.0)


def login(email: str, password: str) -> dict[str, Any]:
    """Authenticate with email + password. Returns {access_token, token_type, user}."""
    response = _client().post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    response.raise_for_status()
    return response.json()


def register(name: str, email: str, password: str) -> dict[str, Any]:
    """Create a new account. Returns {access_token, token_type, user}."""
    response = _client().post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    if response.status_code == 409:
        raise ValueError("An account with that email already exists.")
    response.raise_for_status()
    return response.json()


def update_account(token: str, *, name: str | None = None,
                   current_password: str | None = None, new_password: str | None = None) -> dict[str, Any]:
    """Update display name and/or password. Returns the updated user."""
    body: dict[str, Any] = {}
    if name:
        body["name"] = name
    if new_password:
        body["current_password"] = current_password
        body["new_password"] = new_password
    response = _client().patch("/auth/me", json=body, headers=_auth(token))
    if response.status_code == 400:
        raise ValueError(response.json().get("detail", "Update failed."))
    response.raise_for_status()
    return response.json()


def ai_recommend(token: str) -> dict[str, Any]:
    """Ask the AI for a new restaurant suggestion. Returns {name, cuisine, city, reason}."""
    response = _client().post("/ai/recommend", headers=_auth(token), timeout=60.0)
    if response.status_code == 503:
        raise ValueError("AI is not configured on the server (missing API key).")
    response.raise_for_status()
    return response.json()


def chat(message: str, token: str) -> str:
    """Send a message to the AI assistant. Returns the reply text."""
    response = _client().post(
        "/ai/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {token}"},
        timeout=60.0,
    )
    if response.status_code == 503:
        raise ValueError("AI is not configured on the server (missing API key).")
    response.raise_for_status()
    return response.json()["reply"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def list_restaurants(
    token: str,
    *,
    search: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
    page_size: int = 100,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"page_size": page_size, "sort_by": sort_by, "order": order}
    if search:
        params["search"] = search
    response = _client().get("/restaurants", params=params, headers=_auth(token))
    response.raise_for_status()
    return response.json()


def create_restaurant(
    token: str, *, name: str, cuisine: str, city: str, rating: int, status: str,
    notes: str | None = None, is_favorite: bool = False,
    price_level: int | None = None, tags: str | None = None,
) -> dict[str, Any]:
    response = _client().post(
        "/restaurants",
        json={"name": name, "cuisine": cuisine, "city": city, "rating": rating,
              "status": status, "notes": notes, "is_favorite": is_favorite,
              "price_level": price_level, "tags": tags},
        headers=_auth(token),
    )
    response.raise_for_status()
    return response.json()


def delete_restaurant(restaurant_id: int, token: str) -> None:
    response = _client().delete(f"/restaurants/{restaurant_id}", headers=_auth(token))
    response.raise_for_status()


def update_restaurant(
    restaurant_id: int, token: str, *, name: str, cuisine: str, city: str, rating: int, status: str,
    notes: str | None = None, is_favorite: bool = False,
    price_level: int | None = None, tags: str | None = None,
) -> dict[str, Any]:
    response = _client().put(
        f"/restaurants/{restaurant_id}",
        json={"name": name, "cuisine": cuisine, "city": city, "rating": rating,
              "status": status, "notes": notes, "is_favorite": is_favorite,
              "price_level": price_level, "tags": tags},
        headers=_auth(token),
    )
    response.raise_for_status()
    return response.json()
