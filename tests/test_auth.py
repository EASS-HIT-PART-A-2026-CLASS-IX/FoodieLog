"""Security tests — Session 11: registration, login, 401/403/expiry paths."""
from datetime import timedelta

from app.config import Settings
from app.security import create_access_token


def test_register_creates_account_and_returns_token(client):
    response = client.post(
        "/auth/register",
        json={"name": "Tester", "email": "tester@test.com", "password": "pass123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "tester@test.com"
    assert body["user"]["role"] == "user"


def test_register_duplicate_email_returns_409(client):
    payload = {"name": "A", "email": "dup@test.com", "password": "pass123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json={**payload, "name": "B"})
    assert response.status_code == 409


def test_login_success_after_register(client):
    client.post(
        "/auth/register",
        json={"name": "Logger", "email": "logger@test.com", "password": "pass123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "logger@test.com", "password": "pass123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_form_flow_for_swagger(client):
    """The OAuth2 password form (/auth/token) uses email as the username."""
    client.post(
        "/auth/register",
        json={"name": "Form", "email": "form@test.com", "password": "pass123"},
    )
    response = client.post(
        "/auth/token",
        data={"username": "form@test.com", "password": "pass123"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    client.post(
        "/auth/register",
        json={"name": "WP", "email": "wp@test.com", "password": "pass123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "wp@test.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_login_unknown_user_returns_401(client):
    response = client.post(
        "/auth/login",
        json={"email": "ghost@test.com", "password": "x"},
    )
    assert response.status_code == 401


def test_update_account_name(auth_client):
    response = auth_client.patch("/auth/me", json={"name": "Renamed"})
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"


def test_change_password_wrong_current_returns_400(auth_client):
    response = auth_client.patch(
        "/auth/me",
        json={"current_password": "wrongpass", "new_password": "newpass123"},
    )
    assert response.status_code == 400


def test_delete_without_token_returns_401(client):
    response = client.delete("/restaurants/1")
    assert response.status_code == 401


def test_delete_others_restaurant_returns_403(client):
    """A user cannot delete a restaurant owned by someone else."""
    token_a = client.post(
        "/auth/register", json={"name": "A", "email": "a@test.com", "password": "pass123"}
    ).json()["access_token"]
    client.post(
        "/restaurants",
        json={"name": "Owned", "cuisine": "Italian", "city": "Tel Aviv", "rating": 4, "status": "Visited"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    token_b = client.post(
        "/auth/register", json={"name": "B", "email": "b@test.com", "password": "pass123"}
    ).json()["access_token"]
    response = client.delete(
        "/restaurants/1",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 403


def test_expired_token_returns_401(client):
    settings = Settings()
    token = create_access_token(
        subject="admin",
        roles=["admin"],
        settings=settings,
        expires_delta=timedelta(seconds=-1),  # already expired
    )
    response = client.delete(
        "/restaurants/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
