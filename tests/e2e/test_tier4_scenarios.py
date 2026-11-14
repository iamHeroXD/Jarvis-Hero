"""
Tier 4: Real-World Application Scenarios E2E Test Suite.
Verifies complete operational workflows across end-to-end subsystems:
1. Assistant Morning Briefing Workflow
2. Volume Control Workflow
3. Vocal Barge-In Workflow
4. Autonomous Self-Healing Incident Recovery Workflow
5. Desktop App Serving & Health Verification Workflow
"""
from __future__ import annotations

import asyncio
from pathlib import Path
import pytest
import httpx
from starlette.testclient import TestClient

from backend.app.tools.laptop_controller import laptop_controller
from backend.app.voice.voice_service import voice_service
from backend.app.evolution.self_healing import self_healing_engine
from backend.app.tasks.reminders import reminder_manager


# ══════════════════════════════════════════════════════════════════════════════
# Scenario 1: Assistant Morning Briefing Workflow
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_scenario_morning_briefing_workflow(auth_client: httpx.AsyncClient):
    """
    Workflow 1: Morning Briefing.
    Simulates multi-turn session where user greets JARVIS, queries the time,
    checks battery power, gathers hardware telemetry, and receives a tactical briefing.
    """
    # Turn 1: Greeting
    greet_resp = await auth_client.post("/api/v1/conversations/chat", json={"message": "Jarvis, good morning"})
    assert greet_resp.status_code == 200
    greet_data = greet_resp.json()
    convo_id = greet_data["conversation_id"]
    assert len(greet_data["reply"]) > 0
    assert any(g in greet_data["reply"].lower() for g in ["morning", "afternoon", "evening", "systems", "sir", "hello", "service"])

    # Turn 2: Query Time
    time_resp = await auth_client.post(
        "/api/v1/conversations/chat",
        json={"message": "What time is it?", "conversation_id": convo_id},
    )
    assert time_resp.status_code == 200
    assert "time is" in time_resp.json()["reply"].lower() or ":" in time_resp.json()["reply"]

    # Turn 3: Check Battery & Hardware Telemetry
    bat_resp = await auth_client.post(
        "/api/v1/conversations/chat",
        json={"message": "Check battery status", "conversation_id": convo_id},
    )
    assert bat_resp.status_code == 200
    assert "battery" in bat_resp.json()["reply"].lower() or "power" in bat_resp.json()["reply"].lower()

    # Turn 4: System Diagnostics Briefing
    diag_resp = await auth_client.post(
        "/api/v1/conversations/chat",
        json={"message": "System diagnostics briefing", "conversation_id": convo_id},
    )
    assert diag_resp.status_code == 200
    assert "cpu" in diag_resp.json()["reply"].lower() or "mark vii" in diag_resp.json()["reply"].lower()

    # Turn 5: Smart Reminders & Daily Briefing Generation
    reminder_manager.add_reminder(
        title="Review quantum telemetry logs",
        due_at="2026-11-12 10:00",
        body="Inspect Starburst visualizer shaders.",
    )
    briefing_text = reminder_manager.generate_daily_briefing(owner_name="Rohan")
    assert "Rohan" in briefing_text
    assert "telemetry" in briefing_text.lower() or "quantum" in briefing_text.lower()


# ══════════════════════════════════════════════════════════════════════════════
# Scenario 2: Volume Control Workflow
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_scenario_volume_control_workflow(auth_client: httpx.AsyncClient):
    """
    Workflow 2: Volume Control.
    Executes a complete audio adjustment sequence: volume up, volume down,
    mute toggle, unmute, and checks audio status.
    """
    # Step 1: Initial voice status
    status_1 = await auth_client.get("/api/v1/voice/status")
    assert status_1.status_code == 200

    # Step 2: Increase Volume
    vol_up = laptop_controller.adjust_volume("up")
    assert vol_up["success"] is True
    assert "increased" in vol_up["message"].lower()

    # Step 3: Decrease Volume
    vol_down = laptop_controller.adjust_volume("down")
    assert vol_down["success"] is True
    assert "lowered" in vol_down["message"].lower()

    # Step 4: Toggle Mute
    vol_mute = laptop_controller.adjust_volume("mute")
    assert vol_mute["success"] is True
    assert "mute" in vol_mute["message"].lower()

    # Step 5: Unmute
    vol_unmute = laptop_controller.adjust_volume("unmute")
    assert vol_unmute["success"] is True

    # Step 6: Verify Voice Status remains online
    status_final = await auth_client.get("/api/v1/voice/status")
    assert status_final.status_code == 200
    assert status_final.json()["enabled"] is True


