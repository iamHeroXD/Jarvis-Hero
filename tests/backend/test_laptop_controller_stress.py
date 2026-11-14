"""
Adversarial Stress Test Suite for JARVIS Laptop Controller
Empirical stress-testing of backend/app/tools/laptop_controller.py:
1. Malformed, empty, unicode, ultra-long, and injection directive strings.
2. Rapid consecutive volume calls (up, down, mute, unmute, invalid, concurrent).
3. Battery status and system diagnostics with missing hardware, corrupted telemetry, or psutil exceptions.
4. Non-existent application names, empty queries, path traversal, and command injection in launch_app / shortcut cache.
5. Downloads directory organization with read-only, locked, nested, collision, and permission-challenged files.
"""
from __future__ import annotations

import os
import stat
import time
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from backend.app.tools.laptop_controller import LaptopController, laptop_controller


# ==============================================================================
# 1. DIRECTIVE PARSER ADVERSARIAL STRESS TESTS
# ==============================================================================

class TestDirectiveParserAdversarial:
    """Stress-test execute_directive against malformed, boundary, and injection strings."""

    def test_directive_empty_and_whitespace(self):
        """Verify empty and whitespace-only strings do not crash and return None."""
        assert laptop_controller.execute_directive("") is None
        assert laptop_controller.execute_directive("   ") is None
        assert laptop_controller.execute_directive("\t\n\r  ") is None

    @pytest.mark.parametrize("unicode_prompt", [
        "открой калькулятор",
        "打开浏览器",
        "افتح المتصفح",
        "🔊 🔋 💻 🚀 💥 💣 🔥",
        "jarvis\u200b\u200c\u200dwhat time is it",
        "こんにちは",
        "مرحبا بك",
        "⚡️✨🌟💫",
    ])
    def test_directive_unicode_and_emojis(self, unicode_prompt: str):
        """Verify non-ASCII, RTL, zero-width, and emoji inputs execute without crash."""
        res = laptop_controller.execute_directive(unicode_prompt)
        assert res is None or isinstance(res, dict)

    def test_directive_ultra_long_string(self):
        """Verify ultra-long strings (100,000 chars) do not trigger ReDoS or OOM."""
        long_string = "jarvis " + "please " * 5000 + "what time is it"
        t0 = time.perf_counter()
        res = laptop_controller.execute_directive(long_string)
        duration = time.perf_counter() - t0
        assert duration < 1.0, f"Directive parser took {duration:.2f}s (possible catastrophic backtracking)"
        assert res is not None
        assert "current time is" in res["message"]

    def test_directive_deep_punctuation_and_symbols(self):
        """Verify deeply repetitive punctuation does not break regex parsing."""
        prompt = "???????!!!!!!......,,,,,;;;;;;;;;;;;;;;;;;;"
        res = laptop_controller.execute_directive(prompt)
        assert res is None

    @pytest.mark.parametrize("injection_prompt", [
        "open calculator & calc.exe & dir",
        "launch notepad | whoami",
        "open \"; rm -rf /; #",
        "open %USERPROFILE%\\test",
        "open ' OR '1'='1",
        "open <script>alert(1)</script>",
    ])
    def test_directive_injection_attempts(self, injection_prompt: str):
        """Verify injection strings in directives are parsed safely without command execution."""
        with patch("os.startfile") as mock_startfile, \
             patch("subprocess.Popen") as mock_popen:
            res = laptop_controller.execute_directive(injection_prompt)
            assert res is None or isinstance(res, dict)

    @pytest.mark.xfail(reason="Defect: execute_directive lacks typecheck and crashes with AttributeError on NoneType or non-str", strict=False)
    def test_directive_non_string_types(self):
        """Verify non-string inputs (None, int, dict) do not crash the controller."""
        for invalid_input in [None, 12345, 3.14, [], {}, True]:
            res = laptop_controller.execute_directive(invalid_input)  # type: ignore
            assert res is None or isinstance(res, dict)


