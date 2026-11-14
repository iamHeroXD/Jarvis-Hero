"""
Tier 1: Feature Coverage (Isolation / Happy Path) E2E Test Suite.
Verifies all primary subsystems in isolation:
1. FastAPI Health & Core Routes
2. Laptop Controller Tools
3. Directives Natural Execution Engine
4. Voice Endpoints & Service State
5. Self-Healing Traceback & AST Formulation
6. Desktop Frontend Static Serving
"""
from __future__ import annotations

import os
from pathlib import Path
import pytest
import httpx
from starlette.testclient import TestClient

from backend.app.core.config import PROJECT_ROOT, settings
from backend.app.tools.laptop_controller import laptop_controller
from backend.app.voice.voice_service import voice_service
from backend.app.evolution.self_healing import self_healing_engine, DiagnosticReport, CodePatch


# ══════════════════════════════════════════════════════════════════════════════
# Feature Area 1: FastAPI Health & Routes
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_root_health_check_returns_200(async_client: httpx.AsyncClient):
    """GET /health returns 200 OK with genuine system status and telemetry."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data
    assert "system" in data
    assert "components" in data
    assert data["components"]["database"] == "online"
    assert data["components"]["system_monitor"] == "online"


@pytest.mark.asyncio
async def test_detailed_health_endpoint(async_client: httpx.AsyncClient):
    """GET /api/v1/health returns detailed component health for dashboard."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["backend"] == "online"
    assert data["database"] == "online"
    assert "system" in data
    assert "gemini" in data
    assert "voice" in data


