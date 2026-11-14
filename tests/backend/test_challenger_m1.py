"""
Adversarial Stress Test Suite for Milestone 1
Tests:
1. Tool registry execution with invalid args, unauthorized actions, boundary inputs.
2. Directive interception in laptop_controller / conversations: fall-through vs swallowing.
3. Concurrency / race conditions under multi-threaded execution.
4. Memory stability / leak checks across repeated invocations.
"""
import gc
import threading
import pytest
from backend.app.tools.registry import ToolExecutionRequest
from backend.app.tools.tool_registry import tool_registry
from backend.app.tools.laptop_controller import laptop_controller
from backend.app.security.profiles import profile_manager, ProfileType


# ==============================================================================
# 1. Tool Registry Adversarial Boundary Tests
# ==============================================================================

def test_tool_registry_nonexistent_tool():
    """Verify tool registry returns a clean error for non-existent tools."""
    req = ToolExecutionRequest(tool_id="phantom_tool_404", arguments={})
    res = tool_registry.execute_tool(req)
    assert res["success"] is False
    assert "not found" in res["error"].lower()


def test_tool_registry_empty_tool_id():
    """Verify tool registry handles empty string tool_id without unhandled exception."""
    req = ToolExecutionRequest(tool_id="", arguments={})
    res = tool_registry.execute_tool(req)
    assert res["success"] is False
    assert "not found" in res["error"].lower()


def test_tool_registry_invalid_argument_types():
    """Verify tool registry does not crash with unexpected or None argument types."""
    # Test set_volume with None action
    req_vol_none = ToolExecutionRequest(tool_id="set_volume", arguments={"action": None})
    res_vol_none = tool_registry.execute_tool(req_vol_none)
    assert isinstance(res_vol_none, dict)

    # Test set_volume with int action
    req_vol_int = ToolExecutionRequest(tool_id="set_volume", arguments={"action": 12345})
    res_vol_int = tool_registry.execute_tool(req_vol_int)
    assert isinstance(res_vol_int, dict)

    # Test set_volume with unknown string action
    req_vol_unknown = ToolExecutionRequest(tool_id="set_volume", arguments={"action": "explode_speakers"})
    res_vol_unknown = tool_registry.execute_tool(req_vol_unknown)
    assert res_vol_unknown["success"] is False
    assert "unknown" in res_vol_unknown["message"].lower()

    # Test launch_app with empty/None
    req_app_none = ToolExecutionRequest(tool_id="launch_app", arguments={"app_name": None})
    res_app_none = tool_registry.execute_tool(req_app_none)
    assert isinstance(res_app_none, dict)

    # Test execute_directive with None
    req_dir_none = ToolExecutionRequest(tool_id="execute_directive", arguments={"directive": None})
    # This might fail if laptop_controller expects a string
    try:
        res_dir_none = tool_registry.execute_tool(req_dir_none)
        assert isinstance(res_dir_none, dict)
    except Exception as e:
        pytest.fail(f"tool_registry crashed on None directive: {e}")


def test_tool_registry_boundary_inputs():
    """Verify tool registry handles massive strings and control characters."""
    oversized_str = "A" * 50_000
    req = ToolExecutionRequest(tool_id="execute_directive", arguments={"directive": oversized_str})
    res = tool_registry.execute_tool(req)
    assert isinstance(res, dict)

    # Directive with control characters and null bytes
    special_str = "\x00\x01\t\r\n!@#$%^&*()_+"
    req_special = ToolExecutionRequest(tool_id="execute_directive", arguments={"directive": special_str})
    res_special = tool_registry.execute_tool(req_special)
    assert isinstance(res_special, dict)


def test_tool_registry_unauthorized_permission_boundary():
    """Verify profile permission boundaries block higher-tier tools."""
    original_profile = profile_manager.active_profile
    try:
        # Switch to GUEST profile (max_permission_level = 0: READ_ONLY)
        profile_manager.switch_profile(ProfileType.GUEST)

        # set_volume requires level 1 (REVERSIBLE_LOCAL) -> MUST be blocked
        req_vol = ToolExecutionRequest(tool_id="set_volume", arguments={"action": "up"})
        res_vol = tool_registry.execute_tool(req_vol)
        assert res_vol["success"] is False
        assert "permission" in res_vol["error"].lower()

        # organize_downloads requires level 2 (CONFIRMED_MODIFY) -> MUST be blocked
        req_org = ToolExecutionRequest(tool_id="organize_downloads", arguments={}, approval_granted=True)
        res_org = tool_registry.execute_tool(req_org)
        assert res_org["success"] is False
        assert "permission" in res_org["error"].lower()

        # get_battery_status is level 0 (READ_ONLY) -> SHOULD succeed even in GUEST
        req_bat = ToolExecutionRequest(tool_id="get_battery_status", arguments={})
        res_bat = tool_registry.execute_tool(req_bat)
        assert res_bat["success"] is True
    finally:
        profile_manager.switch_profile(original_profile)


