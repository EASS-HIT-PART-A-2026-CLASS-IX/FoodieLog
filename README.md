# EX1 - FoodieLog API

FoodieLog is a core backend microservice for tracking restaurants, cafes, and foodie experiences. It allows users to maintain a wishlist of places to eat and rate the ones they've visited. 

Built with **FastAPI**, **Pydantic**, and **pytest**.
*Upgrade Note:* The persistence layer has been fully upgraded to use **SQLite** and **SQLModel**, with database migrations managed by **Alembic**.

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

## Endpoints Overview
The API provides a complete set of CRUD operations for the core resource:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/health` | Diagnostics check to ensure the API is running. |
| **GET** | `/restaurants` | List all saved restaurants. |
| **POST** | `/restaurants` | Create and save a new restaurant. |
| **GET** | `/restaurants/{id}` | Retrieve a specific restaurant by its ID. |
| **PUT** | `/restaurants/{id}` | Update an existing restaurant's details. |
| **DELETE**| `/restaurants/{id}` | Delete a restaurant from the database. |

## Executing the Tests
The test suite uses `pytest` and `TestClient` to verify the CRUD operations. Each test runs in perfect isolation (Hermetic Tests). A custom pytest fixture spins up a temporary SQLite database, overrides the FastAPI dependencies, and drops the tables after execution to ensure tests never mutate the real database.
```bash
uv run pytest tests/ -v
```

## AI Assistance
This project was developed with the assistance of AI. It was used to brainstorm an original concept, scaffold the FastAPI routes, generate the Pydantic/SQLModel models with custom string normalization, and build the Pytest suite. Additionally, AI was used to help transition the architecture from an in-memory dictionary to a persistent SQLite database, including setting up the Alembic workflow and migration scripts. All AI-generated code was verified locally by running `pytest` and testing the Swagger UI manually.