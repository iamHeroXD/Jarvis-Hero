"""
Authentication endpoints.
Phase 1: Local owner authentication with JWT.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger
from backend.app.database.session import get_db
from backend.app.models.database_models import User
from backend.app.security.auth import (
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)

router = APIRouter()
logger = get_logger("api.auth")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# ── Schemas ───────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    display_name: str
    is_owner: bool


class UserCreate(BaseModel):
    username: str
    display_name: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    is_owner: bool
    is_active: bool

    model_config = {"from_attributes": True}


class SetupStatus(BaseModel):
    owner_configured: bool
    owner_username: str | None = None


# ── Dependencies ──────────────────────────────────────────────────────────────

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Verify JWT and return the authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if not payload:
        raise credentials_exception

    sub_val = payload.get("sub")
    if sub_val is None:
        raise credentials_exception
    try:
        user_id = int(sub_val)
    except (ValueError, TypeError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_exception
    return user


async def require_owner(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require owner-level access. Security enforced on the backend."""
    if not current_user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required for this operation.",
        )
    return current_user


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/setup-status", response_model=SetupStatus)
async def setup_status(db: Annotated[AsyncSession, Depends(get_db)]):
    """Check whether the owner account has been created yet (first-run detection)."""
    result = await db.execute(select(User).where(User.is_owner == True))
    owner = result.scalar_one_or_none()
    return SetupStatus(
        owner_configured=owner is not None,
        owner_username=owner.username if owner else None,
    )


@router.post("/setup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def create_owner(
    data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    First-run only: create the owner account.
    Fails if an owner already exists.
    """
    # Check no owner exists
    result = await db.execute(select(User).where(User.is_owner == True))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Owner account already exists. Use /auth/token to sign in.",
        )

    # Check username not taken
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken.",
        )

    user = User(
        username=data.username,
        display_name=data.display_name,
        hashed_password=hash_password(data.password),
        is_owner=True,
        is_active=True,
    )
    db.add(user)
    await db.flush()  # Get the ID without full commit

    token = create_access_token({"sub": user.id})
    logger.info("Owner account created: %s", data.username)

    return Token(
        access_token=token,
        user_id=user.id,
        display_name=user.display_name,
        is_owner=True,
    )


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate with username + password. Returns a JWT."""
    result = await db.execute(
        select(User).where(User.username == form_data.username, User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning("Failed login attempt for user: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.id})
    logger.info("User authenticated: %s", user.username)

    return Token(
        access_token=token,
        user_id=user.id,
        display_name=user.display_name,
        is_owner=user.is_owner,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Return the currently authenticated user's profile."""
    return current_user
