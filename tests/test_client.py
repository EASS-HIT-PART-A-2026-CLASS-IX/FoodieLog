"""
Bonus: automated tests for the frontend HTTP client (frontend/client.py).
Each test patches the httpx.Client so no live server is required.
"""
from unittest.mock import MagicMock, patch

import pytest

from frontend.client import _client, create_restaurant, delete_restaurant, list_restaurants


@pytest.fixture(autouse=True)
def reset_client_cache():
    """Clear the lru_cache before each test so a fresh mock is used every time."""
    _client.cache_clear()
    yield
    _client.cache_clear()


def _mock_response(json_data, status_code: int = 200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


# ── list_restaurants ──────────────────────────────────────────────────────────

def test_list_restaurants_returns_list():
    sample = [
        {"id": 1, "name": "Pasta Roma", "cuisine": "Italian", "city": "Tel Aviv", "rating": 5, "status": "Visited"},
        {"id": 2, "name": "Sushi Zen",  "cuisine": "Japanese","city": "Tel Aviv", "rating": 4, "status": "Want to Go"},
    ]
    with patch("frontend.client.httpx.Client") as MockClient:
        MockClient.return_value.get.return_value = _mock_response(sample)
        result = list_restaurants("tok")

    assert len(result) == 2
    assert result[0]["name"] == "Pasta Roma"


def test_list_restaurants_empty():
    with patch("frontend.client.httpx.Client") as MockClient:
        MockClient.return_value.get.return_value = _mock_response([])
        result = list_restaurants("tok")

    assert result == []


# ── create_restaurant ─────────────────────────────────────────────────────────

def test_create_restaurant_returns_new_entry():
    payload = {"id": 3, "name": "Le Bistro", "cuisine": "French", "city": "Tel Aviv", "rating": 5, "status": "Want to Go"}
    with patch("frontend.client.httpx.Client") as MockClient:
        MockClient.return_value.post.return_value = _mock_response(payload, status_code=201)
        result = create_restaurant("tok", name="Le Bistro", cuisine="French", city="Tel Aviv", rating=5, status="Want to Go")

    assert result["id"] == 3
    assert result["cuisine"] == "French"


def test_create_restaurant_sends_correct_body():
    payload = {"id": 4, "name": "Taco Fiesta", "cuisine": "Mexican", "city": "Eilat", "rating": 3, "status": "Want to Go"}
    with patch("frontend.client.httpx.Client") as MockClient:
        mock_post = MockClient.return_value.post
        mock_post.return_value = _mock_response(payload, status_code=201)
        create_restaurant("tok", name="Taco Fiesta", cuisine="Mexican", city="Eilat", rating=3, status="Want to Go")

    _, kwargs = mock_post.call_args
    body = kwargs["json"]
    assert body["name"] == "Taco Fiesta"
    assert body["rating"] == 3


# ── delete_restaurant ─────────────────────────────────────────────────────────

def test_delete_restaurant_calls_correct_endpoint():
    with patch("frontend.client.httpx.Client") as MockClient:
        mock_delete = MockClient.return_value.delete
        mock_delete.return_value = _mock_response(None, status_code=204)
        mock_delete.return_value.raise_for_status.return_value = None
        delete_restaurant(7, "tok")

    args, _ = mock_delete.call_args
    assert args[0] == "/restaurants/7"
