"""
Automated unit & integration tests for JARVIS Evolution Pack,
Persona Engine, JIEE, Sentinel, and Governor.
"""
from __future__ import annotations

import pytest
from backend.app.personality.persona import persona_engine, ConversationMode
from backend.app.personality.humour import humour_engine
from backend.app.guidance.jiee import jiee
from backend.app.evolution.auditor import auditor
from backend.app.evolution.prompt_generator import prompt_generator
from backend.app.security.sentinel import sentinel_monitor
from backend.app.monitoring.governor import performance_governor, PowerProfile
from backend.app.security.profiles import profile_manager, ProfileType


def test_persona_engine_generation():
    prompt = persona_engine.build_system_instruction(
        owner_name="Rohan",
        mode=ConversationMode.BRITISH_ASSISTANT,
        profile_type="owner",
    )
    assert "J.A.R.V.I.S." in prompt
    assert "Rohan" in prompt
    assert "British" in prompt
    assert "ACTIVE MODE: BRITISH ASSISTANT" in prompt


def test_humour_engine():
    quip_startup = humour_engine.get_quip("startup")
    quip_code = humour_engine.get_quip("code_break")
    assert isinstance(quip_startup, str) and len(quip_startup) > 5
    assert isinstance(quip_code, str) and len(quip_code) > 5


def test_jiee_mismatch_detection():
    assert jiee.detect_correction_intent("No, that's not what I meant at all") is True
    assert jiee.detect_correction_intent("You missed the point, make it better") is True
    assert jiee.detect_correction_intent("Open Chrome for me") is False

    prompt = jiee.build_mismatch_prompt("Make website", "Bad SaaS", "Make it cleaner")
    assert "JIEE — INTROSPECTIVE CORRECTION REQUIRED" in prompt


def test_sentinel_url_safety():
    # Good URL
    good_res = sentinel_monitor.evaluate_url("https://github.com/my-org/project")
    assert good_res.risk_level == "low"

    # Spoofed typosquatting URL
    phish_res = sentinel_monitor.evaluate_url("https://github-account-verify.xyz/login")
    assert phish_res.risk_level in ["high", "critical"]
    assert len(phish_res.evidence) >= 1


def test_sentinel_communication_scan():
    scam_text = "Urgent action required! Please share your pin and verify your password immediately."
    threat = sentinel_monitor.analyze_communication(scam_text)
    assert threat.risk_level in ["high", "critical"]
    assert "social engineering" in threat.threat_type.lower()


def test_performance_governor():
    performance_governor.manual_profile = PowerProfile.ECO
    state = performance_governor.evaluate_hardware_state()
    assert state.profile == PowerProfile.ECO
    assert state.is_throttled is True
    assert state.target_particle_count <= 800

    performance_governor.manual_profile = None  # Reset


def test_codebase_auditor():
    findings = auditor.run_full_audit()
    assert isinstance(findings, list)
    assert len(findings) > 0


def test_prompt_generator():
    res = prompt_generator.generate_prompt(
        feature_name="Voice Latency Reduction",
        problem_statement="Reduce buffer latency on audio recording pipeline.",
        affected_modules=["backend/app/voice/audio.py"],
    )
    assert "# ANTIGRAVITY TASK SPECIFICATION: VOICE LATENCY REDUCTION" in res
    assert "backend/app/voice/audio.py" in res


def test_profile_permissions():
    perms_owner = profile_manager.switch_profile(ProfileType.OWNER)
    assert perms_owner.can_access_owner_memory is True

    perms_family = profile_manager.switch_profile(ProfileType.FAMILY)
    assert perms_family.can_access_owner_memory is False
    assert perms_family.can_view_development_evolution is False

    profile_manager.switch_profile(ProfileType.OWNER)  # Reset
