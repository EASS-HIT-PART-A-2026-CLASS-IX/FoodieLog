from typing import Optional
from sqlmodel import Session, select
from .models import Restaurant, RestaurantCreate


class FoodieRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, *, skip: int = 0, limit: int = 100) -> list[Restaurant]:
        statement = select(Restaurant).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def create(self, payload: RestaurantCreate) -> Restaurant:
        db_restaurant = Restaurant.model_validate(payload)
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