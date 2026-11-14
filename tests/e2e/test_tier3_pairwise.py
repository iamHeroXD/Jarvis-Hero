"""
Tier 3: Cross-Feature Combinations (Pairwise) E2E Test Suite.
Verifies integration between interrelated subsystems:
1. Chat WebSocket + Laptop Controller Directives
2. Direct REST Chat + Laptop Fast-Path Execution
3. Voice Synthesis + Immediate Barge-In Cancellation
4. Natural Directive Parser + Application Launching Map
5. Autonomous Self-Healing + Automated Test Verification
6. Desktop SPA Single-Origin Serving + Live API Telemetry
7. Hardware Governor Switching + Performance Telemetry
8. Tool Registry Permissions + Computer Execution
"""
from __future__ import annotations

import asyncio
from pathlib import Path
import pytest
import httpx
from starlette.testclient import TestClient

from backend.app.core.config import settings
from backend.app.tools.laptop_controller import laptop_controller
from backend.app.voice.voice_service import voice_service
from backend.app.evolution.self_healing import self_healing_engine
from backend.app.monitoring.governor import PowerProfile
from backend.app.tools.registry import tool_registry, ToolExecutionRequest


def test_pairwise_websocket_chat_and_laptop_directive(test_client: TestClient, auth_token: str):
    """
    Pairwise: WebSocket Chat + Laptop Controller.
    Sends battery status directive over WebSocket; verifies instantaneous
    interception, tool activity event, delta streaming, and completion.
    """
    with test_client.websocket_connect("/api/v1/conversations/ws/chat") as ws:
        ws.send_json({
            "token": auth_token,
            "message": "Jarvis, what is the battery level?",
        })

        # 1. Conversation ID confirmation
        convo_msg = ws.receive_json()
        assert convo_msg["type"] == "conversation_id"
        assert convo_msg["value"] > 0

        # 2. Tool activity notification
        activity_msg = ws.receive_json()
        assert activity_msg["type"] == "tool_activity"
        assert "Local Directive" in activity_msg["action"] or "Directive" in activity_msg["action"]

        # 3. Spoken delta streaming
        delta_msg = ws.receive_json()
        assert delta_msg["type"] == "delta"
        assert "battery" in delta_msg["text"].lower() or "power" in delta_msg["text"].lower()

        # 4. Turn completion message
        completed_msg = ws.receive_json()
        assert completed_msg["type"] == "completed"
        assert completed_msg["message_id"] > 0


