"""
JARVIS Voice & Speech Engine
Controls British masculine speech synthesis (TTS), speech-to-text (STT),
voice activity detection (VAD), barge-in interruption, and audio playback state.
"""
from __future__ import annotations

import asyncio
from typing import Any
from backend.app.ai.gemini_provider import gemini_provider
from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger

logger = get_logger("voice.service")


class VoiceService:
    """Manages audio recording, STT, British male TTS, and interruption handling."""

    def __init__(self) -> None:
        self.is_listening: bool = False
        self.is_speaking: bool = False
        self.wake_word: str = settings.wake_word
        self.voice_name: str = settings.tts_voice_name
        self._current_speech_task: asyncio.Task | None = None

    def get_status(self) -> dict[str, Any]:
        return {
            "enabled": settings.voice_enabled,
            "wake_word": self.wake_word,
            "voice_name": self.voice_name,
            "is_listening": self.is_listening,
            "is_speaking": self.is_speaking,
            "speed": settings.voice_speed,
            "volume": settings.voice_volume,
        }

    def interrupt_speech(self) -> None:
        """Immediate barge-in: cancels active speech playback when owner starts speaking."""
        if self._current_speech_task and not self._current_speech_task.done():
            self._current_speech_task.cancel()
        self.is_speaking = False
        logger.info("Speech playback interrupted by owner.")

    async def synthesize_british_speech(self, text: str) -> bytes | None:
        """Synthesizes text to speech using Gemini TTS with British masculine Voice Design."""
        self.is_speaking = True
        try:
            audio_bytes = await gemini_provider.synthesise_speech(
                text=text,
                voice_name=self.voice_name,
            )
            return audio_bytes
        finally:
            self.is_speaking = False

    async def transcribe_speech(self, audio_data: bytes, mime_type: str = "audio/wav") -> str | None:
        """Transcribes incoming microphone audio bytes to text."""
        return await gemini_provider.transcribe_audio(audio_data=audio_data, mime_type=mime_type)


voice_service = VoiceService()
