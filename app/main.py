from fastapi import FastAPI, HTTPException, status
from .database import SettingsDep, init_db
from .models import RestaurantCreate, RestaurantRead
from .dependencies import RepositoryDep
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="FoodieLog API", version="2.0.0", lifespan=lifespan)

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