"""API endpoints for Tasks Engine, Verification, Smart Reminders, and Daily Briefings."""
from __future__ import annotations

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.models.database_models import User
from backend.app.tasks.task_engine import task_engine, TaskState
from backend.app.tasks.reminders import reminder_manager

router = APIRouter()


class TaskCreateRequest(BaseModel):
    title: str
    description: str = ""
    assigned_agent: str = "JARVIS"
    permission_level: int = 0
    requires_approval: bool = False
    plan: list[str] = []


class ReminderCreateRequest(BaseModel):
    title: str
    due_at: str
    body: str = ""
    recurrence: str | None = None
    speak_aloud: bool = True


@router.get("")
async def list_tasks(current_user: Annotated[User, Depends(get_current_user)]):
    """Returns active and recent tasks with verified execution status."""
    return task_engine.list_tasks()


@router.post("")
async def create_task(
    data: TaskCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Creates a new managed task in the state machine."""
    task = task_engine.create_task(
        title=data.title,
        description=data.description,
        assigned_agent=data.assigned_agent,
        permission_level=data.permission_level,
        requires_approval=data.requires_approval,
        plan=data.plan,
    )
    return task.model_dump()


@router.get("/reminders")
async def list_reminders(current_user: Annotated[User, Depends(get_current_user)]):
    """Returns scheduled reminders."""
    return reminder_manager.list_reminders()


@router.post("/reminders")
async def create_reminder(
    data: ReminderCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Schedules a new smart reminder."""
    rem = reminder_manager.add_reminder(
        title=data.title,
        due_at=data.due_at,
        body=data.body,
        recurrence=data.recurrence,
        speak_aloud=data.speak_aloud,
    )
    return rem.model_dump()


@router.patch("/reminders/{reminder_id}/complete")
async def complete_reminder(
    reminder_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    success = reminder_manager.complete_reminder(reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found.")
    return {"status": "completed", "reminder_id": reminder_id}


@router.get("/briefing")
async def get_daily_briefing(current_user: Annotated[User, Depends(get_current_user)]):
    """Generates the tactical daily overview briefing."""
    text = reminder_manager.generate_daily_briefing(owner_name=current_user.display_name)
    return {"briefing": text}
