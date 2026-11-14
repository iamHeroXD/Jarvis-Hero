"""
Automated verification tests for JARVIS Autonomous Self-Code Healing Engine.
Verifies:
1. Diagnosis of syntax errors, NameErrors, and ZeroDivisionErrors.
2. Formulation of targeted code patches.
3. Safe application with backup and AST validation.
4. Autonomous verification and test-driven confirmation.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
import pytest
from backend.app.evolution.self_healing import self_healing_engine, DiagnosticReport, CodePatch


def test_self_healing_missing_colon_syntax_error():
    """Test autonomous repair of missing colon in a python function declaration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        broken_file = tmp_path / "broken_service.py"
        broken_file.write_text(
            "def calculate_trajectory(x, y)\n    return x * y + 42\n",
            encoding="utf-8",
        )

        # Trigger SyntaxError
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
        assert "def calculate_trajectory(x, y):" in broken_file.read_text(encoding="utf-8")


def test_self_healing_zero_division_guard():
    """Test autonomous injection of zero division protection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        calc_file = tmp_path / "math_ops.py"
        calc_file.write_text(
            "def safe_divide(a, b):\n    return a / b\n",
            encoding="utf-8",
        )

        try:
            # Simulate zero division
            10 / 0
        except ZeroDivisionError as exc:
            import traceback
            tb_str = traceback.format_exc()
            # Replace traceback file path with our test file
            tb_custom = f'File "{calc_file}", line 2, in safe_divide\n    return a / b\nZeroDivisionError: division by zero'
            result = self_healing_engine.diagnose_and_repair(
                error_input=tb_custom,
                target_file=calc_file,
            )

        assert result.success is True
        assert result.verification_passed is True
        healed_code = calc_file.read_text(encoding="utf-8")
        assert "if b != 0 else" in healed_code or "1e-9" in healed_code


def test_self_healing_undefined_name_error():
    """Test autonomous declaration of missing variable."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        name_file = tmp_path / "telemetry_reporter.py"
        name_file.write_text(
            "def get_metrics():\n    return telemetry_data\n",
            encoding="utf-8",
        )

        tb_custom = f'File "{name_file}", line 2, in get_metrics\n    return telemetry_data\nNameError: name \'telemetry_data\' is not defined'
        result = self_healing_engine.diagnose_and_repair(
            error_input=tb_custom,
            target_file=name_file,
        )

        assert result.success is True
        healed_code = name_file.read_text(encoding="utf-8")
        assert "telemetry_data = None" in healed_code
