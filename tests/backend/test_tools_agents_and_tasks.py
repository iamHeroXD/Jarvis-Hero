"""
Automated unit & integration tests for Computer Control Tools,
Specialist Agents, Task State Machine, Verification Engine, and Voice Service.
"""
from __future__ import annotations

import os
from pathlib import Path
import pytest
from backend.app.tools.app_launcher import app_launcher
from backend.app.tools.file_ops import file_ops
from backend.app.tools.command_runner import command_runner
from backend.app.tools.registry import tool_registry, ToolExecutionRequest
from backend.app.agents.orchestrator import jarvis_orchestrator
from backend.app.agents.atlas import atlas_agent
from backend.app.tasks.task_engine import task_engine, TaskState
from backend.app.tasks.verification import verification_engine
from backend.app.tasks.reminders import reminder_manager
from backend.app.voice.voice_service import voice_service


def test_approved_app_launcher():
    apps = app_launcher.list_approved_apps()
    assert len(apps) >= 4
    app_ids = [a["app_id"] for a in apps]
    assert "vscode" in app_ids
    assert "chrome" in app_ids
    assert "terminal" in app_ids

    # Unapproved app launch rejection
    unapproved = app_launcher.launch("malicious_trojan")
    assert unapproved["success"] is False
    assert "not in the approved" in unapproved["error"]


def test_file_operations_with_verification(tmp_path: Path):
    file_ops.add_approved_root(tmp_path)
    test_file = tmp_path / "jarvis_verified.txt"

    # Write file
    write_res = file_ops.create_or_update_file(test_file, "Hello from JARVIS")
    assert write_res["success"] is True
    assert write_res["verified"] is True

    # Verification Engine
    verify_res = verification_engine.verify_file_exists(test_file)
    assert verify_res.verified is True

    # Read file
    read_res = file_ops.read_file(test_file)
    assert read_res["success"] is True
    assert "Hello from JARVIS" in read_res["content"]

    # Outside approved path rejection
    unapproved = file_ops.read_file(r"C:\Windows\System32\drivers\etc\hosts")
    assert unapproved["success"] is False
    assert "Access denied" in unapproved["error"]


def test_allowlisted_command_runner():
    res = command_runner.run_command("git", ["--version"])
    assert res["success"] is True
    assert "git version" in res["stdout"]

    # Disallow chaining and unapproved binaries
    illegal = command_runner.run_command("git", ["status; rm -rf /"])
    assert illegal["success"] is False

    unapproved_bin = command_runner.run_command("curl", ["https://evil.com"])
    assert unapproved_bin["success"] is False


def test_tool_registry_and_permissions():
    tools = tool_registry.list_tools()
    assert len(tools) >= 5

    # Level 2 modification tool requires approval if not granted
    req_denied = ToolExecutionRequest(
        tool_id="create_file",
        arguments={"file_path": "test.txt", "content": "data"},
        approval_granted=False,
    )
    res_denied = tool_registry.execute_tool(req_denied)
    assert res_denied.get("requires_approval") is True


def test_agent_orchestrator_dispatch():
    # Dispatch code inspection to ATLAS
    atlas_res = jarvis_orchestrator.dispatch("Inspect the git repository status", {})
    assert atlas_res.agent == "ATLAS"
    assert atlas_res.status in ["completed", "completed_with_warnings"]

    # Dispatch research to ORACLE
    oracle_res = jarvis_orchestrator.dispatch("Research the latest documentation for WebSockets", {"topic": "WebSockets"})
    assert oracle_res.agent == "ORACLE"
    assert oracle_res.status == "completed"


def test_task_engine_state_machine():
    task = task_engine.create_task(
        title="Automated Test Workflow",
        description="Verify task state lifecycle.",
        assigned_agent="ATLAS",
    )
    assert task.status == TaskState.CREATED

    task_engine.transition(task.task_id, TaskState.PLANNING)
    assert task_engine.get_task(task.task_id).status == TaskState.PLANNING

    task_engine.transition(task.task_id, TaskState.RUNNING)
    assert task_engine.get_task(task.task_id).status == TaskState.RUNNING

    task_engine.record_evidence(task.task_id, "Test assertions passed.")
    task_engine.transition(task.task_id, TaskState.COMPLETED)
    completed = task_engine.get_task(task.task_id)
    assert completed.status == TaskState.COMPLETED
    assert completed.verified is True
    assert len(completed.evidence) > 0


def test_smart_reminders_and_briefing():
    rem = reminder_manager.add_reminder(
        title="Complete chemistry record",
        due_at="2026-11-10 20:00",
        body="Finish experiments 4 and 5.",
    )
    assert rem.id in [r["id"] for r in reminder_manager.list_reminders()]

    briefing = reminder_manager.generate_daily_briefing(owner_name="Rohan")
    assert "Rohan" in briefing
    assert "Complete chemistry record" in briefing

    reminder_manager.complete_reminder(rem.id)
    assert rem.id not in [r["id"] for r in reminder_manager.list_reminders()]


def test_voice_service_barge_in():
    status = voice_service.get_status()
    assert "wake_word" in status
    assert "voice_name" in status

    voice_service.is_speaking = True
    voice_service.interrupt_speech()
    assert voice_service.is_speaking is False
