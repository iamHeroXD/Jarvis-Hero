"""
JARVIS AI Router
Decides which provider handles each request based on:
- Request type and complexity
- Online/offline status
- Provider availability
- User configuration
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger

logger = get_logger("ai.router")


class ProviderName(str, Enum):
    GEMINI = "gemini"
    OLLAMA = "ollama"
    LOCAL_ACTION = "local_action"   # No AI needed — deterministic local service


class RequestType(str, Enum):
    COMPLEX_REASONING = "complex_reasoning"     # → Gemini (4-argon)
    GENERAL_CHAT = "general_chat"               # → Gemini flash
    CODE_ANALYSIS = "code_analysis"             # → Gemini (4-argon)
    RESEARCH = "research"                       # → Gemini flash
    BUSINESS = "business"                       # → Gemini flash
    SIMPLE_OFFLINE = "simple_offline"           # → Ollama (if available)
    MEMORY_RETRIEVAL = "memory_retrieval"       # → Local backend
    TASK_STATUS = "task_status"                 # → Local backend
    OPEN_APPLICATION = "open_application"       # → Local action service
    CREATE_REMINDER = "create_reminder"         # → Local backend
    SYSTEM_QUERY = "system_query"               # → Local backend


# Maps request types to preferred provider + model
_ROUTING_TABLE: dict[RequestType, dict[str, Any]] = {
    RequestType.COMPLEX_REASONING: {
        "provider": ProviderName.GEMINI,
        "model": settings.reasoning_model,  # gemini-4-argon
    },
    RequestType.GENERAL_CHAT: {
        "provider": ProviderName.GEMINI,
        "model": settings.primary_model,  # gemini-3.8-flash
    },
    RequestType.CODE_ANALYSIS: {
        "provider": ProviderName.GEMINI,
        "model": settings.reasoning_model,
    },
    RequestType.RESEARCH: {
        "provider": ProviderName.GEMINI,
        "model": settings.primary_model,
    },
    RequestType.BUSINESS: {
        "provider": ProviderName.GEMINI,
        "model": settings.primary_model,
    },
    RequestType.SIMPLE_OFFLINE: {
        "provider": ProviderName.OLLAMA,
        "model": settings.local_model,
    },
    RequestType.MEMORY_RETRIEVAL: {
        "provider": ProviderName.LOCAL_ACTION,
        "model": None,
    },
    RequestType.TASK_STATUS: {
        "provider": ProviderName.LOCAL_ACTION,
        "model": None,
    },
    RequestType.OPEN_APPLICATION: {
        "provider": ProviderName.LOCAL_ACTION,
        "model": None,
    },
    RequestType.CREATE_REMINDER: {
        "provider": ProviderName.LOCAL_ACTION,
        "model": None,
    },
    RequestType.SYSTEM_QUERY: {
        "provider": ProviderName.LOCAL_ACTION,
        "model": None,
    },
}


class AIRouter:
    """
    Central routing decision engine.
    Checks availability before routing — never blindly assumes a provider is up.
    """

    def __init__(self) -> None:
        self._internet_available: bool = True
        self._gemini_available: bool = False
        self._ollama_available: bool = False

    def update_connectivity(
        self,
        internet: bool,
        gemini: bool,
        ollama: bool,
    ) -> None:
        """Called by health monitor when connectivity changes."""
        self._internet_available = internet
        self._gemini_available = gemini
        self._ollama_available = ollama
        logger.info(
            "Connectivity updated: internet=%s gemini=%s ollama=%s",
            internet, gemini, ollama,
        )

    def route(self, request_type: RequestType) -> dict[str, Any]:
        """
        Return the actual provider and model to use for this request.
        Falls back gracefully if the preferred provider is unavailable.
        """
        preferred = _ROUTING_TABLE.get(request_type, _ROUTING_TABLE[RequestType.GENERAL_CHAT])
        provider = preferred["provider"]
        model = preferred["model"]

        # Local actions always work
        if provider == ProviderName.LOCAL_ACTION:
            return {"provider": provider, "model": model, "fallback": False}

        # Gemini requires internet + API key
        if provider == ProviderName.GEMINI:
            if self._gemini_available and self._internet_available:
                return {"provider": provider, "model": model, "fallback": False}
            # Fall back to Ollama if available
            if self._ollama_available and settings.ollama_enabled:
                logger.warning(
                    "Gemini unavailable for %s — falling back to Ollama.", request_type
                )
                return {
                    "provider": ProviderName.OLLAMA,
                    "model": settings.local_model,
                    "fallback": True,
                }
            # No AI available
            logger.error("No AI provider available for request type: %s", request_type)
            return {"provider": None, "model": None, "fallback": True, "unavailable": True}

        # Ollama
        if provider == ProviderName.OLLAMA:
            if self._ollama_available and settings.ollama_enabled:
                return {"provider": provider, "model": model, "fallback": False}
            if self._gemini_available and self._internet_available:
                return {
                    "provider": ProviderName.GEMINI,
                    "model": settings.primary_model,
                    "fallback": True,
                }
            return {"provider": None, "model": None, "fallback": True, "unavailable": True}

        return {"provider": None, "model": None, "fallback": True, "unavailable": True}

    @property
    def status(self) -> dict[str, Any]:
        return {
            "internet_available": self._internet_available,
            "gemini_available": self._gemini_available,
            "ollama_available": self._ollama_available,
        }


# Global singleton
ai_router = AIRouter()