# ══════════════════════════════════════════════════════════════════════════════
# Scenario 3: Vocal Barge-In Workflow
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_scenario_vocal_barge_in_workflow(auth_client: httpx.AsyncClient):
    """
    Workflow 3: Vocal Barge-In.
    Simulates speech playback, immediate user interruption, and subsequent
    dialogue without deadlock or session freeze.
    """
    # Step 1: Start speech playback simulation
    voice_service.is_speaking = True
    assert voice_service.is_speaking is True

    # Step 2: Owner speaks mid-playback; frontend triggers interrupt
    interrupt_resp = await auth_client.post("/api/v1/voice/interrupt")
    assert interrupt_resp.status_code == 200
    assert interrupt_resp.json()["status"] == "interrupted"
    assert interrupt_resp.json()["is_speaking"] is False
    assert voice_service.is_speaking is False

    # Step 3: Owner issues a new command immediately after barge-in
    chat_resp = await auth_client.post(
        "/api/v1/conversations/chat",
        json={"message": "Jarvis, what is the time?"},
    )
    assert chat_resp.status_code == 200
    assert "time is" in chat_resp.json()["reply"].lower() or ":" in chat_resp.json()["reply"]

    # Step 4: Verify speech synthesis can be cleanly invoked again
    speak_resp = await auth_client.post(
        "/api/v1/voice/speak",
        json={"text": "Acknowledged, Sir."},
    )
    assert speak_resp.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
# Scenario 4: Autonomous Self-Healing Incident Recovery Workflow
# ══════════════════════════════════════════════════════════════════════════════

def test_scenario_self_healing_incident_recovery_workflow(tmp_path: Path):
    """
    Workflow 4: Autonomous Self-Healing Incident Recovery.
    Simulates a runtime syntax defect in a Python service module, intercepts
    the defect, applies an autonomous AST patch, verifies against tests, and
    executes the repaired module with zero downtime.
    """
    # Step 1: Deploy a faulty service module
    service_file = tmp_path / "telemetry_processor.py"
    service_file.write_text(
        "def process_telemetry(packet)\n"
        "    return {'processed': True, 'metric': packet * 2}\n",
        encoding="utf-8",
    )

    # Step 2: Execute code and catch defect
    try:
        compile(service_file.read_text(), str(service_file), "exec")
        pytest.fail("Expected SyntaxError was not raised")
    except SyntaxError as defect_exc:
        # Step 3: Dispatch to Self-Healing Engine
        repair_result = self_healing_engine.diagnose_and_repair(
            error_input=defect_exc,
            target_file=service_file,
        )

    # Step 4: Verify autonomous repair confirmation
    assert repair_result.success is True
    assert repair_result.verification_passed is True
    assert repair_result.file_healed is not None
    assert repair_result.duration_ms >= 0

    # Step 5: Verify repaired file content
    repaired_code = service_file.read_text(encoding="utf-8")
    assert "def process_telemetry(packet):" in repaired_code

    # Step 6: Verify zero-downtime execution of repaired code
    env = {}
    exec(repaired_code, env)
    result = env["process_telemetry"](21)
    assert result == {"processed": True, "metric": 42}


# ══════════════════════════════════════════════════════════════════════════════
# Scenario 5: Desktop App Serving & Health Verification Workflow
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_scenario_desktop_app_serving_and_health_workflow(auth_client: httpx.AsyncClient):
    """
    Workflow 5: Desktop App Serving & Health Verification.
    Simulates complete client startup: fetching desktop index bundle,
    resolving the application icon, and verifying all health matrices.
    """
    # Step 1: Fetch Desktop App Shell
    spa_resp = await auth_client.get("/")
    assert spa_resp.status_code == 200
    assert "<!doctype html>" in spa_resp.text.lower() or "<html" in spa_resp.text.lower()

    # Step 2: Fetch App Icon Asset
    icon_resp = await auth_client.get("/jarvis-icon.svg")
    assert icon_resp.status_code == 200

    # Step 3: Health Matrix Validation
    health_resp = await auth_client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["status"] == "online"
    assert health_data["components"]["database"] == "online"
    assert health_data["components"]["system_monitor"] == "online"

    # Step 4: Auth Readiness
    setup_resp = await auth_client.get("/api/v1/auth/setup-status")
    assert setup_resp.status_code == 200
    assert setup_resp.json()["owner_configured"] is True

    # Step 5: System Telemetry Streaming
    metrics_resp = await auth_client.get("/api/v1/system/metrics")
    assert metrics_resp.status_code == 200
    assert "status" in metrics_resp.json() or "cpu_percent" in metrics_resp.json()
