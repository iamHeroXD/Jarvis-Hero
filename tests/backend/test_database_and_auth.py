"""
Automated tests for Database Session, User Authentication, Password Hashing,
and JWT verification in JARVIS.
"""
from __future__ import annotations

import pytest
from backend.app.security.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)


def test_password_hashing():
    raw = "JarvisSecret2026!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_generation_and_validation():
    payload = {"sub": 42, "role": "owner"}
    token = create_access_token(payload)
    assert isinstance(token, str) and len(token) > 20

    decoded = verify_token(token)
    assert decoded is not None
    assert int(decoded.get("sub")) == 42
    assert decoded.get("role") == "owner"


def test_invalid_jwt():
    assert verify_token("invalid.token.here") is None
