def test_create_restaurant(client):
    response = client.post("/restaurants", json={
        "name": "mcdonalds",
        "cuisine": "Fast Food",
        "city": "tel aviv",
        "rating": 3,
        "status": "Visited"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Mcdonalds"  # בדיקה שהוולידציה עובדת!
    assert data["city"] == "Tel Aviv"
    assert data["id"] == 1

def test_list_restaurants(client):
    client.post("/restaurants", json={"name": "Vitrina", "cuisine": "Burger", "city": "Tel Aviv", "rating": 5, "status": "Visited"})
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_restaurant(client):
    client.post("/restaurants", json={"name": "Goocha", "cuisine": "Seafood", "city": "Tel Aviv", "rating": 4, "status": "Want to Go"})
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Goocha"

def test_update_restaurant(client):
    client.post("/restaurants", json={"name": "Dominos", "cuisine": "Pizza", "city": "Rishon Lezion", "rating": 3, "status": "Want to Go"})
    response = client.put("/restaurants/1", json={
        "name": "Dominos",
        "cuisine": "Pizza",
        "city": "Rishon Lezion",
        "rating": 2, # שינוי דירוג
        "status": "Visited" # שינוי סטטוס
    })
    assert response.status_code == 200
    assert response.json()["rating"] == 2
    assert response.json()["status"] == "Visited"

def test_delete_restaurant(client):
    client.post("/restaurants", json={"name": "KFC", "cuisine": "Chicken", "city": "Rishon Lezion", "rating": 3, "status": "Visited"})
    response = client.delete("/restaurants/1")
    assert response.status_code == 204
    assert client.get("/restaurants/1").status_code == 404