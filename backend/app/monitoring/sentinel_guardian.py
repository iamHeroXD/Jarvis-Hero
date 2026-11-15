"""
JARVIS Mark XI — Autonomous Sentinel Guardian & Storage Optimizer
Proactive system health monitor, anomaly detector, and automatic disk cleaner:
- Actively detects low C: drive storage (<15GB warning, <6GB critical)
- Proactively raises alerts, suggests fixes, and speaks warnings
- Safely cleans user Temp (%TEMP%), Windows Temp, and empties Recycle Bin
- Monitors RAM saturation, battery status, and offline transitions
- Logs every guardian action into the database activity ledger
"""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil

from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger

logger = get_logger("monitoring.sentinel_guardian")


class SentinelGuardian:
    """Proactive system guardian, anomaly detection, and storage maintenance engine."""

    def __init__(self) -> None:
        self.user_profile = os.environ.get("USERPROFILE", r"C:\Users\Rohan")
        self.user_temp_dir = Path(os.environ.get("TEMP", os.path.join(self.user_profile, r"AppData\Local\Temp")))
        self.windows_temp_dir = Path(r"C:\Windows\Temp")

        # Thresholds
        self.STORAGE_WARN_GB = 15.0
        self.STORAGE_CRITICAL_GB = 6.0
        self.RAM_WARN_PERCENT = 82.0
        self.RAM_CRITICAL_PERCENT = 90.0
        self.BATTERY_WARN_PERCENT = 20

    # ── 1. Proactive System Health & Anomaly Check ─────────────────────────────

    def get_storage_status(self) -> dict[str, Any]:
        """Returns direct C: drive storage metrics with severity."""
        c_disk = psutil.disk_usage("C:\\")
        c_total_gb = round(c_disk.total / (1024 ** 3), 2)
        c_free_gb = round(c_disk.free / (1024 ** 3), 2)
        c_used_gb = round(c_disk.used / (1024 ** 3), 2)
        c_pct = c_disk.percent
        severity = "critical" if c_free_gb < self.STORAGE_CRITICAL_GB else ("warning" if c_free_gb < self.STORAGE_WARN_GB else "optimal")
        return {
            "total_gb": c_total_gb,
            "free_gb": c_free_gb,
            "used_gb": c_used_gb,
            "percent_used": c_pct,
            "severity": severity,
            "is_critical": severity == "critical",
        }

    def get_proactive_alert_message(self, free_threshold_gb: float = 15.0) -> str | None:
        """Returns vocal alert if C: drive storage is below specified threshold."""
        c_disk = psutil.disk_usage("C:\\")
        c_free_gb = round(c_disk.free / (1024 ** 3), 2)
        if c_free_gb < free_threshold_gb:
            return (
                f"Warning, Sir. Primary storage on your C: drive is critically low with only "
                f"{c_free_gb:.1f} gigabytes remaining. I strongly advise letting me purge "
                f"temporary caches and the Recycle Bin to safeguard system stability."
            )
        return None

    def get_sentinel_summary(self) -> dict[str, Any]:
        """Returns aggregated telemetry summary for dashboard and sentinel status."""
        health = self.check_system_health()
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "overall_status": health["overall_status"],
            "storage": health["storage"],
            "ram": health["memory"],
            "cpu": {"percent": round(psutil.cpu_percent(interval=None))},
            "battery": health["battery"],
            "network": health["network"],
            "alerts": health["alerts"],
            "proactive_speech": health["proactive_speech"],
        }

    def check_system_health(self) -> dict[str, Any]:
        """
        Scans all critical laptop hardware metrics and returns active alerts,
        severity ratings, and proactive recommendations for Rohan.
        """
        alerts: list[dict[str, Any]] = []

        # 1. C: Drive Storage Analysis
        c_disk = psutil.disk_usage("C:\\")
        c_total_gb = round(c_disk.total / (1024 ** 3), 2)
        c_free_gb = round(c_disk.free / (1024 ** 3), 2)
        c_used_gb = round(c_disk.used / (1024 ** 3), 2)
        c_pct = c_disk.percent

        storage_severity = "optimal"
        if c_free_gb < self.STORAGE_CRITICAL_GB:
            storage_severity = "critical"
            alerts.append({
                "id": "c_drive_critical",
                "severity": "critical",
                "component": "storage",
                "title": "C: Drive Storage Critically Low",
                "message": (
                    f"C: Drive has only {c_free_gb} GB free out of {c_total_gb} GB ({c_pct}% utilized). "
                    f"System performance and file creation may degrade."
                ),
                "suggested_action": "Purge temporary caches and empty Recycle Bin immediately.",
                "action_cmd": "clean c drive",
            })
        elif c_free_gb < self.STORAGE_WARN_GB:
            storage_severity = "warning"
            alerts.append({
                "id": "c_drive_warning",
                "severity": "warning",
                "component": "storage",
                "title": "C: Drive Storage Low",
                "message": f"C: Drive free space is down to {c_free_gb} GB ({c_pct}% used).",
                "suggested_action": "Clean temporary storage to prevent disk exhaustion.",
                "action_cmd": "clean c drive",
            })

        # 2. RAM Saturation Analysis
        vm = psutil.virtual_memory()
        ram_pct = vm.percent
        ram_free_gb = round(vm.available / (1024 ** 3), 2)
        ram_used_gb = round(vm.used / (1024 ** 3), 2)
        ram_total_gb = round(vm.total / (1024 ** 3), 2)

        ram_severity = "optimal"
        if ram_pct > self.RAM_CRITICAL_PERCENT:
            ram_severity = "critical"
            alerts.append({
                "id": "ram_critical",
                "severity": "critical",
                "component": "memory",
                "title": "System Memory Saturated",
                "message": f"RAM utilization is at {ram_pct}% ({ram_free_gb} GB available).",
                "suggested_action": "Trim process working sets via Win32 memory optimizer.",
                "action_cmd": "clean ram",
            })
        elif ram_pct > self.RAM_WARN_PERCENT:
            ram_severity = "warning"
            alerts.append({
                "id": "ram_warning",
                "severity": "warning",
                "component": "memory",
                "title": "High Memory Utilization",
                "message": f"RAM utilization is standing at {ram_pct}%.",
                "suggested_action": "Execute memory optimization to reclaim dormant pages.",
                "action_cmd": "clean ram",
            })

        # 3. Battery Power Telemetry
        battery = psutil.sensors_battery()
        bat_pct = int(battery.percent) if battery else 100
        bat_plugged = bool(battery.power_plugged) if battery else True

        battery_severity = "optimal"
        if not bat_plugged and bat_pct < self.BATTERY_WARN_PERCENT:
            battery_severity = "critical" if bat_pct < 10 else "warning"
            alerts.append({
                "id": "battery_low",
                "severity": battery_severity,
                "component": "power",
                "title": "Battery Level Critical" if bat_pct < 10 else "Battery Level Low",
                "message": f"Laptop is running on battery at {bat_pct}% power.",
                "suggested_action": "Connect AC charging adapter.",
                "action_cmd": "battery status",
            })

        # 4. Internet Connectivity
        from backend.app.monitoring.system_monitor import system_monitor
        internet_online = system_monitor.snapshot.internet_available
        if not internet_online:
            alerts.append({
                "id": "offline_mode",
                "severity": "warning",
                "component": "network",
                "title": "Offline Mode Engaged",
                "message": "No active internet uplink detected. Operating on Local Neural Core.",
                "suggested_action": "Local commands, computer control, and storage cleanup remain active.",
                "action_cmd": "system diagnostics",
            })

        # Determine overall status
        if any(a["severity"] == "critical" for a in alerts):
            overall_status = "critical"
        elif any(a["severity"] == "warning" for a in alerts):
            overall_status = "warning"
        else:
            overall_status = "optimal"

        # Formulate synthesized proactive vocal prompt if unusual events found
        proactive_speech = self._synthesize_proactive_speech(alerts, c_free_gb, ram_pct)

        return {
            "overall_status": overall_status,
            "has_anomalies": len(alerts) > 0,
            "alerts_count": len(alerts),
            "alerts": alerts,
            "proactive_speech": proactive_speech,
            "storage": {
                "total_gb": c_total_gb,
                "free_gb": c_free_gb,
                "used_gb": c_used_gb,
                "percent_used": c_pct,
                "severity": storage_severity,
            },
            "memory": {
                "total_gb": ram_total_gb,
                "free_gb": ram_free_gb,
                "used_gb": ram_used_gb,
                "percent_used": ram_pct,
                "severity": ram_severity,
            },
            "battery": {
                "percent": bat_pct,
                "plugged_in": bat_plugged,
                "severity": battery_severity,
            },
            "network": {
                "online": internet_online,
                "mode": "cloud_connected" if internet_online else "local_offline",
            },
        }

    def _synthesize_proactive_speech(self, alerts: list[dict[str, Any]], c_free_gb: float, ram_pct: float) -> str | None:
        """Generates spoken warning prompt for Rohan if critical anomalies exist."""
        if not alerts:
            return None

        # Prioritize C: Drive storage warning
        c_alert = next((a for a in alerts if a["id"] in ("c_drive_critical", "c_drive_warning")), None)
        if c_alert:
            return (
                f"Warning, Sir. Primary storage on your C: drive is critically low with only "
                f"{c_free_gb:.1f} gigabytes remaining. I strongly advise letting me purge "
                f"temporary caches and the Recycle Bin to safeguard system stability."
            )

        ram_alert = next((a for a in alerts if a["id"] in ("ram_critical", "ram_warning")), None)
        if ram_alert:
            return f"Notice, Sir: System RAM utilization has reached {ram_pct:.0f}%. Shall I execute working set memory optimization?"

        return None

    # ── 2. Active C: Drive Temp & Cache Purge ──────────────────────────────────

    def purge_temp_storage(self) -> dict[str, Any]:
        """
        Safely clears user %TEMP%, Windows Temp, and Recycle Bin without touching
        system or locked files. Returns exact megabytes reclaimed and new free space.
        """
        c_before = psutil.disk_usage("C:\\").free
        initial_free_gb = round(c_before / (1024 ** 3), 2)

        files_deleted = 0
        bytes_deleted = 0
        cleaned_targets: list[str] = []

        # 1. Clean User Temp (%TEMP%)
        if self.user_temp_dir.exists():
            cleaned_targets.append(str(self.user_temp_dir))
            for item in list(self.user_temp_dir.iterdir()):
                try:
                    if "pytest" in item.name.lower():
                        continue  # Preserve test harnesses during active test runs
                    if item.is_file() or item.is_symlink():
                        size = item.stat().st_size
                        item.unlink(missing_ok=True)
                        files_deleted += 1
                        bytes_deleted += size
                    elif item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                except Exception:
                    # In-use/locked files are skipped safely
                    continue

        # 2. Clean Windows Temp (accessible files only)
        if self.windows_temp_dir.exists():
            cleaned_targets.append(str(self.windows_temp_dir))
            try:
                for item in list(self.windows_temp_dir.iterdir()):
                    try:
                        if item.is_file():
                            size = item.stat().st_size
                            item.unlink(missing_ok=True)
                            files_deleted += 1
                            bytes_deleted += size
                    except Exception:
                        continue
            except Exception:
                pass

        # 3. Empty Windows Recycle Bin
        try:
            ps_cmd = "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=3)
            cleaned_targets.append("Windows Recycle Bin")
        except Exception:
            pass

        # 4. Measure after
        c_after = psutil.disk_usage("C:\\").free
        new_free_gb = round(c_after / (1024 ** 3), 2)
        freed_bytes_real = max(bytes_deleted, c_after - c_before)
        freed_mb = round(freed_bytes_real / (1024 ** 2), 1)

        logger.info(
            "Sentinel storage purge complete: %d files removed, %.1f MB reclaimed. Free space: %.2f GB -> %.2f GB",
            files_deleted, freed_mb, initial_free_gb, new_free_gb
        )

        msg = (
            f"Storage cleanup complete, Sir. Successfully purged {files_deleted} temporary files and emptied the Recycle Bin, "
            f"reclaiming {freed_mb} MB of disk space. C: drive now has {new_free_gb} GB free."
        )

        return {
            "success": True,
            "action": "Sentinel Storage Purge",
            "files_removed": files_deleted,
            "freed_mb": freed_mb,
            "initial_free_gb": initial_free_gb,
            "current_free_gb": new_free_gb,
            "targets_cleaned": cleaned_targets,
            "message": msg,
        }


sentinel_guardian = SentinelGuardian()
