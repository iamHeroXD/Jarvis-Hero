"""
JARVIS Core Configuration
Loads from environment variables and .env file.
Secrets (API keys) are NEVER stored in config files — always from Windows Credential Manager.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve project root (backend/app/core/config.py → project root is 3 levels up)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
DB_DIR = DATA_DIR / "db"
LOGS_DIR = DATA_DIR / "logs"
BACKUPS_DIR = DATA_DIR / "backups"


class JarvisSettings(BaseSettings):
    """Central application configuration. Loaded once at startup."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application Identity ──────────────────────────────────────────────
    app_name: str = "JARVIS"
    app_version: str = "0.1.0"
    app_codename: str = "Project J.A.R.V.I.S."
    debug: bool = Field(default=False, description="Enable debug logging")

    # ── Server ────────────────────────────────────────────────────────────
    backend_host: str = "127.0.0.1"
    backend_port: int = 8765
    backend_reload: bool = False  # only for development

    # ── Database ─────────────────────────────────────────────────────────
    database_url: str = f"sqlite+aiosqlite:///{DB_DIR / 'jarvis.db'}"
    database_echo: bool = False  # set True in debug to see SQL

    # ── Security ─────────────────────────────────────────────────────────
    secret_key: str = Field(
        default="CHANGE-ME-IN-PRODUCTION-USE-A-REAL-SECRET",
        description="JWT signing secret. Override via JARVIS_SECRET_KEY env var.",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # ── AI Provider ───────────────────────────────────────────────────────
    # API key comes from Windows Credential Manager, NOT from here.
    # This field is a runtime-populated cache only.
    gemini_api_key: str | None = Field(default=None, exclude=True)
    primary_model: str = "gemini-3.8-flash"
    reasoning_model: str = "gemini-4-argon"
    tts_model: str = "gemini-3.8-flash-tts"
    stt_model: str = "gemini-3.5-transcribe"
    local_model: str = "qwen2.5:1.5b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_enabled: bool = False

    # ── Voice ─────────────────────────────────────────────────────────────
    voice_enabled: bool = True
    wake_word: str = "jarvis"
    voice_speed: float = 1.0
    voice_volume: float = 0.9
    tts_voice_name: str = "Charon"  # British masculine Voice Design preset
    push_to_talk_key: str = "ctrl+space"

    # ── Personality ───────────────────────────────────────────────────────
    assistant_mode: Literal[
        "casual", "focus", "developer", "business", "study", "serious", "quiet"
    ] = "casual"
    owner_name: str = "Sir"  # How JARVIS addresses the owner

    # ── Memory ────────────────────────────────────────────────────────────
    memory_enabled: bool = True
    memory_max_tokens_per_context: int = 2000

    # ── Logging ───────────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_file: str = str(LOGS_DIR / "jarvis.log")
    log_max_size_mb: int = 10
    log_backup_count: int = 5

    # ── Resource Limits ───────────────────────────────────────────────────
    max_cpu_percent: float = 80.0
    max_ram_percent: float = 85.0
    background_indexing: bool = True

    # ── Startup ───────────────────────────────────────────────────────────
    startup_with_windows: bool = False
    minimise_to_tray: bool = True

    # ── Quiet Hours ───────────────────────────────────────────────────────
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"log_level must be one of {valid}")
        return upper


# Global singleton — import this everywhere
settings = JarvisSettings()


def ensure_data_dirs() -> None:
    """Create required data directories if they do not exist."""
    for d in [DATA_DIR, DB_DIR, LOGS_DIR, BACKUPS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