# ==============================================================================
# 2. MASTER VOLUME ADVERSARIAL STRESS TESTS
# ==============================================================================

class TestVolumeAdjustmentStress:
    """Stress-test volume controls with rapid bursts, invalid values, and concurrent calls."""

    def test_rapid_consecutive_volume_calls(self):
        """Verify 100 rapid consecutive volume calls execute cleanly without ctypes error."""
        actions = ["up", "down", "mute", "unmute"] * 25
        with patch("ctypes.windll.user32.keybd_event") as mock_keybd:
            t0 = time.perf_counter()
            for action in actions:
                res = laptop_controller.adjust_volume(action)
                assert res["success"] is True
            elapsed = time.perf_counter() - t0
            assert elapsed < 0.5, f"100 volume adjustments took {elapsed:.2f}s (exceeds budget)"
            assert mock_keybd.call_count == (25 * 5 * 2) + (25 * 5 * 2) + (25 * 2) + (25 * 2)

    @pytest.mark.parametrize("invalid_action", [
        "",
        "   ",
        "warp_speed",
        "100",
        "-5",
        "louder",
        "max",
        "UP",  # Case sensitivity check
        "Down",
        "MUTE",
    ])
    def test_volume_invalid_and_mixed_case(self, invalid_action: str):
        """Verify invalid actions return success=False and uppercase are normalized."""
        with patch("ctypes.windll.user32.keybd_event"):
            res = laptop_controller.adjust_volume(invalid_action)
            assert isinstance(res, dict)
            if invalid_action.lower().strip() in ("up", "down", "mute", "unmute"):
                assert res["success"] is True
            else:
                assert res["success"] is False
                assert "Unknown volume action" in res["message"]

    @pytest.mark.xfail(reason="Defect: adjust_volume calls action.lower() before try-block, raising uncaught AttributeError on None", strict=False)
    def test_volume_non_string_types(self):
        """Verify passing non-string types to adjust_volume returns failure rather than crashing."""
        for invalid_type in [None, 42, 99.9, [], {}]:
            res = laptop_controller.adjust_volume(invalid_type)  # type: ignore
            assert isinstance(res, dict)
            assert res["success"] is False


# ==============================================================================
# 3. BATTERY & SYSTEM DIAGNOSTICS ADVERSARIAL TESTS
# ==============================================================================

class TestBatteryAndDiagnosticsAdversarial:
    """Stress-test telemetry retrieval against hardware faults and corrupted return data."""

    def test_battery_psutil_exception_handling(self):
        """Verify battery query gracefully falls back when psutil raises unexpected exceptions."""
        for exc in [
            PermissionError("Access denied to hardware telemetry"),
            RuntimeError("Hardware driver unresponsive"),
            OSError("Device I/O error"),
            AttributeError("'NoneType' object has no attribute 'percent'"),
        ]:
            with patch("psutil.sensors_battery", side_effect=exc):
                res = laptop_controller.get_battery_status()
                assert res["success"] is True
                assert res["percent"] == 90
                assert res["charging"] is True
                assert "nominal" in res["message"].lower()

    @pytest.mark.parametrize("corrupted_percent,corrupted_plugged", [
        (-5, True),
        (150, False),
        (0, False),
        (100, True),
        (None, True),
        ("85", True),
    ])
    def test_battery_corrupted_hardware_telemetry(self, corrupted_percent, corrupted_plugged):
        """Verify resilience against abnormal psutil battery values."""
        mock_battery = MagicMock()
        mock_battery.percent = corrupted_percent
        mock_battery.power_plugged = corrupted_plugged

        with patch("psutil.sensors_battery", return_value=mock_battery):
            res = laptop_controller.get_battery_status()
            assert res["success"] is True
            assert "percent" in res

    def test_diagnostics_when_battery_none(self):
        """Verify system diagnostics runs cleanly when battery hardware is completely absent (desktop)."""
        with patch("psutil.sensors_battery", return_value=None):
            res = laptop_controller.get_system_diagnostics()
            assert res["success"] is True
            assert "battery" not in res["message"]
            assert "Mark VII systems" in res["message"]

    @pytest.mark.xfail(reason="Defect: get_system_diagnostics lacks try-except for disk_usage or battery.percent=None", strict=False)
    def test_diagnostics_resilience_to_psutil_exceptions(self):
        """Empirically check whether get_system_diagnostics handles psutil exceptions."""
        with patch("psutil.disk_usage", side_effect=OSError("Drive C: unavailable")):
            res = laptop_controller.get_system_diagnostics()
            assert isinstance(res, dict)
            assert res["success"] is False

    @pytest.mark.xfail(reason="Defect: get_system_diagnostics raises TypeError when battery.percent is None", strict=False)
    def test_diagnostics_resilience_to_battery_percent_none(self):
        """Empirically verify get_system_diagnostics when battery is present but percent is None."""
        mock_b = MagicMock()
        mock_b.percent = None
        with patch("psutil.sensors_battery", return_value=mock_b):
            res = laptop_controller.get_system_diagnostics()
            assert isinstance(res, dict)


