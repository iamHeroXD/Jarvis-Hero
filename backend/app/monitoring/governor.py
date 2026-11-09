"""
JARVIS Performance & Thermal Governor
Protects the Intel Core i5 and 8 GB RAM environment from overheating,
excessive memory pressure, or battery drain. Automatically switches between
ECO, BALANCED, and PERFORMANCE profiles.
"""
from __future__ import annotations

import psutil
from enum import Enum
from typing import Any
from backend.app.core.logging_config import get_logger

logger = get_logger("monitoring.governor")


class PowerProfile(str, Enum):
    ECO = "eco"
    BALANCED = "balanced"
    PERFORMANCE = "performance"


class GovernorState:
    def __init__(
        self,
        profile: PowerProfile = PowerProfile.BALANCED,
        is_throttled: bool = False,
        target_particle_count: int = 1500,
        camera_fps_limit: int = 24,
        allow_background_indexing: bool = True,
    ) -> None:
        self.profile = profile
        self.is_throttled = is_throttled
        self.target_particle_count = target_particle_count
        self.camera_fps_limit = camera_fps_limit
        self.allow_background_indexing = allow_background_indexing

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile.value,
            "is_throttled": self.is_throttled,
            "target_particle_count": self.target_particle_count,
            "camera_fps_limit": self.camera_fps_limit,
            "allow_background_indexing": self.allow_background_indexing,
        }


class PerformanceGovernor:
    """Manages adaptive throttling based on real-time laptop telemetry."""

    def __init__(self) -> None:
        self.manual_profile: PowerProfile | None = None

    def evaluate_hardware_state(self) -> GovernorState:
        cpu_pct = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        mem_pct = mem.percent

        # If user explicitly forced a profile, prioritize it
        if self.manual_profile == PowerProfile.ECO:
            return GovernorState(
                profile=PowerProfile.ECO,
                is_throttled=True,
                target_particle_count=600,
                camera_fps_limit=15,
                allow_background_indexing=False,
            )

        # High pressure detection (Intel i5 dual-core / 8 GB RAM constraints)
        if cpu_pct > 80.0 or mem_pct > 85.0:
            logger.warning("Resource Governor Throttling Triggered: CPU %.1f%%, RAM %.1f%%", cpu_pct, mem_pct)
            return GovernorState(
                profile=PowerProfile.ECO,
                is_throttled=True,
                target_particle_count=800,
                camera_fps_limit=15,
                allow_background_indexing=False,
            )
        elif cpu_pct > 65.0 or mem_pct > 75.0:
            return GovernorState(
                profile=PowerProfile.BALANCED,
                is_throttled=False,
                target_particle_count=1500,
                camera_fps_limit=24,
                allow_background_indexing=True,
            )
        else:
            profile = self.manual_profile or PowerProfile.BALANCED
            particle_count = 2500 if profile == PowerProfile.PERFORMANCE else 1500
            return GovernorState(
                profile=profile,
                is_throttled=False,
                target_particle_count=particle_count,
                camera_fps_limit=30,
                allow_background_indexing=True,
            )


performance_governor = PerformanceGovernor()
