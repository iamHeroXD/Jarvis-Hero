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


# ── Compound Multi-Step Workflow Endpoints ─────────────────────────────────────

from backend.app.tasks.workflow_engine import workflow_engine, WorkflowStep, WorkflowState


class PromptToIdeRequest(BaseModel):
    concept: str
    ide: str = "antigravity"
    project_path: str = r"f:\Work\Jarvis- Hero"


class ResearchPdfRequest(BaseModel):
    topic: str
    output_dir: str = r"f:\Work\Jarvis- Hero\data"


class SocialDraftRequest(BaseModel):
    platform: str = "Instagram"
    recipient: str
    message: str


@router.get("/workflows")
async def list_workflows(current_user: Annotated[User, Depends(get_current_user)]):
    """Returns all tracked multi-step compound workflows and their states."""
    return [wf.model_dump() for wf in workflow_engine.active_workflows.values()]


@router.post("/workflows/prompt-to-ide")
async def trigger_prompt_to_ide_workflow(
    data: PromptToIdeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Initiates master prompt synthesis, IDE launch, and Antigravity handoff deposit."""
    wf = workflow_engine.build_prompt_to_ide_workflow(
        prompt_concept=data.concept,
        ide=data.ide,
        project_path=data.project_path,
    )
    # Execute asynchronously in background
    import asyncio
    asyncio.create_task(workflow_engine.execute_workflow(wf.workflow_id))
    return wf.model_dump()


@router.post("/workflows/research-pdf")
async def trigger_research_pdf_workflow(
    data: ResearchPdfRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Initiates web research, DOM parsing, citation compilation, and PDF generation."""
    wf = workflow_engine.build_research_and_pdf_workflow(
        topic=data.topic,
        output_dir=data.output_dir,
    )
    import asyncio
    asyncio.create_task(workflow_engine.execute_workflow(wf.workflow_id))
    return wf.model_dump()


@router.post("/workflows/social-draft")
async def trigger_social_draft_workflow(
    data: SocialDraftRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Prepares a message draft with MANDATORY owner approval before sending."""
    wf = workflow_engine.build_social_draft_workflow(
        platform=data.platform,
        recipient=data.recipient,
        draft_text=data.message,
    )
    import asyncio
    asyncio.create_task(workflow_engine.execute_workflow(wf.workflow_id))
    return wf.model_dump()


@router.post("/workflows/{workflow_id}/approve")
async def approve_workflow_step(
    workflow_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Explicit owner approval gate to resume a paused workflow."""
    wf = workflow_engine.approve_and_resume(workflow_id)
    return wf.model_dump()

