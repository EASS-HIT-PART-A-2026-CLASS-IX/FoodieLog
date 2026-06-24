from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select

from app.config import Settings
from app.database import get_settings, SessionDep
from app.models import TokenResponse, User, UserLogin, UserRead, UserRegister, UserUpdate
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
    token: str = Security(oauth2_scheme),
    session: SessionDep = None,
    settings: Settings = Depends(get_settings),
) -> User:
    """Decode the JWT and load the matching user (sub = email)."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
    )
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except jwt.PyJWTError as exc:
        raise credentials_error from exc

    email = payload.get("sub")
    if not email:
        raise credentials_error
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def _roles_for(user: User) -> list[str]:
    """Admins implicitly hold the user role too (Session 11)."""
    return ["admin", "user"] if user.role == "admin" else ["user"]


def _issue_token(user: User, settings: Settings) -> str:
    return create_access_token(
        subject=user.email,
        roles=_roles_for(user),
        settings=settings,
        expires_delta=timedelta(minutes=settings.jwt_expiry_minutes),
    )


def _token_response(user: User, settings: Settings) -> TokenResponse:
    return TokenResponse(
        access_token=_issue_token(user, settings),
        user=UserRead(id=user.id, email=user.email, name=user.name, role=user.role),
    )


def _get_by_email(session: SessionDep, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email.strip().lower())).first()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    body: UserRegister,
    session: SessionDep,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    """Create a new account and return a JWT (Session 11)."""
    if _get_by_email(session, body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists.",
        )
    user = User(
        email=body.email,
        name=body.name,
        hashed_password=hash_password(body.password),
        role="user",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return _token_response(user, settings)


@router.post("/login", response_model=TokenResponse)
def login_json(
    body: UserLogin,
    session: SessionDep,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    """Authenticate with email + password (used by the Streamlit frontend)."""
    user = _get_by_email(session, body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    return _token_response(user, settings)


@router.get("/me", response_model=UserRead)
def read_me(current_user: "User" = Depends(get_current_user)) -> UserRead:
    return UserRead(id=current_user.id, email=current_user.email, name=current_user.name, role=current_user.role)


@router.patch("/me", response_model=UserRead)
def update_me(
    body: UserUpdate,
    session: SessionDep,
    current_user: "User" = Depends(get_current_user),
) -> UserRead:
    """Update display name and/or password (current password required to change it)."""
    if body.name:
        current_user.name = body.name.strip()

    if body.new_password:
        if not body.current_password or not verify_password(body.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        current_user.hashed_password = hash_password(body.new_password)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return UserRead(id=current_user.id, email=current_user.email, name=current_user.name, role=current_user.role)


@router.post("/token")
def login_form(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str]:
    """OAuth2 password flow for Swagger's Authorize button (username = email)."""
    user = _get_by_email(session, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return {"access_token": _issue_token(user, settings), "token_type": "bearer"}
