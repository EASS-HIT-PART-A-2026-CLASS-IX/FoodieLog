from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext

from app.config import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    *,
    subject: str,
    settings: Settings,
    expires_delta: Optional[timedelta] = None,
    roles: Optional[list[str]] = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.jwt_expiry_minutes))
    payload = {
        "sub": subject,
        "iat": now.timestamp(),
        "exp": expire.timestamp(),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "roles": roles or ["user"],
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
