"""
JARVIS Antigravity Development Bridge
Provides workspace detection, prompt dispatch, development tracking,
and artifact management for the Google Antigravity environment.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from backend.app.core.config import PROJECT_ROOT
from backend.app.core.logging_config import get_logger

logger = get_logger("integrations.antigravity")


class AntigravityBridge:
    """Interfaces with Antigravity workspace and artifact directories."""

    def __init__(self) -> None:
        self.workspace_root = PROJECT_ROOT
        self.brain_dir = Path(os.path.expanduser("~")) / ".gemini" / "antigravity" / "brain"

    def check_environment_capabilities(self) -> dict[str, Any]:
        """Detects whether Antigravity directories and capabilities are active."""
        brain_exists = self.brain_dir.exists()
        return {
            "antigravity_workspace": str(self.workspace_root),
            "brain_directory_present": brain_exists,
            "bridge_status": "ready" if brain_exists else "standalone",
            "supported_modes": ["prompt_export", "isolated_worktree", "direct_artifact"],
        }

    def export_development_task(
        self,
        task_id: str,
        title: str,
        prompt_content: str,
    ) -> Path:
        """
        Exports a generated development prompt as a tracked markdown artifact
        ready for execution or manual review.
        """
        export_dir = self.workspace_root / "data" / "evolution"
        export_dir.mkdir(parents=True, exist_ok=True)
        file_path = export_dir / f"{task_id}_{title.lower().replace(' ', '_')}.md"
        file_path.write_text(prompt_content, encoding="utf-8")
        logger.info("Antigravity task artifact exported to %s", file_path)
        return file_path


antigravity_bridge = AntigravityBridge()
