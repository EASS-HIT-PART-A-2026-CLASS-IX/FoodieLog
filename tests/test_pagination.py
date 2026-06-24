"""Enhancement tests — Session 12: pagination, X-Total-Count, ETag."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app


@pytest.fixture(name="populated_client")
def populated_client_fixture(tmp_path):
    db = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db}", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def override():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = override
    with TestClient(app) as c:
        token = c.post("/auth/register", json={
            "name": "Pager", "email": "pager@test.com", "password": "pass123",
        }).json()["access_token"]
        c.headers.update({"Authorization": f"Bearer {token}"})
        for i in range(5):
            c.post("/restaurants", json={
                "name": f"Restaurant {i}",
                "cuisine": "Italian",
                "city": "Tel Aviv",
                "rating": 3,
                "status": "Visited",
            })
        yield c
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


def test_list_returns_x_total_count(populated_client):
    response = populated_client.get("/restaurants?page=1&page_size=10")
    assert response.status_code == 200
    assert response.headers["X-Total-Count"] == "5"


def test_pagination_limits_results(populated_client):
    response = populated_client.get("/restaurants?page=1&page_size=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_pagination_second_page(populated_client):
    response = populated_client.get("/restaurants?page=2&page_size=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_pagination_last_page_partial(populated_client):
    response = populated_client.get("/restaurants?page=3&page_size=2")
    assert response.status_code == 200
    assert len(response.json()) == 1  # only 1 left out of 5


def test_list_returns_etag(populated_client):
    response = populated_client.get("/restaurants")
    assert "etag" in response.headers


def test_etag_returns_304_on_match(populated_client):
    r1 = populated_client.get("/restaurants")
    etag = r1.headers["etag"]
    r2 = populated_client.get("/restaurants", headers={"if-none-match": etag})
    assert r2.status_code == 304
