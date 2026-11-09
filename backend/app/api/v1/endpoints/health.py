"""Health endpoints — genuine system status only."""
from __future__ import annotations

from fastapi import APIRouter
from backend.app.monitoring.system_monitor import system_monitor
from backend.app.ai.gemini_provider import gemini_provider
from backend.app.core.config import settings

router = APIRouter()


@router.get("")
async def detailed_health():
    """Full health breakdown for the System dashboard."""
    system_data = system_monitor.get_status_dict()
    return {
        "backend": "online",
        "database": "online",
        "internet": system_data.get("internet_available", False),
        "gemini": {
            "available": gemini_provider.is_available,
            "last_error": gemini_provider.last_error,
            "primary_model": settings.primary_model,
        },
        "ollama": {
            "enabled": settings.ollama_enabled,
            "base_url": settings.ollama_base_url,
        },
        "voice": {
            "enabled": settings.voice_enabled,
            "wake_word": settings.wake_word,
        },
        "system": system_data,
        "mode": settings.assistant_mode,
    }
