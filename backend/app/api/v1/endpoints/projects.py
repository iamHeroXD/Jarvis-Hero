"""Projects, tasks, settings, system, and AI endpoints — Phase 1 stubs with real routing."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import get_current_user, require_owner
from backend.app.models.database_models import User

router = APIRouter()


@router.get("")
async def list_projects(current_user: Annotated[User, Depends(get_current_user)]):
    """List all projects. Full implementation in Phase 5."""
    return []


@router.post("")
async def create_project(current_user: Annotated[User, Depends(require_owner)]):
    return {"message": "Project creation — Phase 5"}