# ==============================================================================
# 4. APPLICATION LAUNCHING & SHORTCUT RESOLUTION STRESS
# ==============================================================================

class TestAppLaunchingStress:
    """Stress-test application resolution against non-existent apps, path traversal, and empty strings."""

    @pytest.mark.xfail(reason="Defect: launch_app('') matches first shortcut because '' in name is True", strict=False)
    def test_launch_app_empty_string_vulnerability(self):
        """Empirically test whether launch_app('') triggers unintended shortcut match."""
        test_ctrl = LaptopController()
        test_ctrl._shortcut_cache = {"some_app": r"C:\Dummy\some_app.lnk"}

        with patch("os.startfile") as mock_startfile, \
             patch("subprocess.Popen") as mock_popen:
            res = test_ctrl.launch_app("")
            # If "" in name is True, it will attempt to launch 'some_app'
            if mock_startfile.called:
                called_target = mock_startfile.call_args[0][0]
                pytest.fail(f"VULNERABILITY DETECTED: launch_app('') triggered launch of '{called_target}'")
            assert isinstance(res, dict)
            assert res["success"] is False

    def test_launch_app_non_existent(self):
        """Verify launching a completely non-existent application handles failure."""
        with patch("os.startfile") as mock_startfile, \
             patch("subprocess.Popen") as mock_popen:
            res = laptop_controller.launch_app("completely_fake_nonexistent_program_xyz_9999")
            assert isinstance(res, dict)
            assert "app" in res

    @pytest.mark.parametrize("dangerous_app_name", [
        "notepad & calc.exe",
        "../../../../windows/system32/cmd.exe",
        "calc.exe; notepad.exe",
        "test`whoami`",
        "| dir",
    ])
    def test_launch_app_command_injection_safety(self, dangerous_app_name: str):
        """Verify command injection attempts in app name are handled safely."""
        with patch("os.startfile") as mock_startfile, \
             patch("subprocess.Popen") as mock_popen:
            res = laptop_controller.launch_app(dangerous_app_name)
            assert isinstance(res, dict)
            if mock_popen.called:
                args = mock_popen.call_args[0][0]
                assert isinstance(args, (list, str))

    def test_close_app_non_existent_and_empty(self):
        """Verify close_app handles non-existent processes and empty strings cleanly."""
        res_empty = laptop_controller.close_app("")
        assert res_empty["success"] is False

        res_fake = laptop_controller.close_app("non_existent_process_12345")
        assert res_fake["success"] is False
        assert "No active process found" in res_fake["message"] or "Failed to terminate" in res_fake["message"]


# ==============================================================================
# 5. DOWNLOADS ORGANIZATION ADVERSARIAL STRESS TESTS
# ==============================================================================

