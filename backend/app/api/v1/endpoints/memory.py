"""Memory management endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, delete, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.models.database_models import Memory, User
from backend.app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger("api.memory")

VALID_CATEGORIES = {"personal", "project", "work", "conversation", "technical", "preference", "learning"}


class MemoryCreate(BaseModel):
    category: str
    title: str
    content: str
    source_type: str = "manual"
    source_ref: str | None = None
    tags: list[str] = []
    is_sensitive: bool = False


class MemoryResponse(BaseModel):
    id: int
    category: str
    title: str
    content: str
    source_type: str
    is_pinned: bool
    is_sensitive: bool
    tags: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MemoryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    is_pinned: bool | None = None


@router.get("", response_model=list[MemoryResponse])
async def list_memories(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    query = select(Memory).where(Memory.user_id == current_user.id)
    if category:
        query = query.where(Memory.category == category)
    query = query.order_by(Memory.is_pinned.desc(), Memory.updated_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/search", response_model=list[MemoryResponse])
async def search_memories(
    q: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 20,
):
    """Full-text search using SQLite FTS5."""
    if not q.strip():
        return []
    # FTS5 search
    result = await db.execute(
        text("""
            SELECT m.* FROM memories m
            JOIN memories_fts f ON m.id = f.rowid
            WHERE memories_fts MATCH :query
            AND m.user_id = :user_id
            ORDER BY rank
            LIMIT :limit
        """),
        {"query": q, "user_id": current_user.id, "limit": limit},
    )
    rows = result.fetchall()
    # Re-fetch as ORM objects
    ids = [r[0] for r in rows]
    if not ids:
        return []
    orm_result = await db.execute(select(Memory).where(Memory.id.in_(ids)))
    return orm_result.scalars().all()


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    data: MemoryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if data.category not in VALID_CATEGORIES:
        raise HTTPException(400, f"Invalid category. Valid: {sorted(VALID_CATEGORIES)}")

    import json
    mem = Memory(
        user_id=current_user.id,
        category=data.category,
        title=data.title,
        content=data.content,
        source_type=data.source_type,
        source_ref=data.source_ref,
        tags=json.dumps(data.tags),
        is_sensitive=data.is_sensitive,
    )
    db.add(mem)
    await db.flush()
    logger.info("Memory created: [%s] %s", data.category, data.title)
    return mem


@router.patch("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: int,
    data: MemoryUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    import json
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.user_id == current_user.id)
    )
    mem = result.scalar_one_or_none()
    if not mem:
        raise HTTPException(404, "Memory not found.")

    if data.title is not None:
        mem.title = data.title
    if data.content is not None:
        mem.content = data.content
    if data.category is not None:
        if data.category not in VALID_CATEGORIES:
            raise HTTPException(400, f"Invalid category.")
        mem.category = data.category
    if data.tags is not None:
        mem.tags = json.dumps(data.tags)
    if data.is_pinned is not None:
        mem.is_pinned = data.is_pinned

    return mem


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.user_id == current_user.id)
    )
    mem = result.scalar_one_or_none()
    if not mem:
        raise HTTPException(404, "Memory not found.")
    await db.delete(mem)


@router.delete("/category/{category}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if category not in VALID_CATEGORIES:
        raise HTTPException(400, "Invalid category.")
    await db.execute(
        delete(Memory).where(Memory.user_id == current_user.id, Memory.category == category)
    )
    logger.info("Deleted all memories in category '%s' for user %d", category, current_user.id)
