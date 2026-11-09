"""System monitoring endpoints."""
from fastapi import APIRouter, Depends
from typing import Annotated
from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.models.database_models import User
from backend.app.monitoring.system_monitor import system_monitor

router = APIRouter()

@router.get("/metrics")
async def get_metrics(current_user: Annotated[User, Depends(get_current_user)]):
    """Real-time system metrics. Never fabricated."""
    return system_monitor.get_status_dict()
