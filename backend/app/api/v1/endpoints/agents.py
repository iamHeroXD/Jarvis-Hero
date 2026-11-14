"""API endpoints for Specialist Agents (ATLAS, ORACLE, NEXUS, ATHENA, ECHO, JDI)."""
from __future__ import annotations

from typing import Annotated, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.models.database_models import User
from backend.app.agents.orchestrator import jarvis_orchestrator

router = APIRouter()


class DispatchRequest(BaseModel):
    intent: str
    parameters: dict[str, Any] = {}
    task_id: str | None = None


@router.get("")
async def list_agents(current_user: Annotated[User, Depends(get_current_user)]):
    """Returns specialist agent roster and current capabilities."""
    return [
        {"name": "ATLAS", "role": "Development & Architecture", "status": "active"},
        {"name": "ORACLE", "role": "Research & Source Verification", "status": "active"},
        {"name": "NEXUS", "role": "Business, Pricing & Strategy", "status": "active"},
        {"name": "ATHENA", "role": "Learning, Concepts & Socratic Study", "status": "active"},
        {"name": "ECHO", "role": "Communications & Drafting", "status": "active"},
        {"name": "SENTINEL", "role": "Cybersecurity & Health Sentinel", "status": "active"},
        {"name": "JDI", "role": "JARVIS Development Intelligence", "status": "active"},
    ]


@router.post("/dispatch")
async def dispatch_task(
    data: DispatchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Coordinates specialist agents under central JARVIS orchestrator."""
    result = await jarvis_orchestrator.dispatch_async(
        intent=data.intent,
        parameters=data.parameters,
        task_id=data.task_id,
    )
    return result.model_dump()