@pytest.mark.asyncio
async def test_system_metrics_endpoint(auth_client: httpx.AsyncClient):
    """GET /api/v1/system/metrics returns live hardware metrics."""
    response = await auth_client.get("/api/v1/system/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "cpu_percent" in data or "cpu" in data or "memory_percent" in data
    assert "status" in data or "timestamp" in data


@pytest.mark.asyncio
async def test_governor_status_endpoint(auth_client: httpx.AsyncClient):
    """GET /api/v1/governor/status returns governor state and particle limits."""
    response = await auth_client.get("/api/v1/governor/status")
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    assert data["profile"] in ["eco", "balanced", "performance"]
    assert "target_particle_count" in data or "particle_limit" in data


@pytest.mark.asyncio
async def test_auth_setup_status_endpoint(async_client: httpx.AsyncClient):
    """GET /api/v1/auth/setup-status returns setup status with owner_configured flag."""
    response = await async_client.get("/api/v1/auth/setup-status")
    assert response.status_code == 200
    data = response.json()
    assert "owner_configured" in data
    assert isinstance(data["owner_configured"], bool)


@pytest.mark.asyncio
async def test_tools_list_endpoint(auth_client: httpx.AsyncClient):
    """GET /api/v1/tools lists available computer control tools."""
    response = await auth_client.get("/api/v1/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "name" in data[0] or "tool_id" in data[0]


# ══════════════════════════════════════════════════════════════════════════════
# Feature Area 2: Laptop Tools
# ══════════════════════════════════════════════════════════════════════════════

def test_laptop_battery_telemetry():
    """LaptopController.get_battery_status returns valid power metrics."""
    res = laptop_controller.get_battery_status()
    assert res["success"] is True
    assert 0 <= res["percent"] <= 100
    assert isinstance(res["charging"], bool)
    assert isinstance(res["message"], str)
    assert len(res["message"]) > 0


def test_laptop_volume_up_action():
    """LaptopController.adjust_volume('up') executes virtual keystrokes."""
    res = laptop_controller.adjust_volume("up")
    assert res["success"] is True
    assert "increased" in res["message"].lower()


def test_laptop_volume_down_action():
    """LaptopController.adjust_volume('down') executes virtual keystrokes."""
    res = laptop_controller.adjust_volume("down")
    assert res["success"] is True
    assert "lowered" in res["message"].lower()


def test_laptop_volume_mute_action():
    """LaptopController.adjust_volume('mute') toggles mute state."""
    res = laptop_controller.adjust_volume("mute")
    assert res["success"] is True
    assert "mute" in res["message"].lower()


def test_laptop_system_diagnostics():
    """LaptopController.get_system_diagnostics compiles real hardware telemetry."""
    res = laptop_controller.get_system_diagnostics()
    assert res["success"] is True
    assert res["cpu"] >= 0
    assert res["ram"] >= 0
    assert res["disk_free_gb"] >= 0
    assert "Mark VII" in res["message"] or "systems" in res["message"].lower()


def test_laptop_folder_resolution():
    """LaptopController.open_folder resolves user shell folders."""
    res = laptop_controller.open_folder("downloads")
    assert res["success"] is True
    assert "explorer" in res["message"].lower() or "downloads" in res["message"].lower()


# ══════════════════════════════════════════════════════════════════════════════
# Feature Area 3: Directive Execution
# ══════════════════════════════════════════════════════════════════════════════

def test_directive_greeting():
    """execute_directive handles natural greetings."""
    res = laptop_controller.execute_directive("Good morning")
    assert res is not None
    assert res["success"] is True
    assert any(g in res["message"].lower() for g in ["morning", "afternoon", "evening", "systems"])


def test_directive_time():
    """execute_directive parses time queries."""
    res = laptop_controller.execute_directive("Jarvis, what time is it?")
    assert res is not None
    assert res["success"] is True
    assert "time is" in res["message"].lower() or ":" in res["message"]


def test_directive_date():
    """execute_directive parses date queries."""
    res = laptop_controller.execute_directive("What is today's date?")
    assert res is not None
    assert res["success"] is True
    assert "today is" in res["message"].lower() or "202" in res["message"]


def test_directive_battery():
    """execute_directive intercepts battery inquiries for instant telemetry."""
    res = laptop_controller.execute_directive("Jarvis, what is the battery level?")
    assert res is not None
    assert res["success"] is True
    assert "battery" in res["message"].lower() or "power" in res["message"].lower()


def test_directive_diagnostics():
    """execute_directive triggers system diagnostics report."""
    res = laptop_controller.execute_directive("Give me a system diagnostics briefing")
    assert res is not None
    assert res["success"] is True
    assert "cpu" in res


def test_directive_identity():
    """execute_directive identifies JARVIS role and capabilities."""
    res = laptop_controller.execute_directive("Who are you?")
    assert res is not None
    assert res["success"] is True
    assert "J.A.R.V.I.S." in res["message"]


def test_directive_volume_up():
    """execute_directive dispatches volume adjustment commands."""
    res = laptop_controller.execute_directive("Jarvis volume up please")
    assert res is not None
    assert res["success"] is True
    assert "increased" in res["message"].lower()


# ══════════════════════════════════════════════════════════════════════════════
# Feature Area 4: Voice Endpoints
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_voice_status_endpoint(auth_client: httpx.AsyncClient):
    """GET /api/v1/voice/status returns active voice engine parameters."""
    response = await auth_client.get("/api/v1/voice/status")
    assert response.status_code == 200
    data = response.json()
    assert "wake_word" in data
    assert "voice_name" in data
    assert "is_speaking" in data
    assert "is_listening" in data


@pytest.mark.asyncio
async def test_voice_interrupt_endpoint(auth_client: httpx.AsyncClient):
    """POST /api/v1/voice/interrupt halts active speech synthesis."""
    voice_service.is_speaking = True
    response = await auth_client.post("/api/v1/voice/interrupt")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "interrupted"
    assert data["is_speaking"] is False
    assert voice_service.is_speaking is False


@pytest.mark.asyncio
async def test_voice_speak_endpoint(auth_client: httpx.AsyncClient):
    """POST /api/v1/voice/speak returns audio WAV or graceful fallback."""
    response = await auth_client.post("/api/v1/voice/speak", json={"text": "All systems nominal, Sir."})
    assert response.status_code == 200
    if response.headers.get("content-type") == "audio/wav":
        assert len(response.content) > 100
    else:
        # Fallback JSON response when local audio hardware is in test mode
        data = response.json()
        assert data.get("status") in ["fallback", "ok"] or "text" in data


def test_voice_service_state_management():
    """VoiceService manages speaking state and barge-in cancellation."""
    voice_service.is_speaking = True
    assert voice_service.is_speaking is True
    voice_service.interrupt_speech()
    assert voice_service.is_speaking is False


@pytest.mark.asyncio
async def test_voice_service_synthesize_text():
    """VoiceService.synthesize_british_speech runs without unhandled exceptions."""
    result = await voice_service.synthesize_british_speech("J.A.R.V.I.S. online")
    # Returns audio bytes or None if neither cloud nor SAPI is configured on headless host
    assert result is None or isinstance(result, bytes)
    assert voice_service.is_speaking is False


# ══════════════════════════════════════════════════════════════════════════════
# Feature Area 5: Self-Healing Traceback & AST Formulation
# ══════════════════════════════════════════════════════════════════════════════

def test_self_healing_diagnose_syntax_traceback(tmp_path: Path):
    """SelfHealingEngine parses SyntaxError tracebacks accurately."""
    calc_file = tmp_path / "calc_test.py"
    calc_file.write_text("def calculate(x, y)\n    return x + y\n", encoding="utf-8")

    tb = (
        f'File "{calc_file}", line 1\n'
        '    def calculate(x, y)\n'
        '                       ^\n'
        'SyntaxError: expected \':\''
    )
    report = self_healing_engine.diagnose_traceback(tb, fallback_file=calc_file)
    assert report is not None
    assert report.error_type == "SyntaxError"
    assert report.line_number == 1
    assert "calc_test.py" in str(report.file_path)


def test_self_healing_diagnose_zero_division_traceback(tmp_path: Path):
    """SelfHealingEngine parses ZeroDivisionError tracebacks."""
    ops_file = tmp_path / "ops_test.py"
    ops_file.write_text("def divide(a, b):\n    return a / b\n", encoding="utf-8")

    tb = (
        f'File "{ops_file}", line 2, in divide\n'
        '    return a / b\n'
        'ZeroDivisionError: division by zero'
    )
    report = self_healing_engine.diagnose_traceback(tb, fallback_file=ops_file)
    assert report is not None
    assert report.error_type == "ZeroDivisionError"
    assert report.line_number == 2


def test_self_healing_diagnose_name_error_traceback(tmp_path: Path):
    """SelfHealingEngine parses NameError tracebacks."""
    handler_file = tmp_path / "handler_test.py"
    handler_file.write_text("def load():\n    return payload_config\n", encoding="utf-8")

    tb = (
        f'File "{handler_file}", line 2, in load\n'
        '    return payload_config\n'
        'NameError: name \'payload_config\' is not defined'
    )
    report = self_healing_engine.diagnose_traceback(tb, fallback_file=handler_file)
    assert report is not None
    assert report.error_type == "NameError"
    assert "payload_config" in report.error_message


def test_self_healing_formulate_missing_colon_patch(tmp_path: Path):
    """SelfHealingEngine generates a valid patch for missing colons."""
    test_file = tmp_path / "service_test.py"
    test_file.write_text("def execute_directive(action)\n    pass\n", encoding="utf-8")

    report = DiagnosticReport(
        error_type="SyntaxError",
        error_message="expected ':'",
        file_path=test_file,
        line_number=1,
        faulty_code="def execute_directive(action)",
        traceback_snippet="...",
    )
    patch = self_healing_engine.formulate_patch(report)
    assert patch is not None
    assert patch.replacement_snippet.rstrip().endswith(":")


def test_self_healing_formulate_zero_division_patch(tmp_path: Path):
    """SelfHealingEngine generates a safe denominator guard patch."""
    test_file = tmp_path / "math_test.py"
    test_file.write_text("def run_div(val, denominator):\n    return val / denominator\n", encoding="utf-8")

    report = DiagnosticReport(
        error_type="ZeroDivisionError",
        error_message="division by zero",
        file_path=test_file,
        line_number=2,
        faulty_code="return val / denominator",
        traceback_snippet="...",
    )
    patch = self_healing_engine.formulate_patch(report)
    assert patch is not None
    assert "if" in patch.replacement_snippet and "!= 0" in patch.replacement_snippet


def test_self_healing_syntax_sweep():
    """SelfHealingEngine scans codebase AST without raising exceptions."""
    results = self_healing_engine.scan_and_heal_syntax()
    assert isinstance(results, list)


# ══════════════════════════════════════════════════════════════════════════════
# Feature Area 6: Desktop Static Assets
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_desktop_root_serves_html(async_client: httpx.AsyncClient):
    """GET / serves the compiled React Single Page Application."""
    response = await async_client.get("/")
    assert response.status_code == 200
    content = response.text
    assert "<!DOCTYPE html>" in content or "<html" in content or "JARVIS" in content


@pytest.mark.asyncio
async def test_desktop_spa_route_serving(async_client: httpx.AsyncClient):
    """GET /{full_path} falls back to index.html for client-side routing."""
    response = await async_client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "<!DOCTYPE html>" in content or "<html" in content or "JARVIS" in content


@pytest.mark.asyncio
async def test_desktop_favicon_asset(async_client: httpx.AsyncClient):
    """GET /jarvis-icon.svg serves valid icon or fallback."""
    response = await async_client.get("/jarvis-icon.svg")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_desktop_assets_static_mount(async_client: httpx.AsyncClient):
    """GET /assets request handles static asset resolution without server error."""
    response = await async_client.get("/assets/index.css")
    # Returns 200 if css bundle exists, or 404/SPA fallback (never 500)
    assert response.status_code in [200, 404]


def test_desktop_dist_html_structure():
    """Verifies compiled desktop index.html contains necessary React mount point."""
    dist_index = PROJECT_ROOT / "apps" / "desktop" / "dist" / "index.html"
    if dist_index.exists():
        content = dist_index.read_text(encoding="utf-8")
        assert 'id="root"' in content
        assert "<script" in content
