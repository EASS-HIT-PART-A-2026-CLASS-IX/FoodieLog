from typing import Annotated
from fastapi import Depends
from .database import SessionDep
from .repository import FoodieRepository

def get_repository(session: SessionDep) -> FoodieRepository:
    return FoodieRepository(session)

RepositoryDep = Annotated[FoodieRepository, Depends(get_repository)]