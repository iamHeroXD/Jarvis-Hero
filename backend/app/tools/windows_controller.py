"""
JARVIS Mark X — Windows Computer Control & Process Verification Layer
Provides reliable Windows OS operations with verified execution:
- Process launch with post-execution polling & PID verification
- Active desktop application listing & telemetry
- Safe termination with confirmation
- Win32 virtual keystroke automation
- Verified system power, volume, and desktop controls
"""
from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import psutil

from backend.app.core.logging_config import get_logger

logger = get_logger("tools.windows_controller")


class WindowsComputerController:
    """Enterprise-grade Windows OS Computer Controller with execution verification."""

    def __init__(self) -> None:
        self.user_profile = os.environ.get("USERPROFILE", r"C:\Users\Rohan")
        self._user32 = ctypes.windll.user32
        self._kernel32 = ctypes.windll.kernel32

        # Primary application registry mapped to real verified executables
        self.verified_app_registry: dict[str, dict[str, Any]] = {
            "chrome": {
                "name": "Google Chrome",
                "exe": "chrome.exe",
                "path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "synonyms": ["chrome", "google chrome", "browser"],
            },
            "vscode": {
                "name": "Visual Studio Code",
                "exe": "Code.exe",
                "path": os.path.join(self.user_profile, r"AppData\Local\Programs\Microsoft VS Code\Code.exe"),
                "synonyms": ["code", "vscode", "vs code", "visual studio code"],
            },
            "antigravity": {
                "name": "Antigravity IDE",
                "exe": "Antigravity IDE.exe",
                "fallback_exe": "Antigravity.exe",
                "path": os.path.join(self.user_profile, r"AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe"),
                "fallback_path": os.path.join(self.user_profile, r"AppData\Local\Programs\Antigravity\Antigravity.exe"),
                "synonyms": ["antigravity", "antigravity ide", "agy", "anti-gravity", "anti gravity"],
            },
            "spotify": {
                "name": "Spotify",
                "exe": "Spotify.exe",
                "path": os.path.join(self.user_profile, r"AppData\Roaming\Spotify\Spotify.exe"),
                "synonyms": ["spotify", "music", "songs"],
            },
            "discord": {
                "name": "Discord",
                "exe": "Discord.exe",
                "path": os.path.join(self.user_profile, r"AppData\Local\Discord\Update.exe"),
                "args": ["--processStart", "Discord.exe"],
                "synonyms": ["discord", "chat"],
            },
            "notepad": {
                "name": "Notepad",
                "exe": "notepad.exe",
                "path": r"C:\Windows\System32\notepad.exe",
                "synonyms": ["notepad", "notes", "text editor"],
            },
            "calculator": {
                "name": "Calculator",
                "exe": "CalculatorApp.exe",
                "fallback_exe": "calc.exe",
                "path": r"C:\Windows\System32\calc.exe",
                "synonyms": ["calc", "calculator", "math"],
            },
            "terminal": {
                "name": "Windows Terminal",
                "exe": "wt.exe",
                "fallback_exe": "cmd.exe",
                "path": os.path.join(self.user_profile, r"AppData\Local\Microsoft\WindowsApps\wt.exe"),
                "fallback_path": r"C:\Windows\System32\cmd.exe",
                "synonyms": ["terminal", "powershell", "cmd", "command prompt"],
            },
            "explorer": {
                "name": "File Explorer",
                "exe": "explorer.exe",
                "path": r"C:\Windows\explorer.exe",
                "synonyms": ["explorer", "files", "my computer", "this pc"],
            },
            "taskmanager": {
                "name": "Task Manager",
                "exe": "taskmgr.exe",
                "path": r"C:\Windows\System32\taskmgr.exe",
                "synonyms": ["task manager", "taskmgr", "processes", "activity monitor"],
            },
            "settings": {
                "name": "Windows Settings",
                "exe": "SystemSettings.exe",
                "protocol": "ms-settings:",
                "synonyms": ["settings", "windows settings", "control panel"],
            },
            "paint": {
                "name": "Paint",
                "exe": "mspaint.exe",
                "path": r"C:\Windows\System32\mspaint.exe",
                "synonyms": ["paint", "mspaint", "draw"],
            },
            "snippingtool": {
                "name": "Snipping Tool",
                "exe": "SnippingTool.exe",
                "path": r"C:\Windows\System32\SnippingTool.exe",
                "synonyms": ["snipping tool", "screenshot", "snip"],
            },
        }

    # ── Process Verification & Monitoring ─────────────────────────────────────

    def is_process_running(self, exe_name: str) -> bool:
        """Checks if any process matches the target executable name."""
        target = exe_name.lower().strip()
        for p in psutil.process_iter(["name"]):
            try:
                name = p.info.get("name")
                if name and name.lower() == target:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def get_process_info(self, exe_name: str) -> dict[str, Any] | None:
        """Retrieves real-time telemetry for a named process."""
        target = exe_name.lower().strip()
        for p in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
            try:
                if p.info["name"] and p.info["name"].lower() == target:
                    mem_mb = round(p.info["memory_info"].rss / (1024 * 1024), 1)
                    return {
                        "pid": p.info["pid"],
                        "name": p.info["name"],
                        "memory_mb": mem_mb,
                        "cpu_percent": p.info.get("cpu_percent", 0.0),
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def poll_process_launched(self, exe_name: str, timeout_sec: float = 1.8) -> dict[str, Any]:
        """Polls the Windows process table to verify process execution after launch."""
        start = time.perf_counter()
        target = exe_name.lower().strip()

        while (time.perf_counter() - start) < timeout_sec:
            info = self.get_process_info(target)
            if info:
                elapsed_ms = round((time.perf_counter() - start) * 1000)
                return {
                    "verified": True,
                    "pid": info["pid"],
                    "memory_mb": info["memory_mb"],
                    "verification_ms": elapsed_ms,
                }
            time.sleep(0.08)

        return {
            "verified": False,
            "pid": None,
            "memory_mb": 0,
            "verification_ms": round(timeout_sec * 1000),
        }

    # ── Verified Application Launch ───────────────────────────────────────────

    def launch_app_verified(self, app_query: str) -> dict[str, Any]:
        """
        Launches an application and verifies that the process actually spawned.
        Returns verified execution telemetry, PID, and user-facing message.
        """
        q = app_query.lower().strip()
        clean_q = q.replace("open ", "").replace("launch ", "").replace("start ", "").strip()

        matched_app: dict[str, Any] | None = None
        for key, info in self.verified_app_registry.items():
            if clean_q == key or clean_q in info.get("synonyms", []):
                matched_app = info
                break

        if not matched_app:
            # Fallback to general lookup
            return {
                "success": False,
                "verified": False,
                "app": app_query,
                "message": f"Application '{app_query}' is not in the verified registry, Sir.",
            }

        app_name = matched_app["name"]
        primary_exe = matched_app.get("exe", "")
        target_path = matched_app.get("path")
        args = matched_app.get("args")
        proto = matched_app.get("protocol")

        # 1. Check if already running
        if primary_exe and self.is_process_running(primary_exe):
            proc_info = self.get_process_info(primary_exe)
            return {
                "success": True,
                "verified": True,
                "already_running": True,
                "app": app_name,
                "pid": proc_info["pid"] if proc_info else None,
                "message": f"{app_name} is already active on your desktop, Sir.",
            }

        # 2. Execute launch
        launched = False
        if target_path and os.path.exists(target_path):
            try:
                if args:
                    subprocess.Popen([target_path] + args)
                else:
                    os.startfile(target_path)
                launched = True
            except Exception as err:
                logger.warning("os.startfile failed for %s: %s", target_path, err)

        if not launched:
            fallback_path = matched_app.get("fallback_path")
            if fallback_path and os.path.exists(fallback_path):
                try:
                    os.startfile(fallback_path)
                    launched = True
                except Exception:
                    pass

        if not launched and proto:
            try:
                subprocess.Popen(f'start "" "{proto}"', shell=True)
                launched = True
            except Exception:
                pass

        if not launched:
            return {
                "success": False,
                "verified": False,
                "app": app_name,
                "message": f"Could not locate an executable for {app_name}, Sir.",
            }

        # 3. Post-execution verification poll (<1.8s)
        poll_res = self.poll_process_launched(primary_exe, timeout_sec=1.5)
        if poll_res["verified"]:
            return {
                "success": True,
                "verified": True,
                "already_running": False,
                "app": app_name,
                "pid": poll_res["pid"],
                "memory_mb": poll_res["memory_mb"],
                "verification_ms": poll_res["verification_ms"],
                "message": f"Right away, Sir. {app_name} launched and verified running (PID {poll_res['pid']}).",
            }
        else:
            return {
                "success": True,
                "verified": False,
                "already_running": False,
                "app": app_name,
                "pid": None,
                "message": f"Launch signal dispatched for {app_name}, Sir. Awaiting window initialization.",
            }

    # ── Running Desktop Applications Inspection ───────────────────────────────

    def get_running_applications(self, limit: int = 15) -> list[dict[str, Any]]:
        """Returns verified list of active desktop applications with resource metrics."""
        apps: list[dict[str, Any]] = []
        known_exes = {info.get("exe", "").lower(): info["name"] for info in self.verified_app_registry.values()}

        for p in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
            try:
                name = p.info.get("name")
                if not name:
                    continue
                name_lower = name.lower()
                if name_lower in known_exes:
                    mem_mb = round(p.info["memory_info"].rss / (1024 * 1024), 1)
                    apps.append({
                        "name": known_exes[name_lower],
                        "exe": name,
                        "pid": p.info["pid"],
                        "memory_mb": mem_mb,
                        "cpu_percent": p.info.get("cpu_percent", 0.0),
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by memory usage descending
        apps.sort(key=lambda a: a["memory_mb"], reverse=True)
        return apps[:limit]

    # ── Safe Application Termination ──────────────────────────────────────────

    def terminate_application(self, app_query: str) -> dict[str, Any]:
        """Safely terminates an application and verifies process exit."""
        q = app_query.lower().strip()
        matched_info = None
        for key, info in self.verified_app_registry.items():
            if q == key or q in info.get("synonyms", []):
                matched_info = info
                break

        exe = matched_info.get("exe") if matched_info else (q if q.endswith(".exe") else f"{q}.exe")
        app_name = matched_info.get("name") if matched_info else exe

        if not self.is_process_running(exe):
            return {
                "success": True,
                "verified": True,
                "app": app_name,
                "message": f"{app_name} is not currently running, Sir.",
            }

        try:
            res = subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True, text=True, timeout=3)
            # Verify exit
            time.sleep(0.15)
            still_running = self.is_process_running(exe)
            if not still_running:
                return {
                    "success": True,
                    "verified": True,
                    "app": app_name,
                    "message": f"{app_name} terminated successfully, Sir.",
                }
            else:
                return {
                    "success": False,
                    "verified": False,
                    "app": app_name,
                    "message": f"Process {exe} did not exit after termination signal.",
                }
        except Exception as e:
            return {"success": False, "verified": False, "app": app_name, "message": f"Termination failed: {e}"}

    # ── Fast Native Keystroke Operations ──────────────────────────────────────

    def adjust_volume(self, action: str) -> dict[str, Any]:
        """Adjusts system volume via Win32 virtual keystrokes in <0.2ms."""
        action = str(action or "").lower().strip()
        VK_VOLUME_MUTE = 0xAD
        VK_VOLUME_DOWN = 0xAE
        VK_VOLUME_UP = 0xAF
        KEYEVENTF_KEYUP = 0x0002

        try:
            if action == "up":
                for _ in range(5):
                    self._user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
                    self._user32.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_KEYUP, 0)
                return {"success": True, "message": "Master volume increased, Sir."}
            elif action == "down":
                for _ in range(5):
                    self._user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
                    self._user32.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_KEYUP, 0)
                return {"success": True, "message": "Master volume lowered, Sir."}
            elif action in ("mute", "unmute"):
                self._user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
                self._user32.keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, 0)
                return {"success": True, "message": "Audio mute toggled, Sir."}
            else:
                return {"success": False, "message": f"Unknown volume action: {action}"}
        except Exception as err:
            return {"success": False, "message": f"Volume control failed: {err}"}

    def lock_workstation(self) -> dict[str, Any]:
        """Locks the Windows desktop instantly in <1ms."""
        try:
            self._user32.LockWorkStation()
            return {"success": True, "message": "Workstation secured and locked, Sir."}
        except Exception as err:
            return {"success": False, "message": f"Lock failed: {err}"}

    def minimize_all_windows(self) -> dict[str, Any]:
        """Minimizes all windows to reveal desktop."""
        try:
            ps_cmd = "(New-Object -ComObject Shell.Application).MinimizeAll()"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=2)
            return {"success": True, "message": "All windows minimized, Sir. Desktop visible."}
        except Exception as err:
            return {"success": False, "message": f"Minimize all failed: {err}"}


windows_controller = WindowsComputerController()
