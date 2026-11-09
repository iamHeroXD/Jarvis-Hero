"""API endpoints for User Profiles (Owner, Family, Guest) and Access Boundaries."""
from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.models.database_models import User
from backend.app.security.profiles import profile_manager, ProfileType

router = APIRouter()


class SwitchProfileRequest(BaseModel):
    profile: ProfileType


@router.get("/current")
async def get_current_profile(current_user: Annotated[User, Depends(get_current_user)]):
    return {
        "active_profile": profile_manager.active_profile.value,
        "permissions": profile_manager.get_active_permissions().model_dump(),
    }


@router.post("/switch")
async def switch_profile(
    data: SwitchProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    perms = profile_manager.switch_profile(data.profile)
    return {
        "message": f"Switched to {data.profile.value} profile.",
        "active_profile": data.profile.value,
        "permissions": perms.model_dump(),
    }
