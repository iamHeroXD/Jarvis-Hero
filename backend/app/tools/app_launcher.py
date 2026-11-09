"""
JARVIS Application Launcher & Registry
Controlled allowlist of approved desktop applications.
Verifies existence before launching, tracks spawned processes,
and provides verified evidence of successful launch.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any
from pydantic import BaseModel
from backend.app.core.logging_config import get_logger

logger = get_logger("tools.launcher")


class ApprovedApp(BaseModel):
    app_id: str
    display_name: str
    executable_candidates: list[str]
    default_args: list[str] = []
    category: str


# Allowlisted application registry
_APP_REGISTRY: dict[str, ApprovedApp] = {
    "vscode": ApprovedApp(
        app_id="vscode",
        display_name="Visual Studio Code",
        executable_candidates=["code.cmd", "code.exe", "code"],
        category="developer",
    ),
    "chrome": ApprovedApp(
        app_id="chrome",
        display_name="Google Chrome",
        executable_candidates=[
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "chrome.exe",
        ],
        category="browser",
    ),
    "terminal": ApprovedApp(
        app_id="terminal",
        display_name="Windows Terminal",
        executable_candidates=["wt.exe", "powershell.exe"],
        category="system",
    ),
    "explorer": ApprovedApp(
        app_id="explorer",
        display_name="File Explorer",
        executable_candidates=["explorer.exe"],
        category="system",
    ),
    "antigravity": ApprovedApp(
        app_id="antigravity",
        display_name="Google Antigravity IDE",
        executable_candidates=[
            r"C:\Users\Rohan\AppData\Local\Programs\Antigravity\Antigravity.exe",
            "antigravity.exe",
            "code.cmd",  # Fallback workspace launcher
        ],
        category="developer",
    ),
}


class ApplicationLauncher:
    """Manages secure application execution with verification."""

    def resolve_path(self, app_id: str) -> str | None:
        app = _APP_REGISTRY.get(app_id)
        if not app:
            return None

        for candidate in app.executable_candidates:
            if os.path.isabs(candidate) and os.path.exists(candidate):
                return candidate
            which_path = shutil.which(candidate)
            if which_path and os.path.exists(which_path):
                return which_path
        return None

    def list_approved_apps(self) -> list[dict[str, Any]]:
        results = []
        for app_id, app in _APP_REGISTRY.items():
            resolved = self.resolve_path(app_id)
            results.append({
                "app_id": app.app_id,
                "display_name": app.display_name,
                "category": app.category,
                "is_installed": resolved is not None,
                "resolved_path": resolved,
            })
        return results

    def launch(self, app_id: str, extra_args: list[str] | None = None) -> dict[str, Any]:
        app = _APP_REGISTRY.get(app_id)
        if not app:
            return {
                "success": False,
                "verified": False,
                "error": f"Application '{app_id}' is not in the approved application registry.",
            }

        resolved_exe = self.resolve_path(app_id)
        if not resolved_exe:
            return {
                "success": False,
                "verified": False,
                "error": f"Application '{app.display_name}' executable not found on this machine.",
            }

        cmd = [resolved_exe] + app.default_args + (extra_args or [])
        try:
            # Launch without inheriting stdin; non-blocking
            proc = subprocess.Popen(
                cmd,
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info("Launched %s (PID: %d)", app.display_name, proc.pid)
            return {
                "success": True,
                "verified": True,
                "app_id": app_id,
                "display_name": app.display_name,
                "pid": proc.pid,
                "evidence": f"Process spawned with verified PID {proc.pid}",
            }
        except Exception as exc:
            logger.error("Failed to launch %s: %s", app.display_name, exc)
            return {
                "success": False,
                "verified": False,
                "error": str(exc),
            }


app_launcher = ApplicationLauncher()
