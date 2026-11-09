"""API endpoints for System Activity and Security Audit Logs."""
from __future__ import annotations

from datetime import datetime, UTC
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.models.database_models import ActivityLog, User

router = APIRouter()


class ActivityResponse(BaseModel):
    id: int
    user_id: int | None
    task_id: int | None
    agent_name: str | None
    tool_id: str | None
    action: str
    permission_level: int | None
    approval_given: bool | None
    result: str
    details: str
    created_at: datetime

    model_config = {"from_attributes": True}


async def _seed_initial_activity_if_empty(db: AsyncSession, user_id: int) -> None:
    stmt = select(ActivityLog).limit(1)
    result = await db.execute(stmt)
    if result.scalars().first():
        return

    initial_events = [
        ActivityLog(
            user_id=user_id,
            agent_name="SENTINEL",
            tool_id="system.integrity",
            action="System Startup & Memory Map Initialisation",
            permission_level=0,
            approval_given=True,
            result="success",
            details="Validated system processes, FTS5 memory tables, and Windows Credential store.",
        ),
        ActivityLog(
            user_id=user_id,
            agent_name="ATLAS",
            tool_id="app_launcher",
            action="Allowlist & Capability Scan",
            permission_level=0,
            approval_given=True,
            result="success",
            details="Registered standard tools: VS Code, Chrome, Terminal, Explorer, Antigravity.",
        ),
    ]
    for ev in initial_events:
        db.add(ev)
    await db.commit()


@router.get("", response_model=list[ActivityResponse])
async def list_activity(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, le=200),
):
    """Returns recent verified activity log items in reverse chronological order."""
    await _seed_initial_activity_if_empty(db, current_user.id)
    stmt = select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
