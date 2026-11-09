"""
JARVIS System Monitor
Tracks CPU, RAM, disk, and JARVIS process metrics.
Feeds data to the AI router and dashboard.
"""
from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime

import psutil

from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger

logger = get_logger("monitoring")


@dataclass
class SystemSnapshot:
    """Point-in-time system resource snapshot."""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    cpu_percent: float = 0.0
    ram_percent: float = 0.0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_free_gb: float = 0.0
    jarvis_cpu_percent: float = 0.0
    jarvis_ram_mb: float = 0.0
    internet_available: bool = True


class SystemMonitor:
    """
    Lightweight resource monitor.
    Polls periodically; does NOT continuously stream to Gemini.
    """

    _POLL_INTERVAL_SECONDS = 15

    def __init__(self) -> None:
        self._snapshot = SystemSnapshot()
        self._running = False
        self._task: asyncio.Task | None = None
        self._jarvis_process = psutil.Process(os.getpid())
        self._internet_check_url = "https://8.8.8.8"

    async def start(self) -> None:
        """Start background polling."""
        self._running = True
        self._task = asyncio.create_task(self._poll_loop(), name="system_monitor")
        logger.info("System monitor started.")

    async def stop(self) -> None:
        """Stop background polling."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("System monitor stopped.")

    async def _poll_loop(self) -> None:
        while self._running:
            try:
                await self._refresh()
            except Exception as exc:
                logger.debug("Monitor poll error: %s", exc)
            await asyncio.sleep(self._POLL_INTERVAL_SECONDS)

    async def _refresh(self) -> None:
        """Collect current metrics."""
        # CPU (non-blocking — uses an interval internally)
        cpu = psutil.cpu_percent(interval=None)

        # RAM
        mem = psutil.virtual_memory()
        ram_pct = mem.percent
        ram_used = mem.used / (1024 ** 3)
        ram_total = mem.total / (1024 ** 3)

        # Disk (C: drive)
        disk = psutil.disk_usage("C:\\")
        disk_pct = disk.percent
        disk_free = disk.free / (1024 ** 3)

        # JARVIS process metrics
        try:
            jarvis_cpu = self._jarvis_process.cpu_percent(interval=None)
            jarvis_mem = self._jarvis_process.memory_info().rss / (1024 ** 2)
        except psutil.NoSuchProcess:
            jarvis_cpu = 0.0
            jarvis_mem = 0.0

        # Internet connectivity (simple socket check)
        internet = await self._check_internet()

        self._snapshot = SystemSnapshot(
            cpu_percent=cpu,
            ram_percent=ram_pct,
            ram_used_gb=round(ram_used, 2),
            ram_total_gb=round(ram_total, 2),
            disk_percent=disk_pct,
            disk_free_gb=round(disk_free, 2),
            jarvis_cpu_percent=jarvis_cpu,
            jarvis_ram_mb=round(jarvis_mem, 1),
            internet_available=internet,
        )

        # Warn if resources are low
        if ram_pct > settings.max_ram_percent:
            logger.warning("RAM usage high: %.1f%%", ram_pct)
        if disk_free < 2.0:
            logger.warning("Disk space critically low: %.2f GB free", disk_free)

    async def _check_internet(self) -> bool:
        """Fast internet check using TCP socket — no cloud data sent."""
        try:
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(None, self._tcp_check),
                timeout=3.0,
            )
            return True
        except (asyncio.TimeoutError, OSError):
            return False

    @staticmethod
    def _tcp_check() -> None:
        import socket
        sock = socket.create_connection(("8.8.8.8", 53), timeout=2)
        sock.close()

    @property
    def snapshot(self) -> SystemSnapshot:
        return self._snapshot

    def get_status_dict(self) -> dict:
        s = self._snapshot
        return {
            "timestamp": s.timestamp.isoformat(),
            "cpu_percent": s.cpu_percent,
            "ram_percent": s.ram_percent,
            "ram_used_gb": s.ram_used_gb,
            "ram_total_gb": s.ram_total_gb,
            "disk_percent": s.disk_percent,
            "disk_free_gb": s.disk_free_gb,
            "jarvis_cpu_percent": s.jarvis_cpu_percent,
            "jarvis_ram_mb": s.jarvis_ram_mb,
            "internet_available": s.internet_available,
        }

    def should_reduce_load(self) -> bool:
        """True when resources are under pressure."""
        s = self._snapshot
        return s.ram_percent > settings.max_ram_percent or s.cpu_percent > settings.max_cpu_percent


# Global singleton
system_monitor = SystemMonitor()
