"""API endpoints for Computer Control, Tool Registry, and Application Launcher."""
from __future__ import annotations

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import get_current_user, require_owner
from backend.app.models.database_models import User
from backend.app.tools.registry import tool_registry, ToolExecutionRequest
from backend.app.tools.app_launcher import app_launcher

router = APIRouter()


class ExecuteRequest(BaseModel):
    tool_id: str
    arguments: dict[str, Any] = {}
    approval_granted: bool = False


@router.get("")
async def list_tools(current_user: Annotated[User, Depends(get_current_user)]):
    """Returns the registry of approved tools and their permission levels."""
    return tool_registry.list_tools()


@router.get("/apps")
async def list_approved_applications(current_user: Annotated[User, Depends(get_current_user)]):
    """Returns all approved desktop applications and whether they are installed."""
    return app_launcher.list_approved_apps()


@router.post("/execute")
async def execute_tool(
    data: ExecuteRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Executes a computer control tool under strict permission and verification rules."""
    req = ToolExecutionRequest(
        tool_id=data.tool_id,
        arguments=data.arguments,
        approval_granted=data.approval_granted,
    )
    result = tool_registry.execute_tool(req)
    return result
