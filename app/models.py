from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator

class RestaurantBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    cuisine: str = Field(min_length=1, max_length=50)
    city: str = Field(min_length=1, max_length=50)
    rating: int = Field(ge=1, le=5)
    status: str = Field(default="Want to Go")
    notes: Optional[str] = Field(default=None, max_length=500)
    is_favorite: bool = Field(default=False)
    price_level: Optional[int] = Field(default=None, ge=1, le=4)
    tags: Optional[str] = Field(default=None, max_length=200)

class Restaurant(RestaurantBase, table=True):
    __tablename__ = "restaurants"
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)

class RestaurantCreate(RestaurantBase):
    @field_validator("name", "city")
    @classmethod
    def capitalize_words(cls, v: str) -> str:
        return v.strip().title()

class RestaurantRead(RestaurantBase):
    id: int


# ── Users / Auth (Session 11) ─────────────────────────────────────────────────

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=120)
    name: str = Field(min_length=1, max_length=80)
    hashed_password: str
    role: str = Field(default="user", max_length=20)

class UserRegister(SQLModel):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Please enter a valid email address.")
        return v

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip()

class UserLogin(SQLModel):
    email: str
    password: str

class UserRead(SQLModel):
    id: int
    email: str
    name: str
    role: str

class UserUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(default=None, min_length=6, max_length=128)

class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


# ── AI assistant ──────────────────────────────────────────────────────────────

class ChatRequest(SQLModel):
    message: str = Field(min_length=1, max_length=2000)

class ChatResponse(SQLModel):
    reply: str

class Recommendation(SQLModel):
    name: str
    cuisine: str
    city: str
    reason: str
