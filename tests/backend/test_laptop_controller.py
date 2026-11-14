"""
Comprehensive Unit Tests for JARVIS Laptop Controller & Tool Registry Integration
Covers:
- Battery status telemetry (live and mocked)
- System diagnostics metrics (CPU, RAM, disk, battery)
- Volume adjustments (up, down, mute, unmute, invalid)
- Start menu and desktop shortcut cache lookup
- Downloads folder categorization and safe organization logic
- Natural directive parsing (battery, time, date, diagnostics, volume, conversational, AI fallback)
- Tool registry queries and tool executions for laptop controller functions
"""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from backend.app.tools.laptop_controller import LaptopController, laptop_controller
from backend.app.tools.tool_registry import tool_registry, ToolExecutionRequest


# ── 1. Battery Status Tests ──────────────────────────────────────────────────

def test_battery_status_live_or_fallback():
    """Verify live battery status returns expected schema and non-empty message."""
    res = laptop_controller.get_battery_status()
    assert res["success"] is True
    assert "percent" in res
    assert isinstance(res["percent"], int)
    assert 0 <= res["percent"] <= 100
    assert "charging" in res
    assert isinstance(res["charging"], bool)
    assert "message" in res
    assert len(res["message"]) > 0


def test_battery_status_mocked():
    """Verify battery status parsing when psutil returns specific battery telemetry."""
    mock_battery = MagicMock()
    mock_battery.percent = 84.5
    mock_battery.power_plugged = True

    with patch("psutil.sensors_battery", return_value=mock_battery):
        res = laptop_controller.get_battery_status()
        assert res["success"] is True
        assert res["percent"] == 84
        assert res["charging"] is True
        assert "84%" in res["message"]
        assert "charging on AC power" in res["message"]


def test_battery_status_psutil_none_fallback():
    """Verify graceful fallback when psutil cannot detect power cells (e.g. desktop)."""
    with patch("psutil.sensors_battery", return_value=None):
        res = laptop_controller.get_battery_status()
        assert res["success"] is True
        assert res["percent"] == 90
        assert res["charging"] is True
        assert "Power cells are nominal" in res["message"]


# ── 2. System Diagnostics Tests ──────────────────────────────────────────────

def test_system_diagnostics_live():
    """Verify instantaneous system diagnostics query returns valid telemetry metrics."""
    res = laptop_controller.get_system_diagnostics()
    assert res["success"] is True
    assert "cpu" in res
    assert isinstance(res["cpu"], (int, float))
    assert res["cpu"] >= 0.0
    assert "ram" in res
    assert isinstance(res["ram"], (int, float))
    assert 0.0 <= res["ram"] <= 100.0
    assert "disk_free_gb" in res
    assert res["disk_free_gb"] > 0
    assert "message" in res
    assert "Mark VII systems" in res["message"]


def test_system_diagnostics_mocked():
    """Verify system diagnostics string formatting against deterministic mocked metrics."""
    mock_mem = MagicMock()
    mock_mem.percent = 42.0
    mock_mem.available = 16 * (1024 ** 3)  # 16 GB

    mock_disk = MagicMock()
    mock_disk.free = 250 * (1024 ** 3)  # 250 GB

    mock_battery = MagicMock()
    mock_battery.percent = 92.0

    with patch("psutil.cpu_percent", return_value=12.5), \
         patch("psutil.virtual_memory", return_value=mock_mem), \
         patch("psutil.disk_usage", return_value=mock_disk), \
         patch("psutil.sensors_battery", return_value=mock_battery):
        res = laptop_controller.get_system_diagnostics()
        assert res["success"] is True
        assert res["cpu"] == 12.5
        assert res["ram"] == 42.0
        assert res["disk_free_gb"] == 250.0
        assert "CPU load is at 12%" in res["message"]
        assert "RAM utilization is at 42%" in res["message"]
        assert "250 GB remaining" in res["message"]
        assert "battery at 92%" in res["message"]


# ── 3. Volume Adjustment Tests ───────────────────────────────────────────────

@pytest.mark.parametrize("action,expected_msg", [
    ("up", "Master volume increased, Sir."),
    ("down", "Master volume lowered, Sir."),
    ("mute", "Audio mute toggled, Sir."),
    ("unmute", "Audio mute toggled, Sir."),
])
def test_adjust_volume_actions(action: str, expected_msg: str):
    """Verify volume actions trigger Windows keybd events and report success."""
    with patch("ctypes.windll.user32.keybd_event") as mock_keybd:
        res = laptop_controller.adjust_volume(action)
        assert res["success"] is True
        assert res["message"] == expected_msg
        assert mock_keybd.called


