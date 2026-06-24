from __future__ import annotations

from typing import Optional
from sqlmodel import Session, func, select
from .models import Restaurant, RestaurantCreate


class FoodieRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    _SORT_COLUMNS = {
        "id": Restaurant.id,
        "name": Restaurant.name,
        "rating": Restaurant.rating,
        "city": Restaurant.city,
        "cuisine": Restaurant.cuisine,
        "price_level": Restaurant.price_level,
    }

    def list(self, *, owner_id: int, skip: int = 0, limit: int = 100) -> list[Restaurant]:
        statement = select(Restaurant).where(Restaurant.owner_id == owner_id).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def list_paginated(
        self,
        owner_id: int,
        page: int,
        page_size: int,
        search: str | None = None,
        sort_by: str = "id",
        order: str = "asc",
    ) -> tuple[list[Restaurant], int]:
        """Return one page of the owner's restaurants plus the total count (Session 12)."""
        base = select(Restaurant).where(Restaurant.owner_id == owner_id)
        count_q = select(func.count()).select_from(Restaurant).where(Restaurant.owner_id == owner_id)

        if search:
            like = f"%{search}%"
            cond = (
                Restaurant.name.ilike(like)
                | Restaurant.cuisine.ilike(like)
                | Restaurant.city.ilike(like)
                | Restaurant.tags.ilike(like)
            )
            base = base.where(cond)
            count_q = count_q.where(cond)

        total = self.session.exec(count_q).one()

        col = self._SORT_COLUMNS.get(sort_by, Restaurant.id)
        base = base.order_by(col.desc() if order == "desc" else col.asc())

        offset = (page - 1) * page_size
        items = list(self.session.exec(base.offset(offset).limit(page_size)).all())
        return items, total

    def create(self, payload: RestaurantCreate, owner_id: int) -> Restaurant:
        db_restaurant = Restaurant.model_validate(payload)
        db_restaurant.owner_id = owner_id
        self.session.add(db_restaurant)
        self.session.commit()
        self.session.refresh(db_restaurant)
        return db_restaurant

    def get(self, restaurant_id: int) -> Optional[Restaurant]:
        return self.session.get(Restaurant, restaurant_id)

    def update(self, restaurant_id: int, payload: RestaurantCreate) -> Optional[Restaurant]:
        db_restaurant = self.get(restaurant_id)
        if not db_restaurant:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_restaurant, key, value)

        self.session.add(db_restaurant)
        self.session.commit()
        self.session.refresh(db_restaurant)
        return db_restaurant

    def delete(self, restaurant_id: int) -> bool:
        db_restaurant = self.get(restaurant_id)
        if not db_restaurant:
            return False
        self.session.delete(db_restaurant)
        self.session.commit()
        return True