"""System monitoring & optimization endpoints."""
from __future__ import annotations

from fastapi import APIRouter
from backend.app.monitoring.system_monitor import system_monitor
from backend.app.tools.windows_controller import windows_controller

router = APIRouter()


@router.get("/metrics")
async def get_metrics():
    """Real-time system metrics. Never fabricated."""
    return system_monitor.get_status_dict()


@router.post("/optimize-memory")
async def optimize_memory():
    """Actively trims process working sets and collects garbage to reclaim system RAM."""
    result = windows_controller.optimize_system_memory()
    # Also update system snapshot
    try:
        await system_monitor.update()
    except Exception:
        pass
    return result
