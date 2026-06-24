from contextlib import asynccontextmanager
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from .database import SettingsDep, get_settings, init_db
from .dependencies import RepositoryDep
from .models import RestaurantCreate, RestaurantRead, User
from .pagination import Page, compute_etag, maybe_not_modified, pagination_params
from .rate_limit import rate_limit_middleware
from .routers import ai, auth
from .routers.auth import get_current_user
from .config import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def require_role(*allowed_roles: str):
    """FastAPI dependency that validates JWT and checks role membership (Session 11)."""
    def _inner(
        token: str = Security(oauth2_scheme),
        settings: Settings = Depends(get_settings),
    ) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=["HS256"],
                audience=settings.jwt_audience,
                issuer=settings.jwt_issuer,
            )
        except jwt.PyJWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from exc

        roles = set(payload.get("roles", []))
        if not roles.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return payload

    return _inner


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="FoodieLog API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate-limit middleware — fails open when Redis is unavailable (Session 10)
app.middleware("http")(rate_limit_middleware)

# Auth router — POST /auth/token (Session 11)
app.include_router(auth.router)

# AI assistant router — POST /ai/chat
app.include_router(ai.router)


@app.get("/health", tags=["diagnostics"])
def health_check(settings: SettingsDep):
    return {"status": "ok", "app": settings.app_name}


CurrentUserDep = Annotated[User, Depends(get_current_user)]


@app.get("/restaurants", response_model=list[RestaurantRead], tags=["restaurants"])
def list_restaurants(
    request: Request,
    response: Response,
    repository: RepositoryDep,
    current_user: CurrentUserDep,
    page: Annotated[Page, Depends(pagination_params)],
    search: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
):
    """List the current user's restaurants — paginated, searchable, sortable, ETag-cached."""
    items, total = repository.list_paginated(
        current_user.id, page.number, page.size, search, sort_by, order
    )
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Total-Pages"] = str((total + page.size - 1) // page.size if page.size else 1)

    data = [r.model_dump() for r in items]
    etag = compute_etag(data)
    if maybe_not_modified(request, response, etag):
        return Response(status_code=304, headers={"ETag": etag})

    return items


@app.post(
    "/restaurants",
    response_model=RestaurantRead,
    status_code=status.HTTP_201_CREATED,
    tags=["restaurants"],
)
def create_restaurant(payload: RestaurantCreate, repository: RepositoryDep, current_user: CurrentUserDep):
    return repository.create(payload, current_user.id)


@app.get("/restaurants/{restaurant_id}", response_model=RestaurantRead, tags=["restaurants"])
def get_restaurant(restaurant_id: int, repository: RepositoryDep, current_user: CurrentUserDep):
    restaurant = repository.get(restaurant_id)
    if not restaurant or restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not found")
    return restaurant


@app.put("/restaurants/{restaurant_id}", response_model=RestaurantRead, tags=["restaurants"])
def update_restaurant(
    restaurant_id: int, payload: RestaurantCreate, repository: RepositoryDep, current_user: CurrentUserDep
):
    existing = repository.get(restaurant_id)
    if not existing or existing.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not found")
    return repository.update(restaurant_id, payload)


@app.delete(
    "/restaurants/{restaurant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["restaurants"],
)
def delete_restaurant(restaurant_id: int, repository: RepositoryDep, current_user: CurrentUserDep):
    """Delete a restaurant — owner only (admins may delete any). Session 11."""
    existing = repository.get(restaurant_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Not found")
    if existing.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only delete your own restaurants")
    repository.delete(restaurant_id)