def test_adjust_volume_invalid_action():
    """Verify invalid volume action gracefully returns error."""
    res = laptop_controller.adjust_volume("warp_speed")
    assert res["success"] is False
    assert "Unknown volume action" in res["message"]


# ── 4. Shortcut Cache Lookup Tests ───────────────────────────────────────────

def test_shortcut_cache_indexed():
    """Verify shortcut cache is a populated dictionary of Windows shortcuts."""
    assert isinstance(laptop_controller._shortcut_cache, dict)
    # The cache indexes real Start Menu items if available on Windows
    assert len(laptop_controller.app_map) >= 10


def test_shortcut_cache_lookup_and_match():
    """Verify custom shortcut resolution matches registered or mocked shortcuts."""
    test_ctrl = LaptopController()
    test_ctrl._shortcut_cache["custom tool test"] = r"C:\Dummy\custom_tool.lnk"

    # Find registered app in app_map
    assert "chrome" in test_ctrl.app_map
    assert "vscode" in test_ctrl.app_map

    # Test resolution with mock startfile
    with patch("os.startfile") as mock_startfile:
        res = test_ctrl.launch_app("custom tool test")
        assert res["success"] is True
        assert res["app"] == "custom_tool"
        assert mock_startfile.called


# ── 5. Downloads Folder Organization Tests ───────────────────────────────────

def test_organize_downloads_in_temp_dir(tmp_path: Path):
    """Verify organize_downloads accurately categorizes files into target directories."""
    downloads_mock = tmp_path / "Downloads"
    downloads_mock.mkdir()

    # Create test dummy files
    files_to_create = {
        "sample.pdf": "Documents",
        "doc.docx": "Documents",
        "sheet.xlsx": "Documents",
        "graphic.png": "Images",
        "wallpaper.jpg": "Images",
        "vector.svg": "Images",
        "soundtrack.mp3": "Audio",
        "voice.wav": "Audio",
        "trailer.mp4": "Video",
        "clip.mkv": "Video",
        "bundle.zip": "Archives",
        "tarball.tar": "Archives",
        "installer.exe": "Executables",
        "batch.bat": "Executables",
        "script.py": "Code",
        "webpage.html": "Code",
        "random.unknownext": "Other",
    }

    for filename in files_to_create:
        (downloads_mock / filename).write_text("JARVIS test content")

    # Point controller to mock downloads folder
    orig_dir = laptop_controller.downloads_dir
    try:
        laptop_controller.downloads_dir = downloads_mock
        res = laptop_controller.organize_downloads()

        assert res["success"] is True
        assert res["moved_count"] == len(files_to_create)
        assert "reorganized successfully" in res["message"]

        # Verify files were moved into proper folders
        for filename, category in files_to_create.items():
            expected_path = downloads_mock / category / filename
            assert expected_path.exists(), f"File {filename} was not found in {category}"

    finally:
        laptop_controller.downloads_dir = orig_dir


def test_organize_downloads_missing_directory():
    """Verify graceful handling when downloads directory does not exist."""
    orig_dir = laptop_controller.downloads_dir
    try:
        laptop_controller.downloads_dir = Path("Z:\\NonExistentJarvisFolder12345")
        res = laptop_controller.organize_downloads()
        assert res["success"] is False
        assert "not found" in res["message"]
    finally:
        laptop_controller.downloads_dir = orig_dir


# ── 6. Directive Parser Tests ────────────────────────────────────────────────

@pytest.mark.parametrize("prompt", [
    "battery",
    "battery status",
    "check battery level",
    "Jarvis, what is the battery level?",
    "can you tell me the power status?",
])
def test_directive_battery(prompt: str):
    """Verify battery directives are recognized and routed to get_battery_status."""
    res = laptop_controller.execute_directive(prompt)
    assert res is not None
    assert res["success"] is True
    assert "battery" in res["message"].lower() or "power" in res["message"].lower()


@pytest.mark.parametrize("prompt", [
    "what time is it",
    "Jarvis what's the time?",
    "current time",
    "tell me the time please",
])
def test_directive_time(prompt: str):
    """Verify time directives are recognized and return current time."""
    res = laptop_controller.execute_directive(prompt)
    assert res is not None
    assert res["success"] is True
    assert "current time is" in res["message"]


