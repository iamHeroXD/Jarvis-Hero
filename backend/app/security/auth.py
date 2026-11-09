"""
JARVIS Security Utilities
- JWT token creation and verification
- Password hashing
- Windows Credential Manager integration for API keys
- Permission level definitions
"""
from __future__ import annotations

import secrets
import sys
from datetime import UTC, datetime, timedelta
from enum import IntEnum
from typing import Any

import bcrypt
from jose import JWTError, jwt

from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger

logger = get_logger("security")


# ── Permission Levels ─────────────────────────────────────────────────────────

class PermissionLevel(IntEnum):
    """
    Tiered permission system enforced by the backend.
    Frontend cannot override or escalate these.
    """
    READ_ONLY = 0           # Read approved files, retrieve information
    REVERSIBLE_LOCAL = 1    # Open apps, create drafts, reminders
    CONFIRMED_MODIFY = 2    # Modify approved files, organise directories
    EXPLICIT_EXTERNAL = 3   # Send messages, publish, external actions
    RESTRICTED = 4          # NEVER available as normal AI tool


# ── JWT Helpers ───────────────────────────────────────────────────────────────

def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_token(token: str) -> dict[str, Any] | None:
    """
    Decode and verify a JWT.
    Returns the payload dict or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as exc:
        logger.warning("Token verification failed: %s", exc)
        return None


# ── Password Helpers ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Secure bcrypt password hashing with 72-byte max length handling."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Secure bcrypt hash verification."""
    try:
        plain_bytes = plain.encode("utf-8")[:72]
        return bcrypt.checkpw(plain_bytes, hashed.encode("utf-8"))
    except Exception:
        return False


def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


# ── Windows Credential Manager ────────────────────────────────────────────────

_KEYRING_SERVICE = "JARVIS"


def store_secret(key_name: str, value: str) -> bool:
    """
    Store a secret in Windows Credential Manager via keyring.
    Returns True on success.
    """
    try:
        import keyring
        keyring.set_password(_KEYRING_SERVICE, key_name, value)
        logger.info("Secret '%s' stored in Windows Credential Manager.", key_name)
        return True
    except Exception as exc:
        logger.error("Failed to store secret '%s': %s", key_name, exc)
        return False


def retrieve_secret(key_name: str) -> str | None:
    """
    Retrieve a secret from Windows Credential Manager.
    Returns None if not found or on error.
    """
    try:
        import keyring
        value = keyring.get_password(_KEYRING_SERVICE, key_name)
        return value
    except Exception as exc:
        logger.error("Failed to retrieve secret '%s': %s", key_name, exc)
        return None


def delete_secret(key_name: str) -> bool:
    """Delete a secret from Windows Credential Manager."""
    try:
        import keyring
        keyring.delete_password(_KEYRING_SERVICE, key_name)
        return True
    except Exception as exc:
        logger.warning("Failed to delete secret '%s': %s", key_name, exc)
        return False


def get_gemini_api_key() -> str | None:
    """Retrieve the Gemini API key from secure storage."""
    return retrieve_secret("gemini_api_key")


def set_gemini_api_key(api_key: str) -> bool:
    """Store the Gemini API key securely."""
    if not api_key or not api_key.strip():
        return False
    # Never log the actual key
    logger.info("Storing Gemini API key in Windows Credential Manager.")
    return store_secret("gemini_api_key", api_key.strip())
