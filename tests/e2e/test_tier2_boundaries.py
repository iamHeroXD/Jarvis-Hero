"""
Tier 2: Boundary & Corner Cases E2E Test Suite.
Verifies boundary conditions, error handling, input sanitization, and resilience:
1. Empty / Malformed Directive Strings
2. Extreme & Invalid Volume Adjustments
3. Non-Existent Application & Shortcut Lookups
4. Voice Payload Validation & Rapid Interrupts
5. WebSocket Malformed Payloads & Auth Boundaries
6. Self-Healing Unparseable / Non-Existent Files
7. 404 API Boundaries vs SPA Client Routing Fallback
8. Unicode, Emojis, and Format-Specific Meta-Characters
"""
from __future__ import annotations

import asyncio
from pathlib import Path
import pytest
import httpx
from starlette.testclient import TestClient

from backend.app.tools.laptop_controller import laptop_controller
from backend.app.tools.app_launcher import app_launcher
from backend.app.voice.voice_service import voice_service
from backend.app.evolution.self_healing import self_healing_engine


# ══════════════════════════════════════════════════════════════════════════════
# 1. Directive String Boundaries
# ══════════════════════════════════════════════════════════════════════════════

def test_directive_empty_string_returns_none():
    """Empty prompt string is safely ignored by directive parser."""
    assert laptop_controller.execute_directive("") is None


def test_directive_whitespace_only_returns_none():
    """Whitespace-only prompt string is safely ignored."""
    assert laptop_controller.execute_directive("    \t\r\n   ") is None


def test_directive_gibberish_and_symbols_returns_none():
    """Random punctuation and symbols do not raise exceptions."""
    result = laptop_controller.execute_directive("!@#$%^&*()_+~`|}{[]:;?><,./")
    assert result is None


def test_directive_excessive_length():
    """Oversized directive string is handled safely without buffer overflow."""
    oversized = "please " * 500 + "battery"
    res = laptop_controller.execute_directive(oversized)
    # Either successfully detects "battery" or safely falls through to LLM
    assert res is None or res.get("success") is True


def test_directive_null_and_undefined_literals():
    """Literal 'null' and 'undefined' strings do not trigger directives."""
    assert laptop_controller.execute_directive("null") is None
    assert laptop_controller.execute_directive("undefined") is None


def test_directive_unicode_and_emojis():
    """Directive parser handles emojis and unicode cleanly."""
    res = laptop_controller.execute_directive("🤖 Jarvis what is the time ⏰")
    assert res is not None
    assert res["success"] is True
    assert "time is" in res["message"].lower() or ":" in res["message"]


def test_directive_control_characters_resilience():
    """Directive parser handles control characters safely."""
    control_str = "Jarvis \x00\x01\x02\x03 what time is it?"
    res = laptop_controller.execute_directive(control_str)
    assert res is not None
    assert res["success"] is True


# ══════════════════════════════════════════════════════════════════════════════
# 2. Extreme & Invalid Volume Adjustments
# ══════════════════════════════════════════════════════════════════════════════

def test_volume_invalid_action_returns_error():
    """Non-standard volume commands return descriptive error status."""
    res = laptop_controller.adjust_volume("turbo_boost_1000")
    assert res["success"] is False
    assert "unknown volume action" in res["message"].lower()


def test_volume_empty_action_returns_error():
    """Empty volume action string is rejected cleanly."""
    res = laptop_controller.adjust_volume("")
    assert res["success"] is False
    assert "unknown volume action" in res["message"].lower()


def test_volume_numeric_percentage_strings():
    """Numeric percentages are rejected with clear error rather than crashing."""
    res = laptop_controller.adjust_volume("150%")
    assert res["success"] is False
    assert "unknown volume action" in res["message"].lower()


def test_volume_whitespace_and_mixed_case():
    """Volume command trims whitespace and normalizes casing."""
    res = laptop_controller.adjust_volume("   UP  ")
    assert res["success"] is True
    assert "increased" in res["message"].lower()


# ══════════════════════════════════════════════════════════════════════════════
# 3. Non-Existent Application & Shortcut Lookups
# ══════════════════════════════════════════════════════════════════════════════

def test_launch_nonexistent_application():
    """LaptopController dispatches shell fallback without unhandled exception."""
    res = laptop_controller.launch_app("hyperdrive_quantum_accelerator_99999")
    assert isinstance(res, dict)
    assert "message" in res
    assert "hyperdrive_quantum_accelerator_99999" in res["message"].lower() or "direct dispatch" in res["message"].lower()


def test_strict_launcher_rejects_unapproved_app():
    """AppLauncher strictly rejects applications outside whitelist."""
    unapproved = app_launcher.launch("malicious_unapproved_trojan")
    assert unapproved["success"] is False
    assert "not in the approved" in unapproved["error"].lower()


def test_close_nonexistent_application():
    """Closing an unmanaged application returns structured status."""
    res = laptop_controller.close_app("nonexistent_mock_process_99999")
    assert isinstance(res, dict)
    assert "success" in res


