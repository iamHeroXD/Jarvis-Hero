"""
Settings endpoints.
Handles AI configuration including Gemini API key storage.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import require_owner
from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger
from backend.app.models.database_models import User
from backend.app.security.auth import set_gemini_api_key, get_gemini_api_key
from backend.app.ai.gemini_provider import gemini_provider

router = APIRouter()
logger = get_logger("api.settings")


class GeminiKeyRequest(BaseModel):
    api_key: str


class GeminiKeyResponse(BaseModel):
    configured: bool
    masked_key: str | None = None


@router.get("/ai/gemini", response_model=GeminiKeyResponse)
async def gemini_status(current_user: Annotated[User, Depends(require_owner)]):
    """Check if Gemini API key is configured. Never returns the actual key."""
    key = get_gemini_api_key()
    if key:
        masked = key[:8] + "..." + key[-4:]
        return GeminiKeyResponse(configured=True, masked_key=masked)
    return GeminiKeyResponse(configured=False)


@router.post("/ai/gemini")
async def set_gemini_key(
    data: GeminiKeyRequest,
    current_user: Annotated[User, Depends(require_owner)],
):
    """
    Store the Gemini API key in Windows Credential Manager.
    The key is never echoed back or logged.
    """
    if not data.api_key.strip():
        raise HTTPException(400, "API key cannot be empty.")

    success = set_gemini_api_key(data.api_key)
    if not success:
        raise HTTPException(500, "Failed to store API key in Windows Credential Manager.")

    # Reset the Gemini client so it picks up the new key
    gemini_provider.reset_client()
    logger.info("Gemini API key updated by owner.")

    return {"message": "API key stored securely. JARVIS will use it for all Gemini requests."}


@router.post("/ai/gemini/test")
async def test_gemini_connection(current_user: Annotated[User, Depends(require_owner)]):
    """Test the Gemini connection with the stored key."""
    success = await gemini_provider.check_connectivity()
    if success:
        return {"status": "connected", "model": settings.primary_model}
    return {"status": "failed", "error": gemini_provider.last_error}


@router.get("/general")
async def get_general_settings(current_user: Annotated[User, Depends(require_owner)]):
    """Return current non-secret settings."""
    return {
        "assistant_mode": settings.assistant_mode,
        "owner_name": settings.owner_name,
        "voice_enabled": settings.voice_enabled,
        "wake_word": settings.wake_word,
        "primary_model": settings.primary_model,
        "ollama_enabled": settings.ollama_enabled,
        "startup_with_windows": settings.startup_with_windows,
        "quiet_hours_enabled": settings.quiet_hours_enabled,
        "quiet_hours_start": settings.quiet_hours_start,
        "quiet_hours_end": settings.quiet_hours_end,
    }
