def test_create_restaurant(auth_client):
    response = auth_client.post("/restaurants", json={
        "name": "mcdonalds",
        "cuisine": "Fast Food",
        "city": "tel aviv",
        "rating": 3,
        "status": "Visited"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Mcdonalds"  # validation/capitalization works
    assert data["city"] == "Tel Aviv"
    assert data["id"] == 1


def test_list_restaurants(auth_client):
    auth_client.post("/restaurants", json={"name": "Vitrina", "cuisine": "Burger", "city": "Tel Aviv", "rating": 5, "status": "Visited"})
    response = auth_client.get("/restaurants")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_restaurants_returns_total_count_header(auth_client):
    auth_client.post("/restaurants", json={"name": "Vitrina", "cuisine": "Burger", "city": "Tel Aviv", "rating": 5, "status": "Visited"})
    auth_client.post("/restaurants", json={"name": "Goocha", "cuisine": "Seafood", "city": "Tel Aviv", "rating": 4, "status": "Want to Go"})
    response = auth_client.get("/restaurants")
    assert response.headers["X-Total-Count"] == "2"


def test_get_restaurant(auth_client):
    auth_client.post("/restaurants", json={"name": "Goocha", "cuisine": "Seafood", "city": "Tel Aviv", "rating": 4, "status": "Want to Go"})
    response = auth_client.get("/restaurants/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Goocha"


def test_update_restaurant(auth_client):
    auth_client.post("/restaurants", json={"name": "Dominos", "cuisine": "Pizza", "city": "Rishon Lezion", "rating": 3, "status": "Want to Go"})
    response = auth_client.put("/restaurants/1", json={
        "name": "Dominos",
        "cuisine": "Pizza",
        "city": "Rishon Lezion",
        "rating": 2,
        "status": "Visited"
    })
    assert response.status_code == 200
    assert response.json()["rating"] == 2
    assert response.json()["status"] == "Visited"


def test_create_with_notes_and_favorite(auth_client):
    response = auth_client.post("/restaurants", json={
        "name": "Taizu", "cuisine": "Asian Fusion", "city": "Tel Aviv",
        "rating": 5, "status": "Visited", "notes": "Try the pad thai", "is_favorite": True,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["notes"] == "Try the pad thai"
    assert data["is_favorite"] is True


def test_search_filters_results(auth_client):
    auth_client.post("/restaurants", json={"name": "Sushi Zen", "cuisine": "Japanese", "city": "Tel Aviv", "rating": 5, "status": "Visited"})
    auth_client.post("/restaurants", json={"name": "Pasta Roma", "cuisine": "Italian", "city": "Haifa", "rating": 4, "status": "Visited"})
    response = auth_client.get("/restaurants", params={"search": "sushi"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Sushi Zen"


def test_create_with_price_and_tags(auth_client):
    response = auth_client.post("/restaurants", json={
        "name": "Thai House", "cuisine": "Thai", "city": "Tel Aviv",
        "rating": 4, "status": "Visited", "price_level": 3, "tags": "spicy, cheap",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["price_level"] == 3
    assert data["tags"] == "spicy, cheap"


def test_delete_restaurant(auth_client):
    """An owner can delete their own restaurant."""
    auth_client.post("/restaurants", json={"name": "KFC", "cuisine": "Chicken", "city": "Rishon Lezion", "rating": 3, "status": "Visited"})
    response = auth_client.delete("/restaurants/1")
    assert response.status_code == 204
    assert auth_client.get("/restaurants/1").status_code == 404
