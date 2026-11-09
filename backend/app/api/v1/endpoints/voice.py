"""API endpoints for Voice Interaction, British Male TTS, STT, and Speech Interruption."""
from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.models.database_models import User
from backend.app.voice.voice_service import voice_service

router = APIRouter()


class SpeakRequest(BaseModel):
    text: str


@router.get("/status")
async def get_voice_status(current_user: Annotated[User, Depends(get_current_user)]):
    """Returns current voice engine status, wake-word, and playback state."""
    return voice_service.get_status()


@router.post("/interrupt")
async def interrupt_speech(current_user: Annotated[User, Depends(get_current_user)]):
    """Immediate barge-in cancellation: stops active TTS playback."""
    voice_service.interrupt_speech()
    return {"status": "interrupted", "is_speaking": False}


@router.post("/speak")
async def speak_text(
    data: SpeakRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Generates British male speech for text and returns audio bytes."""
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    audio_bytes = await voice_service.synthesize_british_speech(data.text)
    if not audio_bytes:
        # Fallback response if offline / unconfigured
        return {"status": "fallback", "text": data.text, "audio": None}

    return Response(content=audio_bytes, media_type="audio/wav")
