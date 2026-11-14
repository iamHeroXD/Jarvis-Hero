"""API endpoints for Voice Interaction, British Male TTS, STT, and Speech Interruption."""
from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.models.database_models import User
from backend.app.voice.voice_service import voice_service

router = APIRouter()


class SpeakRequest(BaseModel):
    text: str


async def get_voice_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Authenticate user via JWT or fallback to local owner for desktop console."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        from backend.app.security.auth import verify_token
        payload = verify_token(token)
        if payload and payload.get("sub"):
            try:
                user_id = int(payload.get("sub"))
                res = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
                user = res.scalar_one_or_none()
                if user:
                    return user
            except Exception:
                pass

    # Local console fallback
    client_host = getattr(getattr(request, "client", None), "host", "127.0.0.1")
    if client_host in ("127.0.0.1", "localhost", "::1", "testclient"):
        res = await db.execute(select(User).where(User.is_owner == True).order_by(User.id.desc()))
        owner = res.scalars().first()
        if owner:
            return owner

    raise HTTPException(status_code=401, detail="Authentication required.")


@router.get("/status")
async def get_voice_status(current_user: Annotated[User, Depends(get_voice_user)]):
    """Returns current voice engine status, wake-word, and playback state."""
    return voice_service.get_status()


@router.post("/interrupt")
async def interrupt_speech(current_user: Annotated[User, Depends(get_voice_user)]):
    """Immediate barge-in cancellation: stops active TTS playback."""
    voice_service.interrupt_speech()
    return {"status": "interrupted", "is_speaking": False}


@router.post("/speak")
async def speak_text(
    data: SpeakRequest,
    current_user: Annotated[User, Depends(get_voice_user)],
):
    """Generates British male speech for text and returns audio bytes."""
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    audio_bytes = await voice_service.synthesize_british_speech(data.text)
    if not audio_bytes:
        return {"status": "fallback", "text": data.text, "audio": None}

    return Response(content=audio_bytes, media_type="audio/wav")
