"""
JARVIS Database Session Management
Async SQLAlchemy with SQLite + aiosqlite.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.app.core.config import settings, DB_DIR
from backend.app.core.logging_config import get_logger
from backend.app.models.database_models import Base

logger = get_logger("database")

# ── Engine ────────────────────────────────────────────────────────────────────

_engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
    },
    # StaticPool is recommended for single-process SQLite
    poolclass=StaticPool,
)

_session_factory = async_sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ── Lifecycle ─────────────────────────────────────────────────────────────────

async def init_db() -> None:
    """
    Create all tables and enable WAL mode + FTS5.
    Called once on application startup.
    """
    DB_DIR.mkdir(parents=True, exist_ok=True)
    async with _engine.begin() as conn:
        # Create all ORM tables
        await conn.run_sync(Base.metadata.create_all)
        # Enable Write-Ahead Logging for better concurrent reads
        await conn.execute(__import__("sqlalchemy").text("PRAGMA journal_mode=WAL"))
        await conn.execute(__import__("sqlalchemy").text("PRAGMA foreign_keys=ON"))
        await conn.execute(__import__("sqlalchemy").text("PRAGMA synchronous=NORMAL"))
    logger.info("Database initialised at %s", settings.database_url)
    await _ensure_fts_tables()


async def _ensure_fts_tables() -> None:
    """Create FTS5 virtual tables for full-text memory search."""
    async with _engine.begin() as conn:
        await conn.execute(__import__("sqlalchemy").text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                title,
                content,
                content='memories',
                content_rowid='id'
            )
        """))
        # Trigger to keep FTS in sync
        await conn.execute(__import__("sqlalchemy").text("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_insert
            AFTER INSERT ON memories BEGIN
                INSERT INTO memories_fts(rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END
        """))
        await conn.execute(__import__("sqlalchemy").text("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_update
            AFTER UPDATE ON memories BEGIN
                UPDATE memories_fts SET title=new.title, content=new.content
                WHERE rowid=new.id;
            END
        """))
        await conn.execute(__import__("sqlalchemy").text("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_delete
            AFTER DELETE ON memories BEGIN
                DELETE FROM memories_fts WHERE rowid=old.id;
            END
        """))
    logger.debug("FTS5 tables verified.")


async def close_db() -> None:
    """Dispose the database engine on shutdown."""
    await _engine.dispose()
    logger.info("Database engine disposed.")


# ── Dependency ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for a single database session."""
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency injection for database sessions."""
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
