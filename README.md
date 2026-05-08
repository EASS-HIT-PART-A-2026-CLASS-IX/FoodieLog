# FoodieLog

FoodieLog is a full-stack application for tracking restaurants, cafes, and foodie experiences. It allows users to maintain a wishlist of places to eat, rate the ones they've visited, and manage everything through a Streamlit dashboard connected to a REST API.

Built with **FastAPI**, **Pydantic**, **SQLModel**, **Streamlit**, and **pytest**.

## Setup & Environment
This project uses `uv` as the fast package and environment manager.
To initialize the environment and install all dependencies from the `uv.lock` file, open your terminal and run:
```bash
uv sync
```

## Database Initialization (Alembic)
Before running the app for the first time, you must apply the database migrations to create the local SQLite database (`data/foodie.db`):
```bash
uv run alembic upgrade head
```

## Running the API Locally
To start the FastAPI server with live-reloading, run:
```bash
uv run uvicorn app.main:app --reload
```
Once the server is running, you can access the interactive API documentation (Swagger UI) at:
**http://127.0.0.1:8000/docs**

## API Endpoints Overview
The API provides a complete set of CRUD operations for the core resource:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/health` | Diagnostics check to ensure the API is running. |
| **GET** | `/restaurants` | List all saved restaurants. |
| **POST** | `/restaurants` | Create and save a new restaurant. |
| **GET** | `/restaurants/{id}` | Retrieve a specific restaurant by its ID. |
| **PUT** | `/restaurants/{id}` | Update an existing restaurant's details. |
| **DELETE** | `/restaurants/{id}` | Delete a restaurant from the database. |

## Streamlit Dashboard
FoodieLog includes a Streamlit dashboard (`frontend/dashboard.py`) that connects to the API and lets you manage your restaurant list through a browser interface.

### Dashboard Features
- **List** all restaurants with live filters by status, cuisine, and rating range
- **Add** a new restaurant via an inline form
- **Mark as Visited** — one-click status update for any "Want to Go" entry
- **Delete** an entry directly from the UI
- **Summary metrics** — total restaurants, visited count, wishlist count, and average rating
- **Export to CSV** — download the currently filtered list with one click

### Running the API and Dashboard Side-by-Side
Open **two terminals** in the project directory.

**Terminal 1 — FastAPI backend:**
```bash
uv run uvicorn app.main:app --reload
```
The API will be available at **http://localhost:8000**.

**Terminal 2 — Streamlit dashboard:**
```bash
uv run streamlit run frontend/dashboard.py
```
The dashboard will open automatically at **http://localhost:8501**.

Both servers must be running at the same time. The dashboard communicates with the API over HTTP and never accesses the database directly.

## Executing the Tests
The test suite uses `pytest` and `TestClient` to verify all CRUD operations and the frontend HTTP client. Backend tests run in perfect isolation — a custom pytest fixture spins up a temporary SQLite database, overrides the FastAPI dependencies, and drops the tables after execution to ensure tests never mutate the real database. Frontend client tests use mocking so no live server is required.
```bash
uv run pytest tests/ -v
```
