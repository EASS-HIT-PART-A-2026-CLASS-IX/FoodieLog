from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator

class RestaurantBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    cuisine: str = Field(min_length=1, max_length=50)
    city: str = Field(min_length=1, max_length=50)
    rating: int = Field(ge=1, le=5)
    status: str = Field(default="Want to Go")

class Restaurant(RestaurantBase, table=True):
    __tablename__ = "restaurants"
    id: Optional[int] = Field(default=None, primary_key=True)

class RestaurantCreate(RestaurantBase):
    @field_validator("name", "city")
    @classmethod
    def capitalize_words(cls, v: str) -> str:
        return v.strip().title()

class RestaurantRead(RestaurantBase):
    id: int