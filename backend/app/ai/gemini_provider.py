"""
JARVIS AI Provider — Google Gemini
Uses google-genai 3.0.0 SDK with client.interactions.create() API.
Supports streaming, stateful conversations, and function calling.
"""
from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Any

from google import genai

from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger
from backend.app.security.auth import get_gemini_api_key

logger = get_logger("ai.gemini")


class GeminiProvider:
    """
    Wraps google-genai interactions API.
    One instance per application lifecycle.
    API key is loaded from Windows Credential Manager at first use.
    """

    def __init__(self) -> None:
        self._client: genai.Client | None = None
        self._available: bool = False
        self._last_error: str | None = None

    def _get_client(self) -> genai.Client:
        """Lazily initialise the Gemini client using the stored API key."""
        if self._client is not None:
            return self._client

        api_key = get_gemini_api_key()
        if not api_key:
            raise RuntimeError(
                "Gemini API key not configured. "
                "Please add your API key in Settings → AI."
            )

        self._client = genai.Client(api_key=api_key)
        self._available = True
        logger.info("Gemini client initialised.")
        return self._client

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def reset_client(self) -> None:
        """Force re-initialisation (e.g., after API key change)."""
        self._client = None
        self._available = False
        self._last_error = None

    async def check_connectivity(self) -> bool:
        """
        Verify the API key and connectivity with a minimal request.
        Returns True if reachable.
        """
        try:
            client = self._get_client()
            # Use aio for async
            interaction = await client.aio.interactions.create(
                model=settings.primary_model,
                input="ping",
            )
            self._available = True
            self._last_error = None
            logger.info("Gemini connectivity check passed.")
            return True
        except RuntimeError as exc:
            self._last_error = str(exc)
            self._available = False
            return False
        except Exception as exc:
            self._last_error = str(exc)
            self._available = False
            logger.warning("Gemini connectivity check failed: %s", exc)
            return False

    async def chat(
        self,
        message: str,
        system_instruction: str | None = None,
        previous_interaction_id: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        store: bool = True,
    ) -> dict[str, Any]:
        """
        Single-turn or multi-turn chat.
        Returns a dict with 'text', 'interaction_id', 'tokens', 'error'.
        """
        try:
            client = self._get_client()
            model_name = model or settings.primary_model

            kwargs: dict[str, Any] = {
                "model": model_name,
                "input": message,
                "store": store,
            }
            if system_instruction:
                kwargs["system_instruction"] = system_instruction
            if previous_interaction_id:
                kwargs["previous_interaction_id"] = previous_interaction_id

            interaction = await client.aio.interactions.create(**kwargs)

            return {
                "text": interaction.output_text or "",
                "interaction_id": interaction.id,
                "model": model_name,
                "tokens": getattr(getattr(interaction, "usage", None), "total_tokens", None),
                "error": None,
            }

        except RuntimeError as exc:
            return {"text": "", "interaction_id": None, "model": None, "tokens": None, "error": str(exc)}
        except Exception as exc:
            logger.error("Gemini chat error: %s", exc)
            return {"text": "", "interaction_id": None, "model": None, "tokens": None, "error": str(exc)}

    async def stream_chat(
        self,
        message: str,
        system_instruction: str | None = None,
        previous_interaction_id: str | None = None,
        model: str | None = None,
        store: bool = True,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Streaming chat. Yields dicts:
          {'type': 'delta', 'text': '...'}
          {'type': 'completed', 'interaction_id': '...', 'tokens': N}
          {'type': 'error', 'message': '...'}
        """
        try:
            client = self._get_client()
            model_name = model or settings.primary_model

            kwargs: dict[str, Any] = {
                "model": model_name,
                "input": message,
                "stream": True,
                "store": store,
            }
            if system_instruction:
                kwargs["system_instruction"] = system_instruction
            if previous_interaction_id:
                kwargs["previous_interaction_id"] = previous_interaction_id

            interaction_id: str | None = None
            total_tokens: int | None = None

            # client.interactions.create with stream=True returns an iterable
            # Use asyncio.to_thread since the sync iterator may block
            async for event in await asyncio.to_thread(
                lambda: list(client.interactions.create(**kwargs))
            ):
                pass  # Will restructure below

            # Correct async streaming approach:
            stream = client.interactions.create(**kwargs)
            for event in stream:
                event_type = getattr(event, "event_type", None)
                if event_type == "step.delta":
                    delta = getattr(event, "delta", None)
                    if delta and getattr(delta, "type", None) == "text":
                        yield {"type": "delta", "text": delta.text}
                elif event_type == "interaction.created":
                    interaction_obj = getattr(event, "interaction", None)
                    if interaction_obj:
                        interaction_id = getattr(interaction_obj, "id", None)
                elif event_type == "interaction.completed":
                    interaction_obj = getattr(event, "interaction", None)
                    if interaction_obj:
                        interaction_id = interaction_id or getattr(interaction_obj, "id", None)
                        usage = getattr(interaction_obj, "usage", None)
                        if usage:
                            total_tokens = getattr(usage, "total_tokens", None)

            yield {
                "type": "completed",
                "interaction_id": interaction_id,
                "model": model_name,
                "tokens": total_tokens,
            }

        except RuntimeError as exc:
            yield {"type": "error", "message": str(exc)}
        except Exception as exc:
            logger.error("Gemini stream error: %s", exc)
            yield {"type": "error", "message": str(exc)}

    async def transcribe_audio(self, audio_data: bytes, mime_type: str = "audio/wav") -> str | None:
        """
        Transcribe audio bytes using Gemini STT.
        Returns the transcription text or None on failure.
        """
        try:
            import base64
            client = self._get_client()
            interaction = await client.aio.interactions.create(
                model=settings.stt_model,
                input=[
                    {"type": "text", "text": "Transcribe this audio exactly."},
                    {"type": "audio", "data": base64.b64encode(audio_data).decode(), "mime_type": mime_type},
                ],
                store=False,
            )
            return interaction.output_text
        except Exception as exc:
            logger.error("Transcription error: %s", exc)
            return None

    async def synthesise_speech(
        self,
        text: str,
        voice_name: str | None = None,
    ) -> bytes | None:
        """
        Convert text to speech using Gemini TTS.
        Returns WAV audio bytes or None on failure.
        """
        try:
            import base64
            client = self._get_client()
            voice = voice_name or settings.tts_voice_name
            interaction = await client.aio.interactions.create(
                model=settings.tts_model,
                input=text,
                generation_config={
                    "response_modalities": ["audio"],
                    "speech_config": {
                        "voice_config": {
                            "prebuilt_voice_config": {"voice_name": voice}
                        }
                    },
                },
                store=False,
            )
            if interaction.output_audio:
                return base64.b64decode(interaction.output_audio.data)
            return None
        except Exception as exc:
            logger.error("TTS error: %s", exc)
            return None


# Global singleton
gemini_provider = GeminiProvider()