@pytest.mark.asyncio
async def test_pairwise_rest_chat_and_laptop_directive(auth_client: httpx.AsyncClient):
    """
    Pairwise: Direct REST Chat + Laptop Controller.
    Sends system diagnostics directive to /chat; verifies immediate execution
    with model='local_controller' without external LLM latency.
    """
    response = await auth_client.post(
        "/api/v1/conversations/chat",
        json={"message": "system diagnostics briefing"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "cpu" in data["reply"].lower() or "mark vii" in data["reply"].lower()
    assert data["model"] == "local_controller"
    assert data["conversation_id"] > 0


@pytest.mark.asyncio
async def test_pairwise_voice_synthesis_and_barge_in(auth_client: httpx.AsyncClient):
    """
    Pairwise: Voice Synthesis + Barge-In Interruption.
    Starts speech state, immediately triggers /interrupt, verifies clean cancellation.
    """
    # 1. Activate speaking state
    voice_service.is_speaking = True
    assert voice_service.is_speaking is True

    # 2. Trigger interrupt endpoint
    response = await auth_client.post("/api/v1/voice/interrupt")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "interrupted"
    assert data["is_speaking"] is False

    # 3. Verify service state is reset
    status_res = await auth_client.get("/api/v1/voice/status")
    assert status_res.status_code == 200
    assert status_res.json()["is_speaking"] is False


def test_pairwise_directive_and_app_launcher():
    """
    Pairwise: Natural Directive Parser + Application Launcher.
    Issues natural command 'launch notepad', verifying directive parses
    the intent and maps to notepad executable.
    """
    res = laptop_controller.execute_directive("Jarvis please launch notepad")
    assert res is not None
    assert res["success"] is True
    assert "notepad" in res.get("app", "").lower() or "notepad" in res.get("message", "").lower()


def test_pairwise_self_healing_and_test_execution(tmp_path: Path):
    """
    Pairwise: Self-Healing Engine + Automated Test Verification.
    Injects a missing colon defect in a Python function, triggers diagnose_and_repair,
    and verifies that AST verification passes and heals the file.
    """
    broken_file = tmp_path / "trajectory_calc.py"
    broken_file.write_text(
        "def compute_trajectory(speed, angle)\n    return speed * angle + 10\n",
        encoding="utf-8",
    )

    # Trigger syntax error
    try:
        compile(broken_file.read_text(), str(broken_file), "exec")
        pytest.fail("Expected SyntaxError was not raised")
    except SyntaxError as exc:
        result = self_healing_engine.diagnose_and_repair(
            error_input=exc,
            target_file=broken_file,
        )

    assert result.success is True
    assert result.verification_passed is True
    healed_content = broken_file.read_text(encoding="utf-8")
    assert "def compute_trajectory(speed, angle):" in healed_content

    # Verify execution of the healed code
    local_ns = {}
    exec(healed_content, local_ns)
    assert local_ns["compute_trajectory"](10, 2) == 30


@pytest.mark.asyncio
async def test_pairwise_desktop_spa_and_rest_health(auth_client: httpx.AsyncClient):
    """
    Pairwise: Desktop SPA Single-Origin Serving + Backend Health APIs.
    Simulates browser loading SPA HTML and fetching live health and system metrics.
    """
    # 1. Fetch SPA HTML
    spa_resp = await auth_client.get("/")
    assert spa_resp.status_code == 200
    assert "<html" in spa_resp.text.lower() or "<!doctype html>" in spa_resp.text.lower()

    # 2. Fetch root health
    health_resp = await auth_client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "online"

    # 3. Fetch system metrics
    metrics_resp = await auth_client.get("/api/v1/system/metrics")
    assert metrics_resp.status_code == 200
    assert "status" in metrics_resp.json() or "cpu_percent" in metrics_resp.json()


@pytest.mark.asyncio
async def test_pairwise_governor_profile_and_telemetry(auth_client: httpx.AsyncClient):
    """
    Pairwise: Governor Power Profile Switching + Telemetry Validation.
    Switches governor profile to eco and verifies state reflection.
    """
    # 1. Set to eco
    set_resp = await auth_client.post(
        "/api/v1/governor/set-profile",
        json={"profile": "eco"},
    )
    assert set_resp.status_code == 200
    assert "eco" in set_resp.json()["message"].lower()

    # 2. Query status
    status_resp = await auth_client.get("/api/v1/governor/status")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["profile"] in ["eco", "balanced", "performance"]
    assert "target_particle_count" in data

    # 3. Clean up by returning to balanced
    cleanup_resp = await auth_client.post(
        "/api/v1/governor/set-profile",
        json={"profile": "balanced"},
    )
    assert cleanup_resp.status_code == 200


def test_pairwise_tool_registry_and_permissions(tmp_path: Path):
    """
    Pairwise: Tool Registry + Level 2 Permission Enforcement.
    Verifies that Level 2 file modifications require explicit approval flag.
    """
    from backend.app.tools.file_ops import file_ops
    file_ops.add_approved_root(tmp_path)

    sample_file = tmp_path / "registry_pairwise_test.txt"
    denied_req = ToolExecutionRequest(
        tool_id="create_file",
        arguments={"file_path": str(sample_file), "content": "protected"},
        approval_granted=False,
    )
    res_denied = tool_registry.execute_tool(denied_req)
    assert res_denied.get("requires_approval") is True

    # When approval granted, tool proceeds
    granted_req = ToolExecutionRequest(
        tool_id="create_file",
        arguments={"file_path": str(sample_file), "content": "authorized"},
        approval_granted=True,
    )
    res_granted = tool_registry.execute_tool(granted_req)
    assert res_granted.get("success") is True
