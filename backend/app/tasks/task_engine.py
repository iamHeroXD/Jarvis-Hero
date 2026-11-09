"""
JARVIS Task Execution Engine
Implements the formal task lifecycle state machine:
CREATED -> PLANNING -> AWAITING_APPROVAL -> RUNNING -> VERIFYING -> COMPLETED / FAILED
Records task events, execution evidence, and audit logs.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from backend.app.core.logging_config import get_logger

logger = get_logger("tasks.engine")


class TaskState(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_ATTENTION = "needs_attention"
    CANCELLED = "cancelled"


class ManagedTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    title: str
    description: str = ""
    assigned_agent: str = "JARVIS"
    status: TaskState = TaskState.CREATED
    permission_level: int = 0
    requires_approval: bool = False
    plan: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str | None = None
    verified: bool = False


class TaskEngine:
    """Manages active tasks, state transitions, and audit records."""

    def __init__(self) -> None:
        self._tasks: dict[str, ManagedTask] = {}

    def create_task(
        self,
        title: str,
        description: str = "",
        assigned_agent: str = "JARVIS",
        permission_level: int = 0,
        requires_approval: bool = False,
        plan: list[str] | None = None,
    ) -> ManagedTask:
        task = ManagedTask(
            title=title,
            description=description,
            assigned_agent=assigned_agent,
            permission_level=permission_level,
            requires_approval=requires_approval,
            plan=plan or [],
        )
        self._tasks[task.task_id] = task
        logger.info("Task created: [%s] %s (agent: %s)", task.task_id, title, assigned_agent)
        return task

    def transition(self, task_id: str, new_state: TaskState, note: str | None = None) -> ManagedTask | None:
        task = self._tasks.get(task_id)
        if not task:
            return None

        old_state = task.status
        task.status = new_state

        if new_state == TaskState.COMPLETED:
            task.completed_at = datetime.now(UTC).isoformat()
            task.verified = True

        logger.info("Task [%s] state transition: %s -> %s (%s)", task_id, old_state.value, new_state.value, note or "")
        return task

    def record_evidence(self, task_id: str, evidence_item: str) -> None:
        task = self._tasks.get(task_id)
        if task:
            task.evidence.append(evidence_item)

    def record_error(self, task_id: str, error_message: str) -> None:
        task = self._tasks.get(task_id)
        if task:
            task.errors.append(error_message)
            self.transition(task_id, TaskState.FAILED, note=error_message)

    def get_task(self, task_id: str) -> ManagedTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self, limit: int = 50) -> list[dict[str, Any]]:
        return [t.model_dump() for t in list(self._tasks.values())[-limit:]]


task_engine = TaskEngine()
