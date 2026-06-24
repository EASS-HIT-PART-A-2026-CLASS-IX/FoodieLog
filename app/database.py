from collections.abc import Generator
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from .config import Settings

def get_settings() -> Settings:
    return Settings()

SettingsDep = Annotated[Settings, Depends(get_settings)]

settings = get_settings()
engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False}
)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    _migrate_restaurants()
    seed_users()


def _migrate_restaurants() -> None:
    """Lightweight auto-migration: add new columns to an existing restaurants table."""
    from sqlalchemy import text
    with engine.begin() as conn:
        cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(restaurants)").fetchall()}
        if "restaurants" not in {t for t in SQLModel.metadata.tables}:
            return
        if "owner_id" not in cols:
            conn.exec_driver_sql("ALTER TABLE restaurants ADD COLUMN owner_id INTEGER")
        if "notes" not in cols:
            conn.exec_driver_sql("ALTER TABLE restaurants ADD COLUMN notes VARCHAR")
        if "is_favorite" not in cols:
            conn.exec_driver_sql("ALTER TABLE restaurants ADD COLUMN is_favorite BOOLEAN DEFAULT 0")
        if "price_level" not in cols:
            conn.exec_driver_sql("ALTER TABLE restaurants ADD COLUMN price_level INTEGER")
        if "tags" not in cols:
            conn.exec_driver_sql("ALTER TABLE restaurants ADD COLUMN tags VARCHAR")

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


# Demo accounts seeded on startup so the app is usable out of the box (Session 11).
_DEMO_USERS = [
    {"email": "admin@foodielog.com", "name": "Admin", "password": "admin123", "role": "admin"},
    {"email": "demo@foodielog.com", "name": "Demo User", "password": "demo123", "role": "user"},
]


def seed_users() -> None:
    from sqlmodel import select
    from .models import Restaurant, User
    from .security import hash_password

    with Session(engine) as session:
        for demo in _DEMO_USERS:
            exists = session.exec(select(User).where(User.email == demo["email"])).first()
            if exists:
                continue
            session.add(User(
                email=demo["email"],
                name=demo["name"],
                hashed_password=hash_password(demo["password"]),
                role=demo["role"],
            ))
        session.commit()

        # Assign any pre-existing (ownerless) restaurants to the admin account.
        admin = session.exec(select(User).where(User.role == "admin")).first()
        if admin:
            orphans = session.exec(select(Restaurant).where(Restaurant.owner_id == None)).all()  # noqa: E711
            for r in orphans:
                r.owner_id = admin.id
            if orphans:
                session.commit()