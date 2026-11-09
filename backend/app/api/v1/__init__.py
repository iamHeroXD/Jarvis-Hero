"""
JARVIS API v1 — Router aggregator
All versioned endpoints are collected here.
"""
from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    auth,
    health,
    conversations,
    memory,
    projects,
    tasks,
    settings as settings_router,
    system,
    ai,
    evolution,
    sentinel,
    governor,
    profiles,
    tools,
    agents,
    voice,
    automations,
    activity,
)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
router.include_router(memory.router, prefix="/memory", tags=["memory"])
router.include_router(projects.router, prefix="/projects", tags=["projects"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(settings_router.router, prefix="/settings", tags=["settings"])
router.include_router(system.router, prefix="/system", tags=["system"])
router.include_router(ai.router, prefix="/ai", tags=["ai"])
router.include_router(evolution.router, prefix="/evolution", tags=["evolution"])
router.include_router(sentinel.router, prefix="/sentinel", tags=["sentinel"])
router.include_router(governor.router, prefix="/governor", tags=["governor"])
router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
router.include_router(tools.router, prefix="/tools", tags=["tools"])
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(voice.router, prefix="/voice", tags=["voice"])
router.include_router(automations.router, prefix="/automations", tags=["automations"])
router.include_router(activity.router, prefix="/activity", tags=["activity"])
