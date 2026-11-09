"""API endpoints for Hardware Performance & Thermal Governor."""
from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import get_current_user, require_owner
from backend.app.models.database_models import User
from backend.app.monitoring.governor import performance_governor, PowerProfile

router = APIRouter()


class ProfileChangeRequest(BaseModel):
    profile: PowerProfile


@router.get("/status")
async def get_governor_status(current_user: Annotated[User, Depends(get_current_user)]):
    """Returns real-time governor state, particle limits, and throttling flags."""
    state = performance_governor.evaluate_hardware_state()
    return state.to_dict()


@router.post("/set-profile")
async def set_power_profile(
    data: ProfileChangeRequest,
    current_user: Annotated[User, Depends(require_owner)],
):
    """Sets the performance profile (eco, balanced, performance)."""
    performance_governor.manual_profile = data.profile
    state = performance_governor.evaluate_hardware_state()
    return {"message": f"Profile switched to {data.profile.value}", "state": state.to_dict()}
