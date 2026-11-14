"""
JARVIS AI Provider — Google Gemini
Uses official google-genai SDK with streaming, fallback model cascading,
and multi-turn conversational memory.
"""
from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Any

from google import genai
from google.genai import types

from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger
from backend.app.security.auth import get_gemini_api_key

logger = get_logger("ai.gemini")

CANDIDATE_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
]


class GeminiProvider:
    """
    Wraps google-genai models API with cascading fallback and streaming.
    API key is loaded from Windows Credential Manager.
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
                "Please configure your API key in Settings."
            )

        self._client = genai.Client(api_key=api_key)
        self._available = True
        logger.info("Gemini client initialised successfully.")
        return self._client

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def reset_client(self) -> None:
        """Force re-initialisation (e.g. after API key change)."""
        self._client = None
        self._available = False
        self._last_error = None

    async def check_connectivity(self) -> bool:
        """Verify the API key and connectivity with a minimal request."""
        try:
            client = self._get_client()
            res = await asyncio.to_thread(
                lambda: client.models.generate_content(
                    model=settings.primary_model,
                    contents="ping",
                )
            )
            if res and res.text:
                self._available = True
                self._last_error = None
                from backend.app.ai.router import ai_router
                ai_router.update_connectivity(internet=True, gemini=True, ollama=settings.ollama_enabled)
                logger.info("Gemini connectivity verified online.")
                return True
            return False
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("Gemini connectivity check failed: %s", exc)
            return False

    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Convenience method for one-shot text generation."""
        return await self.chat(
            message=prompt,
            system_instruction=system_instruction,
            **kwargs,
        )

    async def chat(
        self,
        message: str,
        system_instruction: str | None = None,
        previous_interaction_id: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        store: bool = True,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        Chat with fallback model cascading and multi-turn conversational memory.
        """
        try:
            client = self._get_client()
        except RuntimeError as exc:
            return {"text": "", "interaction_id": None, "model": None, "tokens": None, "error": str(exc)}

        models_to_try = [model or settings.primary_model] + [
            m for m in CANDIDATE_MODELS if m != (model or settings.primary_model)
        ]

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=1024,
            system_instruction=system_instruction or (
                "You are J.A.R.V.I.S., an extraordinarily capable, witty, loyal, "
                "and intelligent personal AI assistant to your owner, Rohan. Speak with British elegance. "
                "Provide complete, direct, intelligent responses."
            ),
        )

        contents_list: list[Any] = []
        if history:
            for item in history:
                role = "user" if item.get("role") in ("user", "human") else "model"
                text = item.get("text") or item.get("content") or ""
                if text.strip():
                    contents_list.append(types.Content(role=role, parts=[types.Part.from_text(text=text.strip())]))
        contents_list.append(types.Content(role="user", parts=[types.Part.from_text(text=message.strip())]))

        last_err: Exception | None = None
        for candidate_model in models_to_try:
            try:
                response = await asyncio.to_thread(
                    lambda: client.models.generate_content(
                        model=candidate_model,
                        contents=contents_list,
                        config=config,
                    )
                )
                text = response.text or ""
                self._available = True
                return {
                    "text": text,
                    "interaction_id": None,
                    "model": candidate_model,
                    "tokens": None,
                    "error": None,
                }
            except Exception as err:
                last_err = err
                logger.warning("Model %s failed in chat: %s. Trying next...", candidate_model, err)
                continue

        error_msg = str(last_err) if last_err else "Failed to generate AI response."
        return {"text": "", "interaction_id": None, "model": None, "tokens": None, "error": error_msg}

    async def stream_chat(
        self,
        message: str,
        system_instruction: str | None = None,
        previous_interaction_id: str | None = None,
        model: str | None = None,
        store: bool = True,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Real-time streaming chat with fallback cascading and conversational memory.
        Yields {'type': 'delta', 'text': '...'} and {'type': 'completed', ...}.
        """
        try:
            client = self._get_client()
        except RuntimeError as exc:
            yield {"type": "error", "message": str(exc)}
            return

        models_to_try = [model or settings.primary_model] + [
            m for m in CANDIDATE_MODELS if m != (model or settings.primary_model)
        ]

        config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1024,
            system_instruction=system_instruction or (
                "You are J.A.R.V.I.S., an extraordinarily capable, witty, loyal, "
                "and intelligent personal AI assistant to your owner, Rohan. Keep spoken answers engaging, "
                "direct, and speak with authentic British charm."
            ),
        )

        contents_list: list[Any] = []
        if history:
            for item in history:
                role = "user" if item.get("role") in ("user", "human") else "model"
                text = item.get("text") or item.get("content") or ""
                if text.strip():
                    contents_list.append(types.Content(role=role, parts=[types.Part.from_text(text=text.strip())]))
        contents_list.append(types.Content(role="user", parts=[types.Part.from_text(text=message.strip())]))

        succeeded = False
        last_err: Exception | None = None

        for candidate_model in models_to_try:
            try:
                def get_stream():
                    return client.models.generate_content_stream(
                        model=candidate_model,
                        contents=contents_list,
                        config=config,
                    )

                stream = await asyncio.to_thread(get_stream)

                for chunk in stream:
                    if chunk and chunk.text:
                        yield {"type": "delta", "text": chunk.text}

                succeeded = True
                self._available = True
                yield {
                    "type": "completed",
                    "interaction_id": None,
                    "model": candidate_model,
                    "tokens": None,
                }
                break
            except Exception as err:
                last_err = err
                logger.warning("Stream with %s failed: %s. Trying next...", candidate_model, err)
                continue

        if not succeeded:
            error_msg = str(last_err) if last_err else "Stream generation failed."
            yield {"type": "error", "message": error_msg}

    async def transcribe_audio(self, audio_data: bytes, mime_type: str = "audio/wav") -> str | None:
        """
        Transcribe audio bytes using Gemini Multimodal Audio.
        """
        try:
            client = self._get_client()
            res = await asyncio.to_thread(
                lambda: client.models.generate_content(
                    model=settings.primary_model,
                    contents=[
                        types.Part.from_bytes(data=audio_data, mime_type=mime_type),
                        "Transcribe the spoken audio exactly. Return only the transcription text.",
                    ],
                )
            )
            return res.text.strip() if res and res.text else None
        except Exception as exc:
            logger.error("Transcription error: %s", exc)
            return None

    async def synthesise_speech(
        self,
        text: str,
        voice_name: str | None = None,
    ) -> bytes | None:
        """
        Convert text to speech using Windows SAPI 5 fallback or Gemini audio generation.
        Returns WAV audio bytes or None on failure.
        """
        try:
            from backend.app.voice.voice_service import voice_service
            return await voice_service.synthesize_speech(text)
        except Exception as exc:
            logger.error("TTS error: %s", exc)
            return None


# Global singleton
gemini_provider = GeminiProvider()
