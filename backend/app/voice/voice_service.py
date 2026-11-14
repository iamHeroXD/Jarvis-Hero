"""
JARVIS Voice & Speech Engine
Controls British masculine speech synthesis (TTS), speech-to-text (STT),
voice activity detection (VAD), barge-in interruption, and audio playback state.
Supports Gemini TTS with seamless local Windows SAPI fallback.
"""
from __future__ import annotations

import asyncio
import os
import tempfile
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
        """Synthesizes text to speech using Gemini TTS or high-fidelity local Windows SAPI."""
        self.is_speaking = True
        clean_text = text.replace("*", "").replace("#", "").replace("`", "").strip()
        try:
            # 1. Try Gemini TTS if configured
            try:
                audio_bytes = await gemini_provider.synthesise_speech(
                    text=clean_text,
                    voice_name=self.voice_name,
                )
                if audio_bytes:
                    return audio_bytes
            except Exception as e:
                logger.debug("Gemini TTS unavailable, falling back to local SAPI: %s", e)

            # 2. Local Windows SAPI SpVoice fallback (ultra-fast, zero latency)
            def generate_sapi_wav() -> bytes | None:
                try:
                    import win32com.client
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    # Try to find British voice if installed
                    for v in speaker.GetVoices():
                        desc = v.GetDescription()
                        if "United Kingdom" in desc or "George" in desc or "Ryan" in desc or "Hazel" in desc:
                            speaker.Voice = v
                            break

                    speaker.Rate = 0  # Normal conversational rate
                    speaker.Volume = int(settings.voice_volume * 100)

                    tmp_file = os.path.join(tempfile.gettempdir(), f"jarvis_speech_{os.getpid()}_{id(clean_text)}.wav")
                    stream = win32com.client.Dispatch("SAPI.SpFileStream")
                    stream.Open(tmp_file, 3, False)  # 3 = SSFMCreateForWrite
                    speaker.AudioOutputStream = stream
                    speaker.Speak(clean_text)
                    stream.Close()

                    if os.path.exists(tmp_file):
                        with open(tmp_file, "rb") as f:
                            data = f.read()
                        try:
                            os.remove(tmp_file)
                        except Exception:
                            pass
                        return data
                except Exception as ex:
                    logger.error("Local SAPI synthesis failed: %s", ex)
                    return None

            return await asyncio.to_thread(generate_sapi_wav)
        finally:
            self.is_speaking = False

    async def transcribe_speech(self, audio_data: bytes, mime_type: str = "audio/wav") -> str | None:
        """Transcribes incoming microphone audio bytes to text."""
        return await gemini_provider.transcribe_audio(audio_data=audio_data, mime_type=mime_type)


voice_service = VoiceService()