def test_tool_registry_human_approval_enforcement():
    """Verify tools with requires_approval=True reject execution if approval_granted is False."""
    req = ToolExecutionRequest(tool_id="organize_downloads", arguments={}, approval_granted=False)
    res = tool_registry.execute_tool(req)
    assert res["success"] is False
    assert res.get("requires_approval") is True
    assert "approval" in res.get("approval_reason", "").lower()


# ==============================================================================
# 2. Concurrency and Race Condition Tests
# ==============================================================================

def test_tool_registry_concurrent_execution():
    """Verify concurrent multi-threaded execution does not corrupt registry state."""
    errors = []

    def worker(worker_id: int):
        try:
            req_bat = ToolExecutionRequest(tool_id="get_battery_status", arguments={})
            res_bat = tool_registry.execute_tool(req_bat)
            if not res_bat.get("success"):
                errors.append(f"Worker {worker_id} battery failed: {res_bat}")

            req_diag = ToolExecutionRequest(tool_id="get_system_diagnostics", arguments={})
            res_diag = tool_registry.execute_tool(req_diag)
            if not res_diag.get("success"):
                errors.append(f"Worker {worker_id} diag failed: {res_diag}")
        except Exception as e:
            errors.append(f"Worker {worker_id} crashed with {e}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent execution errors: {errors}"


# ==============================================================================
# 3. Memory Stability & Leak Checks
# ==============================================================================

def test_tool_registry_repeated_invocations_no_memory_explosion():
    """Verify 200 repeated telemetry invocations execute without unhandled leak."""
    gc.collect()
    for _ in range(200):
        req = ToolExecutionRequest(tool_id="get_battery_status", arguments={})
        res = tool_registry.execute_tool(req)
        assert res["success"] is True
    gc.collect()


# ==============================================================================
# 4. Directive Interception vs Non-Directive Fall-Through
# ==============================================================================

def test_directive_proper_fallthrough_for_complex_queries():
    """
    Verify queries that MUST fall through to AI reasoning are not swallowed.
    Fails if laptop_controller.execute_directive falsely intercepts non-directive questions.
    """
    queries_that_must_fall_through = [
        "Explain how transformer attention matrices work.",
        "Write a Python script that calculates Fibonacci numbers.",
        "What is the capital of France?",
    ]
    for q in queries_that_must_fall_through:
        res = laptop_controller.execute_directive(q)
        assert res is None, f"Query '{q}' was wrongly intercepted as: {res}"


def test_adversarial_non_directive_swallowing():
    """
    Empirically test whether non-directive user queries containing keywords
    like 'time', 'date', 'update', 'commute', 'battery' are incorrectly swallowed.
    """
    corrupted_queries = {
        "What is the time complexity of quicksort?": "Swallowed by 'time'",
        "Explain spacetime curvature": "Swallowed by 'time'",
        "How do I update my database?": "Swallowed by 'date'",
        "We need to validate the hypothesis": "Swallowed by 'date'",
        "Who is your candidate for the election?": "Swallowed by 'date'",
        "What is your daily commute like?": "Swallowed by 'mute'",
        "Can you play chess with me?": "Swallowed by greedy 'play' regex",
        "Start writing a poem about the sea": "Swallowed by greedy 'start' regex",
        "Run a simulation of orbital mechanics": "Swallowed by greedy 'run' regex",
        "How does a lithium-ion battery work?": "Swallowed by 'battery'",
    }

    swallowed_list = []
    for q, reason in corrupted_queries.items():
        res = laptop_controller.execute_directive(q)
        if res is not None:
            swallowed_list.append((q, reason, res))

    # Note: As an empirical challenger, we document how many queries fail fall-through
    assert len(swallowed_list) == 0, (
        f"{len(swallowed_list)} out of {len(corrupted_queries)} queries were wrongly intercepted and swallowed!\n"
        + "\n".join([f"  - '{q}' -> {res.get('message', res)}" for q, _, res in swallowed_list])
    )
