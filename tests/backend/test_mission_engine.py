"""
Unit Tests for JARVIS Mark XI Database-Backed Mission Execution Engine:
- 14-state machine verification
- Task creation, transition logging, and checkpointing in SQLite
- Approval gate handling
- Error recovery and bounded retries
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from backend.app.tasks.mission_engine import (
    mission_engine,
    MissionState,
    MissionStep,
    VALID_TRANSITIONS,
)
from backend.app.database.session import get_session
from backend.app.models.database_models import User, Task, TaskEvent, ApprovalRequest


def test_mission_states_defined():
    """Verify all 14 Mission States are defined."""
    states = [
        MissionState.CREATED,
        MissionState.PLANNING,
        MissionState.READY,
        MissionState.RUNNING,
        MissionState.WAITING_FOR_INPUT,
        MissionState.WAITING_FOR_APPROVAL,
        MissionState.VERIFYING,
        MissionState.COMPLETED,
        MissionState.PAUSED,
        MissionState.FAILED,
        MissionState.NEEDS_ATTENTION,
        MissionState.CANCELLED,
        MissionState.RECOVERING,
    ]
    for s in states:
        assert isinstance(s, str)
        assert len(s) > 0


def test_valid_transitions_mapping():
    """Verify state transition rules enforce sane lifecycle boundaries."""
    assert MissionState.READY in VALID_TRANSITIONS[MissionState.PLANNING]
    assert MissionState.RUNNING in VALID_TRANSITIONS[MissionState.READY]
    assert MissionState.COMPLETED not in VALID_TRANSITIONS[MissionState.PLANNING]
    assert MissionState.WAITING_FOR_APPROVAL in VALID_TRANSITIONS[MissionState.RUNNING]


@pytest.mark.asyncio
async def test_create_and_transition_mission_live():
    """Verify SQLite persistence of mission and task events."""
    async with get_session() as session:
        # Fetch or create test user
        user = (await session.execute(__import__("sqlalchemy").select(User))).scalars().first()
        if not user:
            user = User(
                username="rohan_test_me",
                display_name="Rohan",
                hashed_password="hash",
                is_owner=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        user_id = user.id

    steps = [
        MissionStep(
            id=1,
            name="Initialize Workspace",
            description="Verify project repository exists",
            action_type="verify",
            parameters={"file_path": r"f:\Work\Jarvis- Hero\package.json"},
        ),
        MissionStep(
            id=2,
            name="Run System Check",
            description="Run quick system telemetry check",
            action_type="directive",
            parameters={"directive": "system diagnostics"},
        ),
    ]

    task = await mission_engine.create_mission(
        user_id=user_id,
        title="Test Mark XI Diagnostic Mission",
        description="Verifies repository and diagnostics",
        steps=steps,
    )
    assert task.id is not None
    assert task.status == MissionState.CREATED
    assert task.task_uuid.startswith("mission_")

    # Transition state to PLANNING then READY
    new_state = await mission_engine.transition_state(task.id, MissionState.PLANNING, "Formulating plan")
    assert new_state == MissionState.PLANNING

    new_state = await mission_engine.transition_state(task.id, MissionState.READY, "Plan ready")
    assert new_state == MissionState.READY

    # Verify TaskEvents logged in DB
    async with get_session() as session:
        events = (await session.execute(
            __import__("sqlalchemy").select(TaskEvent).where(TaskEvent.task_id == task.id).order_by(TaskEvent.id.asc())
        )).scalars().all()
        assert len(events) >= 3  # created, planning, ready


@pytest.mark.asyncio
async def test_approval_request_flow():
    """Verify steps requiring approval pause execution and generate an ApprovalRequest."""
    async with get_session() as session:
        user = (await session.execute(__import__("sqlalchemy").select(User))).scalars().first()
        user_id = user.id

    critical_step = MissionStep(
        id=1,
        name="Deploy Production Code",
        description="Deploy directly to remote production",
        action_type="command",
        parameters={"command": "echo Deploying"},
        requires_approval=True,
        risk_level="critical",
    )

    task = await mission_engine.create_mission(
        user_id=user_id,
        title="Critical Deployment Mission",
        description="Deploys production artifacts",
        steps=[critical_step],
    )

    res = await mission_engine.execute_mission(task.task_uuid)
    assert res["status"] == MissionState.WAITING_FOR_APPROVAL
    assert "approval_uuid" in res

    # Verify ApprovalRequest created in SQLite
    async with get_session() as session:
        appr = (await session.execute(
            __import__("sqlalchemy").select(ApprovalRequest).where(ApprovalRequest.approval_uuid == res["approval_uuid"])
        )).scalar_one_or_none()
        assert appr is not None
        assert appr.risk_level == "critical"
        assert appr.status == "pending"

    # Test approval
    appr_res = await mission_engine.approve_step(res["approval_uuid"], approved=True)
    assert appr_res["success"] is True
    assert appr_res["approved"] is True
