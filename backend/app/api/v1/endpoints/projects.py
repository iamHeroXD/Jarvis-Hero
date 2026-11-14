"""API endpoints for Projects, Workspaces, and Repository Awareness."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Annotated, Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.endpoints.auth import get_current_user, require_owner
from backend.app.database.session import get_db
from backend.app.models.database_models import Project, ProjectNote, Task, User
from backend.app.tools.command_runner import command_runner
from backend.app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger("api.projects")


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    status: str = "active"  # active | paused | completed | archived
    priority: str = "medium"  # low | medium | high | critical
    repository_url: str | None = None
    local_path: str | None = None
    goals: list[str] = []
    tags: list[str] = []
    deadline: datetime | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    repository_url: str | None = None
    local_path: str | None = None
    goals: list[str] | None = None
    tags: list[str] | None = None
    deadline: datetime | None = None


class ProjectNoteCreate(BaseModel):
    content: str
    note_type: str = "note"  # note | decision | blocker | milestone


class ProjectNoteResponse(BaseModel):
    id: int
    project_id: int
    content: str
    note_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str
    status: str
    priority: str
    repository_url: str | None
    local_path: str | None
    goals: list[str]
    tags: list[str]
    deadline: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, p: Project) -> ProjectResponse:
        goals_parsed = []
        tags_parsed = []
        try:
            goals_parsed = json.loads(p.goals) if p.goals else []
        except Exception:
            goals_parsed = []
        try:
            tags_parsed = json.loads(p.tags) if p.tags else []
        except Exception:
            tags_parsed = []

        return cls(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            description=p.description,
            status=p.status,
            priority=p.priority,
            repository_url=p.repository_url,
            local_path=p.local_path,
            goals=goals_parsed,
            tags=tags_parsed,
            deadline=p.deadline,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )


async def _seed_default_projects_if_empty(db: AsyncSession, user_id: int) -> None:
    """Pre-populate core projects (RCN & Clearly AI) if the user has no projects."""
    stmt = select(Project).where(Project.user_id == user_id)
    result = await db.execute(stmt)
    existing = result.scalars().all()
    if existing:
        return

    defaults = [
        Project(
            user_id=user_id,
            name="RCN (Robotics Coding Network)",
            description="Autonomous robotics and coding orchestration architecture for edge systems.",
            status="active",
            priority="high",
            repository_url="https://github.com/owner/rcn",
            local_path="f:\\Work\\Jarvis- Hero",
            goals=json.dumps([
                "Implement distributed control protocol",
                "Integrate hardware telemetry feed",
                "Automate verification test suite",
            ]),
            tags=json.dumps(["robotics", "python", "edge", "active"]),
        ),
        Project(
            user_id=user_id,
            name="Clearly AI",
            description="High-clarity cognitive synthesis, contextual retrieval and decision support platform.",
            status="active",
            priority="medium",
            repository_url="https://github.com/owner/clearly-ai",
            local_path=None,
            goals=json.dumps([
                "Document architecture specification",
                "Benchmark cognitive recall latency",
            ]),
            tags=json.dumps(["ai", "cognition", "platform"]),
        ),
    ]
    for p in defaults:
        db.add(p)
    await db.commit()


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all projects for the authenticated user, seeding defaults on first run."""
    await _seed_default_projects_if_empty(db, current_user.id)
    stmt = select(Project).where(Project.user_id == current_user.id).order_by(Project.updated_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return [ProjectResponse.from_orm_model(p) for p in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: Annotated[User, Depends(require_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new tracked project."""
    project = Project(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        status=data.status,
        priority=data.priority,
        repository_url=data.repository_url,
        local_path=data.local_path,
        goals=json.dumps(data.goals),
        tags=json.dumps(data.tags),
        deadline=data.deadline,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    logger.info("Project '%s' created (id=%d)", project.name, project.id)
    return ProjectResponse.from_orm_model(project)


# ── Mark XI Next-Day Startup Briefing ─────────────────────────────────────────

@router.get("/startup-briefing")
async def get_startup_briefing(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Generates a personalized next-day / startup operational briefing for Rohan:
    - Active projects and pending goals
    - Recent architectural decisions & blockers
    - High-priority open tasks
    - Real-time hardware telemetry and memory status
    - Recommended immediate action
    """
    from backend.app.tools.unified_computer_controller import unified_controller

    # 1. Fetch active projects
    proj_stmt = (
        select(Project)
        .where(Project.user_id == current_user.id, Project.status == "active")
        .order_by(Project.updated_at.desc())
    )
    active_projects = (await db.execute(proj_stmt)).scalars().all()

    # 2. Fetch recent decisions / blockers across projects
    notes_stmt = (
        select(ProjectNote)
        .join(Project, ProjectNote.project_id == Project.id)
        .where(Project.user_id == current_user.id)
        .order_by(ProjectNote.created_at.desc())
        .limit(5)
    )
    recent_notes = (await db.execute(notes_stmt)).scalars().all()

    # 3. Fetch pending tasks
    task_stmt = (
        select(Task)
        .where(Task.user_id == current_user.id, Task.status.in_(["created", "ready", "running", "waiting_for_approval", "needs_attention"]))
        .order_by(Task.priority.desc(), Task.created_at.desc())
        .limit(6)
    )
    pending_tasks = (await db.execute(task_stmt)).scalars().all()

    # 4. System telemetry
    sys_diag = unified_controller.get_system_diagnostics()
    bat_info = unified_controller.get_battery_status()

    hour = datetime.now().hour
    time_greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    owner_name = current_user.display_name or "Sir"

    proj_summaries = []
    for p in active_projects:
        try:
            goals = json.loads(p.goals) if isinstance(p.goals, str) else (p.goals or [])
        except Exception:
            goals = []
        proj_summaries.append({
            "id": p.id,
            "name": p.name,
            "priority": p.priority,
            "goals_count": len(goals),
            "local_path": p.local_path,
        })

    decision_summaries = [
        {"note_type": n.note_type, "content": n.content, "created_at": n.created_at.isoformat()}
        for n in recent_notes
    ]

    task_summaries = [
        {"id": t.id, "uuid": t.task_uuid, "title": t.title, "status": t.status, "priority": t.priority}
        for t in pending_tasks
    ]

    rec_action = (
        f"Review active development on {active_projects[0].name}."
        if active_projects
        else "Formulate today's primary engineering objective."
    )

    spoken = (
        f"{time_greeting}, {owner_name}. All Mark XI systems are nominal. "
        f"You have {len(active_projects)} active projects and {len(pending_tasks)} pending operations. "
        f"RAM is at {sys_diag.get('ram', 70):.0f}%, battery is at {bat_info.get('percent', 90)}%. "
        f"I am standing by to assist with computer control, deep research, and development in Antigravity."
    )

    return {
        "greeting": f"{time_greeting}, {owner_name}",
        "date": datetime.now().strftime("%A, %B %d, %Y"),
        "spoken_briefing": spoken,
        "recommended_action": rec_action,
        "system_status": {
            "ram_percent": sys_diag.get("ram"),
            "cpu_percent": sys_diag.get("cpu"),
            "battery_percent": bat_info.get("percent"),
            "battery_charging": bat_info.get("charging"),
        },
        "active_projects": proj_summaries,
        "recent_notes": decision_summaries,
        "pending_tasks": task_summaries,
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return ProjectResponse.from_orm_model(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: Annotated[User, Depends(require_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.status is not None:
        project.status = data.status
    if data.priority is not None:
        project.priority = data.priority
    if data.repository_url is not None:
        project.repository_url = data.repository_url
    if data.local_path is not None:
        project.local_path = data.local_path
    if data.goals is not None:
        project.goals = json.dumps(data.goals)
    if data.tags is not None:
        project.tags = json.dumps(data.tags)
    if data.deadline is not None:
        project.deadline = data.deadline

    await db.commit()
    await db.refresh(project)
    return ProjectResponse.from_orm_model(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: Annotated[User, Depends(require_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    await db.delete(project)
    await db.commit()
    logger.info("Project id=%d deleted", project_id)


@router.get("/{project_id}/git-status")
async def get_project_git_status(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Inspects git status on the project's local workspace path."""
    stmt = select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if not project.local_path:
        return {"is_git": False, "message": "No local workspace path configured."}

    path = Path(project.local_path)
    if not path.exists() or not (path / ".git").exists():
        return {"is_git": False, "path": str(path), "message": "Directory does not contain a .git repository."}

    # Execute safe git status
    status_res = command_runner.run_command("git", ["status", "--short"], cwd=str(path))
    branch_res = command_runner.run_command("git", ["branch", "--show-current"], cwd=str(path))

    status_out = status_res.get("stdout", "")
    branch_out = branch_res.get("stdout", "")
    is_success = status_res.get("success", False)

    return {
        "is_git": True,
        "path": str(path),
        "branch": branch_out.strip() if branch_res.get("success") else "unknown",
        "has_changes": bool(status_out.strip()),
        "status_output": status_out.strip() if is_success else "",
        "clean": is_success and not bool(status_out.strip()),
    }


@router.get("/{project_id}/notes", response_model=list[ProjectNoteResponse])
async def list_project_notes(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(ProjectNote).where(ProjectNote.project_id == project_id).order_by(ProjectNote.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{project_id}/notes", response_model=ProjectNoteResponse, status_code=status.HTTP_201_CREATED)
async def add_project_note(
    project_id: int,
    data: ProjectNoteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Verify project exists
    stmt = select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    note = ProjectNote(
        project_id=project_id,
        content=data.content,
        note_type=data.note_type,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note

