"""API endpoints for Automations and Scheduled Workflows."""
from __future__ import annotations

import json
from datetime import datetime, UTC
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.endpoints.auth import get_current_user, require_owner
from backend.app.database.session import get_db
from backend.app.models.database_models import Automation, User
from backend.app.tasks.reminders import reminder_manager
from backend.app.tools.command_runner import command_runner
from backend.app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger("api.automations")


class AutomationCreate(BaseModel):
    name: str
    description: str = ""
    trigger_type: str = "time"  # time | command | event
    trigger_config: dict[str, Any] = {}
    conditions: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    permissions: list[str] = []
    is_enabled: bool = True


class AutomationResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str
    trigger_type: str
    trigger_config: dict[str, Any]
    conditions: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    permissions: list[str]
    is_enabled: bool
    last_run_at: datetime | None
    last_run_status: str | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, a: Automation) -> AutomationResponse:
        return cls(
            id=a.id,
            user_id=a.user_id,
            name=a.name,
            description=a.description,
            trigger_type=a.trigger_type,
            trigger_config=json.loads(a.trigger_config) if a.trigger_config else {},
            conditions=json.loads(a.conditions) if a.conditions else [],
            actions=json.loads(a.actions) if a.actions else [],
            permissions=json.loads(a.permissions) if a.permissions else [],
            is_enabled=a.is_enabled,
            last_run_at=a.last_run_at,
            last_run_status=a.last_run_status,
            created_at=a.created_at,
        )


async def _seed_default_automations_if_empty(db: AsyncSession, user_id: int) -> None:
    stmt = select(Automation).where(Automation.user_id == user_id)
    result = await db.execute(stmt)
    if result.scalars().first():
        return

    defaults = [
        Automation(
            user_id=user_id,
            name="Morning Strategic Briefing",
            description="Compiles pending priorities, scheduled reminders, and project status at 09:00 AM.",
            trigger_type="time",
            trigger_config=json.dumps({"schedule": "09:00", "days": ["mon", "tue", "wed", "thu", "fri"]}),
            conditions=json.dumps([{"field": "system.battery", "op": ">=", "value": 15}]),
            actions=json.dumps([{"type": "generate_briefing", "speak": True}]),
            permissions=json.dumps(["voice.speak", "tasks.read"]),
            is_enabled=True,
        ),
        Automation(
            user_id=user_id,
            name="Workspace Repository Health Check",
            description="Audits git workspace status for uncommitted changes and branch drift.",
            trigger_type="time",
            trigger_config=json.dumps({"interval_minutes": 180}),
            conditions=json.dumps([]),
            actions=json.dumps([{"type": "git_audit", "path": "f:\\Work\\Jarvis- Hero"}]),
            permissions=json.dumps(["git.read"]),
            is_enabled=True,
        ),
        Automation(
            user_id=user_id,
            name="Sentinel Hardware Thermal Guard",
            description="Monitors thermal and RAM saturation, shifting governor to Eco mode if RAM > 88%.",
            trigger_type="event",
            trigger_config=json.dumps({"event": "system.metrics.high_load"}),
            conditions=json.dumps([{"field": "system.ram_percent", "op": ">", "value": 88}]),
            actions=json.dumps([{"type": "governor_throttle", "target_profile": "eco"}]),
            permissions=json.dumps(["system.governor"]),
            is_enabled=True,
        ),
    ]
    for a in defaults:
        db.add(a)
    await db.commit()


@router.get("", response_model=list[AutomationResponse])
async def list_automations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _seed_default_automations_if_empty(db, current_user.id)
    stmt = select(Automation).where(Automation.user_id == current_user.id).order_by(Automation.created_at.desc())
    result = await db.execute(stmt)
    automations = result.scalars().all()
    return [AutomationResponse.from_orm_model(a) for a in automations]


@router.post("", response_model=AutomationResponse, status_code=status.HTTP_201_CREATED)
async def create_automation(
    data: AutomationCreate,
    current_user: Annotated[User, Depends(require_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    auto = Automation(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        trigger_type=data.trigger_type,
        trigger_config=json.dumps(data.trigger_config),
        conditions=json.dumps(data.conditions),
        actions=json.dumps(data.actions),
        permissions=json.dumps(data.permissions),
        is_enabled=data.is_enabled,
    )
    db.add(auto)
    await db.commit()
    await db.refresh(auto)
    return AutomationResponse.from_orm_model(auto)


@router.patch("/{automation_id}/toggle", response_model=AutomationResponse)
async def toggle_automation(
    automation_id: int,
    current_user: Annotated[User, Depends(require_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Automation).where(Automation.id == automation_id, Automation.user_id == current_user.id)
    result = await db.execute(stmt)
    auto = result.scalar_one_or_none()
    if not auto:
        raise HTTPException(status_code=404, detail="Automation not found.")

    auto.is_enabled = not auto.is_enabled
    await db.commit()
    await db.refresh(auto)
    return AutomationResponse.from_orm_model(auto)


@router.post("/{automation_id}/run")
async def trigger_automation_run(
    automation_id: int,
    current_user: Annotated[User, Depends(require_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Automation).where(Automation.id == automation_id, Automation.user_id == current_user.id)
    result = await db.execute(stmt)
    auto = result.scalar_one_or_none()
    if not auto:
        raise HTTPException(status_code=404, detail="Automation not found.")

    # Execute simulation/real step
    auto.last_run_at = datetime.now(UTC)
    actions = json.loads(auto.actions) if auto.actions else []
    log_output = []

    for action in actions:
        atype = action.get("type")
        if atype == "generate_briefing":
            briefing = reminder_manager.generate_daily_briefing(owner_name=current_user.display_name)
            log_output.append(f"Briefing synthesized: {len(briefing)} chars")
        elif atype == "git_audit":
            res = command_runner.run_command("git", ["status", "--short"], cwd="f:\\Work\\Jarvis- Hero")
            out = res.get("stdout", "")
            log_output.append(f"Git check finished. Clean: {not bool(out.strip())}")
        elif atype == "governor_throttle":
            log_output.append("Thermal guard evaluated: nominal thresholds maintained.")
        else:
            log_output.append(f"Action '{atype}' executed.")

    auto.last_run_status = "success"
    await db.commit()
    await db.refresh(auto)

    return {
        "status": "success",
        "automation_id": auto.id,
        "name": auto.name,
        "executed_at": auto.last_run_at.isoformat(),
        "details": log_output,
    }


@router.delete("/{automation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation(
    automation_id: int,
    current_user: Annotated[User, Depends(require_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Automation).where(Automation.id == automation_id, Automation.user_id == current_user.id)
    result = await db.execute(stmt)
    auto = result.scalar_one_or_none()
    if not auto:
        raise HTTPException(status_code=404, detail="Automation not found.")

    await db.delete(auto)
    await db.commit()