@pytest.mark.parametrize("prompt", [
    "today's date",
    "what is the date",
    "what day is it",
])
def test_directive_date(prompt: str):
    """Verify date directives return today's formatted date."""
    res = laptop_controller.execute_directive(prompt)
    assert res is not None
    assert res["success"] is True
    assert "Today is" in res["message"]


@pytest.mark.parametrize("prompt", [
    "system diagnostics",
    "diagnostics",
    "system status",
    "health check",
    "status briefing",
])
def test_directive_diagnostics(prompt: str):
    """Verify diagnostics directives trigger get_system_diagnostics."""
    res = laptop_controller.execute_directive(prompt)
    assert res is not None
    assert res["success"] is True
    assert "cpu" in res
    assert "ram" in res


@pytest.mark.parametrize("prompt,action_word", [
    ("volume up", "increased"),
    ("turn it up", "increased"),
    ("louder please", "increased"),
    ("volume down", "lowered"),
    ("turn it down", "lowered"),
    ("quieter", "lowered"),
    ("mute", "toggled"),
    ("unmute", "toggled"),
    ("toggle mute", "toggled"),
])
def test_directive_volume(prompt: str, action_word: str):
    """Verify volume directives invoke adjust_volume."""
    with patch("ctypes.windll.user32.keybd_event"):
        res = laptop_controller.execute_directive(prompt)
        assert res is not None
        assert res["success"] is True
        assert action_word in res["message"].lower()


@pytest.mark.parametrize("prompt", [
    "hello",
    "hi",
    "greetings",
    "who are you",
    "what can you do",
    "thank you",
])
def test_directive_conversational_fast_path(prompt: str):
    """Verify standard conversational fast paths execute without deep AI fallback."""
    res = laptop_controller.execute_directive(prompt)
    assert res is not None
    assert res["success"] is True
    assert len(res["message"]) > 0


def test_directive_ai_reasoning_fallback():
    """Verify non-directive queries return None to allow full Gemini reasoning."""
    assert laptop_controller.execute_directive("Explain how transformer attention matrices work.") is None
    assert laptop_controller.execute_directive("Write a Python script that calculates Fibonacci numbers.") is None
    assert laptop_controller.execute_directive("What is the capital of France?") is None


# ── 7. Tool Registry Integration Tests ───────────────────────────────────────

def test_tool_registry_has_laptop_tools():
    """Verify laptop controller tools are registered and queryable in tool registry."""
    tools = tool_registry.list_tools()
    tool_ids = {t["tool_id"] for t in tools}

    expected_tools = {
        "get_battery_status",
        "get_system_diagnostics",
        "set_volume",
        "launch_app",
        "organize_downloads",
        "execute_directive",
    }
    assert expected_tools.issubset(tool_ids), f"Missing laptop tools: {expected_tools - tool_ids}"


def test_tool_registry_execute_battery():
    """Verify invoking get_battery_status via tool registry."""
    req = ToolExecutionRequest(tool_id="get_battery_status", arguments={})
    res = tool_registry.execute_tool(req)
    assert res["success"] is True
    assert "percent" in res


def test_tool_registry_execute_diagnostics():
    """Verify invoking get_system_diagnostics via tool registry."""
    req = ToolExecutionRequest(tool_id="get_system_diagnostics", arguments={})
    res = tool_registry.execute_tool(req)
    assert res["success"] is True
    assert "cpu" in res
    assert "ram" in res


def test_tool_registry_execute_volume():
    """Verify invoking set_volume via tool registry."""
    with patch("ctypes.windll.user32.keybd_event"):
        req = ToolExecutionRequest(
            tool_id="set_volume",
            arguments={"action": "up"},
        )
        res = tool_registry.execute_tool(req)
        assert res["success"] is True
        assert "increased" in res["message"]


def test_tool_registry_organize_downloads_requires_approval():
    """Verify organize_downloads requires approval (Level 2 modify)."""
    req_unapproved = ToolExecutionRequest(
        tool_id="organize_downloads",
        arguments={},
        approval_granted=False,
    )
    res = tool_registry.execute_tool(req_unapproved)
    assert res["requires_approval"] is True
    assert res["success"] is False


def test_tool_registry_execute_directive():
    """Verify executing a directive via tool registry."""
    req = ToolExecutionRequest(
        tool_id="execute_directive",
        arguments={"directive": "battery"},
    )
    res = tool_registry.execute_tool(req)
    assert res["success"] is True
    assert "battery" in res["message"].lower() or "power" in res["message"].lower()