# ══════════════════════════════════════════════════════════════════════════════
# 4. Voice Payload Validation & Rapid Interrupts
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_voice_speak_empty_text_returns_400(auth_client: httpx.AsyncClient):
    """POST /api/v1/voice/speak rejects empty text payload with 400."""
    response = await auth_client.post("/api/v1/voice/speak", json={"text": ""})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_voice_speak_whitespace_only_returns_400(auth_client: httpx.AsyncClient):
    """POST /api/v1/voice/speak rejects whitespace-only string."""
    response = await auth_client.post("/api/v1/voice/speak", json={"text": "   \n\t  "})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_voice_speak_missing_field_returns_422(auth_client: httpx.AsyncClient):
    """POST /api/v1/voice/speak without 'text' field returns 422 Unprocessable Entity."""
    response = await auth_client.post("/api/v1/voice/speak", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_voice_rapid_consecutive_interrupts(auth_client: httpx.AsyncClient):
    """Multiple rapid barge-in interrupt requests resolve safely without race condition."""
    for _ in range(15):
        response = await auth_client.post("/api/v1/voice/interrupt")
        assert response.status_code == 200
        assert response.json()["status"] == "interrupted"
    assert voice_service.is_speaking is False


# ══════════════════════════════════════════════════════════════════════════════
# 5. WebSocket Malformed Payloads & Auth Boundaries
# ══════════════════════════════════════════════════════════════════════════════

def test_websocket_chat_malformed_json(test_client: TestClient):
    """WebSocket handles malformed non-JSON string with structured error response."""
    with test_client.websocket_connect("/api/v1/conversations/ws/chat") as ws:
        ws.send_text("{broken: json payload")
        resp = ws.receive_json()
        assert resp["type"] == "error"
        assert "invalid json" in resp["message"].lower()


def test_websocket_chat_missing_token(test_client: TestClient):
    """WebSocket rejects message missing authentication token."""
    with test_client.websocket_connect("/api/v1/conversations/ws/chat") as ws:
        ws.send_json({"message": "Hello Jarvis"})
        resp = ws.receive_json()
        assert resp["type"] == "error"
        assert "authentication required" in resp["message"].lower()


def test_websocket_chat_invalid_token(test_client: TestClient):
    """WebSocket rejects message with invalid or expired token."""
    with test_client.websocket_connect("/api/v1/conversations/ws/chat") as ws:
        ws.send_json({"token": "invalid.jwt.signature", "message": "Hello"})
        resp = ws.receive_json()
        assert resp["type"] == "error"
        assert "invalid or expired" in resp["message"].lower()


def test_websocket_chat_immediate_disconnect(test_client: TestClient):
    """Client disconnects immediately after handshake without server crash."""
    with test_client.websocket_connect("/api/v1/conversations/ws/chat") as ws:
        pass  # Context exit immediately closes socket cleanly


# ══════════════════════════════════════════════════════════════════════════════
# 6. Self-Healing Unparseable / Non-Existent Files
# ══════════════════════════════════════════════════════════════════════════════

def test_self_healing_nonexistent_file(tmp_path: Path):
    """Diagnose and repair on non-existent Path returns structured failure."""
    ghost_path = tmp_path / "ghost_file_does_not_exist_9999.py"
    res = self_healing_engine.diagnose_and_repair(
        error_input=f'File "{ghost_path}", line 1\nSyntaxError: invalid syntax',
        target_file=ghost_path,
    )
    assert res.success is False
    assert res.verification_passed is False or "not found" in res.message.lower()


def test_self_healing_binary_file(tmp_path: Path):
    """Self-healing rejects or safely ignores non-UTF-8 binary data."""
    bin_file = tmp_path / "compiled_artifact.bin"
    bin_file.write_bytes(b"\x00\xff\xfe\x00\x12\x34\x56\x78\xaa\xbb")

    res = self_healing_engine.diagnose_and_repair(
        error_input=f'File "{bin_file}", line 1\nSyntaxError: invalid syntax',
        target_file=bin_file,
    )
    # Verifies binary is preserved without crashing
    assert res.success is False
    assert bin_file.exists()


def test_self_healing_empty_traceback():
    """Empty traceback returns None or safe default without exception."""
    res = self_healing_engine.diagnose_traceback("")
    assert res is None or res.error_type in ["UnknownError", "SyntaxError"]


# ══════════════════════════════════════════════════════════════════════════════
# 7. 404 API Boundaries vs SPA Client Routing Fallback
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_api_v1_nonexistent_post_route_returns_404_or_405(async_client: httpx.AsyncClient):
    """Non-existent POST routes under /api/v1 return standard 404 or 405, never SPA HTML."""
    response = await async_client.post("/api/v1/nonexistent_system_subsystem", json={})
    assert response.status_code in [404, 405]


@pytest.mark.asyncio
async def test_spa_nested_frontend_route_fallback(async_client: httpx.AsyncClient):
    """Client-side routing URLs return index.html for React SPA mounting."""
    response = await async_client.get("/settings/neural-core/visualizer")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text or "<html" in response.text


@pytest.mark.asyncio
async def test_governor_invalid_profile_returns_422(auth_client: httpx.AsyncClient):
    """POST /api/v1/governor/set-profile rejects invalid power profile with 422."""
    response = await auth_client.post("/api/v1/governor/set-profile", json={"profile": "extreme_overclock"})
    assert response.status_code == 422
