import pytest
from unittest.mock import patch, MagicMock
from backend.app.monitoring.sentinel_guardian import SentinelGuardian, sentinel_guardian
from backend.app.ai.offline_intelligence import OfflineIntelligenceCore, offline_core


def test_sentinel_storage_status():
    """Verify SentinelGuardian accurately measures and reports C: drive storage."""
    status = sentinel_guardian.get_storage_status()
    assert "total_gb" in status
    assert "free_gb" in status
    assert "used_gb" in status
    assert "percent_used" in status
    assert "is_critical" in status
    assert "severity" in status
    assert status["total_gb"] > 0
    assert status["percent_used"] >= 0


def test_sentinel_proactive_alert_message():
    """Verify SentinelGuardian generates an alert when storage is constrained."""
    # Test critical alert formulation
    alert_critical = sentinel_guardian.get_proactive_alert_message(free_threshold_gb=1000.0)
    assert alert_critical is not None
    assert "Warning, Sir" in alert_critical or "storage" in alert_critical.lower()

    # Test when threshold is 0.0 (no alert)
    alert_none = sentinel_guardian.get_proactive_alert_message(free_threshold_gb=0.0)
    assert alert_none is None


def test_sentinel_summary():
    """Verify get_sentinel_summary aggregates hardware, battery, and network telemetry."""
    summary = sentinel_guardian.get_sentinel_summary()
    assert "storage" in summary
    assert "ram" in summary
    assert "cpu" in summary
    assert "network" in summary
    assert "timestamp" in summary
    assert "online" in summary["network"]


def test_sentinel_purge_temp_storage():
    """Verify purge_temp_storage executes safely and returns metrics."""
    result = sentinel_guardian.purge_temp_storage()
    assert "freed_mb" in result
    assert "files_removed" in result
    assert "current_free_gb" in result
    assert "message" in result
    assert result["freed_mb"] >= 0


def test_offline_core_math_evaluation():
    """Verify offline core computes local math problems instantly."""
    res = offline_core.evaluate_offline_query("calculate 125 * 8")
    assert "1000" in res["text"]
    assert res["source"] == "offline_neural_core"


def test_offline_core_battery_telemetry():
    """Verify offline core reports battery status without internet."""
    res = offline_core.evaluate_offline_query("what is my battery level?")
    assert "battery" in res["text"].lower() or "percent" in res["text"].lower()
    assert res["source"] == "offline_neural_core"


def test_offline_core_storage_check():
    """Verify offline core reports disk storage."""
    res = offline_core.evaluate_offline_query("check my storage and c drive")
    assert "gigabytes" in res["text"].lower() or "c: drive" in res["text"].lower()
    assert res["source"] == "offline_neural_core"


def test_offline_core_computer_directive():
    """Verify offline core routes computer automation commands."""
    res = offline_core.evaluate_offline_query("launch notepad")
    assert "notepad" in res["text"].lower() or "executing" in res["text"].lower()


def test_offline_core_personality_fallback():
    """Verify offline core maintains British in-character demeanor."""
    res = offline_core.evaluate_offline_query("who created you?")
    assert "rohan" in res["text"].lower()
    assert res["source"] == "offline_neural_core"