class TestDownloadsOrganizerStress:
    """Stress-test organize_downloads against read-only, locked, nested, and conflicting files."""

    def test_organize_downloads_with_readonly_file(self, tmp_path: Path):
        """Verify organize_downloads handles read-only files without crashing."""
        downloads_dir = tmp_path / "Downloads"
        downloads_dir.mkdir()

        # Create a read-only document
        ro_file = downloads_dir / "protected_contract.pdf"
        ro_file.write_text("Confidential NDA")
        os.chmod(str(ro_file), stat.S_IREAD)

        orig_dir = laptop_controller.downloads_dir
        try:
            laptop_controller.downloads_dir = downloads_dir
            res = laptop_controller.organize_downloads()
            assert res["success"] is True
            target_path = downloads_dir / "Documents" / "protected_contract.pdf"
            assert target_path.exists()
        finally:
            try:
                os.chmod(str(downloads_dir / "Documents" / "protected_contract.pdf"), stat.S_IWRITE)
            except Exception:
                pass
            laptop_controller.downloads_dir = orig_dir

    def test_organize_downloads_with_locked_file(self, tmp_path: Path):
        """Verify behavior when a file is held exclusively open (locked) by another process."""
        downloads_dir = tmp_path / "Downloads"
        downloads_dir.mkdir()

        file1 = downloads_dir / "regular_photo.jpg"
        file1.write_text("photo data")

        locked_file = downloads_dir / "in_use_archive.zip"
        locked_file.write_text("archive data")

        file2 = downloads_dir / "script.py"
        file2.write_text("print('hello')")

        orig_dir = laptop_controller.downloads_dir
        try:
            laptop_controller.downloads_dir = downloads_dir
            # Open file exclusively on Windows
            with open(locked_file, "a") as lock_handle:
                res = laptop_controller.organize_downloads()
                assert isinstance(res, dict)
                # Catch PermissionError gracefully without unhandled crash
                if not res["success"]:
                    assert "Error organizing downloads" in res["message"]
        finally:
            laptop_controller.downloads_dir = orig_dir

    def test_organize_downloads_nested_subdirectories_ignored(self, tmp_path: Path):
        """Verify existing subdirectories are not mistakenly treated as files or moved."""
        downloads_dir = tmp_path / "Downloads"
        downloads_dir.mkdir()

        nested_dir = downloads_dir / "Projects"
        nested_dir.mkdir()
        (nested_dir / "nested_file.txt").write_text("nested")

        sample_file = downloads_dir / "audio.mp3"
        sample_file.write_text("mp3 audio data")

        orig_dir = laptop_controller.downloads_dir
        try:
            laptop_controller.downloads_dir = downloads_dir
            res = laptop_controller.organize_downloads()
            assert res["success"] is True
            assert res["moved_count"] == 1
            # Nested dir should still be in original location
            assert (downloads_dir / "Projects" / "nested_file.txt").exists()
            assert (downloads_dir / "Audio" / "audio.mp3").exists()
        finally:
            laptop_controller.downloads_dir = orig_dir

    def test_organize_downloads_name_collision_with_identical_timestamp(self, tmp_path: Path):
        """Verify duplicate filename collision handling in target folder."""
        downloads_dir = tmp_path / "Downloads"
        downloads_dir.mkdir()

        # Create existing file in Images/
        images_dir = downloads_dir / "Images"
        images_dir.mkdir()
        existing = images_dir / "photo.png"
        existing.write_text("first photo")

        # Create new file with same name in Downloads root
        new_photo = downloads_dir / "photo.png"
        new_photo.write_text("second photo")

        orig_dir = laptop_controller.downloads_dir
        try:
            laptop_controller.downloads_dir = downloads_dir
            res = laptop_controller.organize_downloads()
            assert res["success"] is True
            assert res["moved_count"] == 1
            assert existing.exists()
            assert existing.read_text() == "first photo"
            images_files = list(images_dir.glob("photo*.png"))
            assert len(images_files) == 2
        finally:
            laptop_controller.downloads_dir = orig_dir
