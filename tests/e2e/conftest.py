"""
Pytest configuration and shared fixtures for JARVIS End-to-End (E2E) test suite.
Provides:
- FastAPI async HTTP client (httpx.AsyncClient with ASGITransport)
- Synchronous Starlette TestClient (with WebSocket test support)
- Authenticated owner fixtures and JWT bearer tokens
- Database lifecycle and test isolation
"""
from __future__ import annotations

import os
import pytest
import httpx
from typing import AsyncGenerator, Generator
from starlette.testclient import TestClient
from sqlalchemy import select

from backend.app.main import app
from backend.app.core.config import settings, ensure_data_dirs
from backend.app.database.session import init_db, get_session
from backend.app.models.database_models import User
from backend.app.security.auth import hash_password, create_access_token


@pytest.fixture(scope="session", autouse=True)
def configure_e2e_environment():
    """Configures environment variables for E2E testing."""
    os.environ["JARVIS_TEST_MODE"] = "true"
    ensure_data_dirs()


@pytest.fixture(autouse=True)
async def ensure_db_ready():
    """Ensures database tables are initialized and an active owner user exists."""
    await init_db()
    async with get_session() as session:
        result = await session.execute(select(User).where(User.is_owner == True))
        owner = result.scalars().first()
        if not owner:
            owner = User(
                username="rohan_e2e_owner",
                display_name="Rohan",
                hashed_password=hash_password("JarvisOwner2026!"),
                is_owner=True,
                is_active=True,
            )
            session.add(owner)
            await session.commit()


@pytest.fixture
async def test_owner() -> User:
    """Returns the primary test owner user."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.is_owner == True).order_by(User.id.desc()))
        owner = result.scalars().first()
        if not owner:
            owner = User(
                username="rohan_e2e_owner",
                display_name="Rohan",
                hashed_password=hash_password("JarvisOwner2026!"),
                is_owner=True,
                is_active=True,
            )
            session.add(owner)
            await session.commit()
            await session.refresh(owner)
        return owner


@pytest.fixture
def auth_token(test_owner: User) -> str:
    """Generates a valid JWT access token for the test owner."""
    return create_access_token({
        "sub": str(test_owner.id),
        "username": test_owner.username,
        "role": "owner",
        "is_owner": True,
    })


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """Returns HTTP headers containing Bearer authorization."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client for testing FastAPI endpoints."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def auth_client(auth_headers: dict[str, str]) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client pre-configured with owner authentication headers."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers=auth_headers,
    ) as client:
        yield client


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Synchronous Starlette TestClient with WebSocket capability."""
    with TestClient(app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def sync_auth_client(auth_headers: dict[str, str]) -> Generator[TestClient, None, None]:
    """Synchronous Starlette TestClient with owner authentication headers."""
    with TestClient(app, base_url="http://testserver", headers=auth_headers) as client:
        yield client
