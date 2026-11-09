"""AI provider endpoints — status and routing info."""
from fastapi import APIRouter, Depends
from typing import Annotated
from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.models.database_models import User
from backend.app.ai.gemini_provider import gemini_provider
from backend.app.ai.router import ai_router
from backend.app.core.config import settings

router = APIRouter()

@router.get("/status")
async def ai_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {
        "gemini": {
            "available": gemini_provider.is_available,
            "last_error": gemini_provider.last_error,
            "primary_model": settings.primary_model,
            "reasoning_model": settings.reasoning_model,
        },
        "ollama": {
            "enabled": settings.ollama_enabled,
            "model": settings.local_model,
        },
        "router": ai_router.status,
    }
