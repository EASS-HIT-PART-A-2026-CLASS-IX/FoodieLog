from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .database import SettingsDep, init_db
from .dependencies import RepositoryDep
from .models import RestaurantCreate, RestaurantRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="FoodieLog API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["diagnostics"])
def health_check(settings: SettingsDep):
    return {"status": "ok", "app": settings.app_name}

@app.get("/restaurants", response_model=list[RestaurantRead], tags=["restaurants"])
def list_restaurants(repository: RepositoryDep):
    return repository.list()

@app.post("/restaurants", response_model=RestaurantRead, status_code=status.HTTP_201_CREATED, tags=["restaurants"])
def create_restaurant(payload: RestaurantCreate, repository: RepositoryDep):
    return repository.create(payload)

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantRead, tags=["restaurants"])
def get_restaurant(restaurant_id: int, repository: RepositoryDep):
    restaurant = repository.get(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Not found")
    return restaurant

@app.put("/restaurants/{restaurant_id}", response_model=RestaurantRead, tags=["restaurants"])
def update_restaurant(restaurant_id: int, payload: RestaurantCreate, repository: RepositoryDep):
    updated = repository.update(restaurant_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated

@app.delete("/restaurants/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["restaurants"])
def delete_restaurant(restaurant_id: int, repository: RepositoryDep):
    if not repository.delete(restaurant_id):
        raise HTTPException(status_code=404, detail="Not found")