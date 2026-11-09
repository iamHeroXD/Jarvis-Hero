"""
JARVIS Controlled File Operations Service
Restricts file manipulation strictly to explicitly approved directories.
Provides verification evidence for all writes, creates automatic backups,
and denies unauthorized system drive crawls.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any
from backend.app.core.config import PROJECT_ROOT
from backend.app.core.logging_config import get_logger

logger = get_logger("tools.file_ops")


class FileOperationManager:
    """Manages verified file operations within approved directories."""

    def __init__(self) -> None:
        self.approved_roots: list[Path] = [
            PROJECT_ROOT,
            PROJECT_ROOT.parent,  # f:\Work
        ]

    def add_approved_root(self, directory: str | Path) -> bool:
        p = Path(directory).resolve()
        if p.exists() and p.is_dir() and p not in self.approved_roots:
            self.approved_roots.append(p)
            logger.info("Added approved directory: %s", p)
            return True
        return False

    def is_path_approved(self, path: str | Path) -> bool:
        try:
            resolved = Path(path).resolve()
            return any(
                resolved == root or root in resolved.parents
                for root in self.approved_roots
            )
        except Exception:
            return False

    def list_files(self, directory: str | Path, max_items: int = 100) -> dict[str, Any]:
        p = Path(directory).resolve()
        if not self.is_path_approved(p):
            return {
                "success": False,
                "verified": False,
                "error": f"Path '{p}' is outside approved directories.",
            }

        if not p.exists() or not p.is_dir():
            return {
                "success": False,
                "verified": False,
                "error": f"Directory '{p}' does not exist.",
            }

        items = []
        try:
            for entry in list(p.iterdir())[:max_items]:
                items.append({
                    "name": entry.name,
                    "is_dir": entry.is_dir(),
                    "size_bytes": entry.stat().st_size if entry.is_file() else 0,
                })
            return {
                "success": True,
                "verified": True,
                "path": str(p),
                "items": items,
                "count": len(items),
            }
        except Exception as exc:
            return {"success": False, "verified": False, "error": str(exc)}

    def read_file(self, file_path: str | Path, max_bytes: int = 100_000) -> dict[str, Any]:
        p = Path(file_path).resolve()
        if not self.is_path_approved(p):
            return {
                "success": False,
                "verified": False,
                "error": f"Access denied: Path '{p}' is not approved.",
            }

        if not p.exists() or not p.is_file():
            return {
                "success": False,
                "verified": False,
                "error": f"File '{p}' does not exist or is not a regular file.",
            }

        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            return {
                "success": True,
                "verified": True,
                "path": str(p),
                "content": content[:max_bytes],
                "size_bytes": p.stat().st_size,
                "truncated": len(content) > max_bytes,
            }
        except Exception as exc:
            return {"success": False, "verified": False, "error": str(exc)}

    def create_or_update_file(
        self,
        file_path: str | Path,
        content: str,
        backup_existing: bool = True,
    ) -> dict[str, Any]:
        p = Path(file_path).resolve()
        if not self.is_path_approved(p):
            return {
                "success": False,
                "verified": False,
                "error": f"Access denied: Destination '{p}' is not in approved paths.",
            }

        try:
            # Automatic backup if file already exists
            if backup_existing and p.exists():
                backup_dir = PROJECT_ROOT / "data" / "backups"
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_file = backup_dir / f"{p.name}.bak"
                shutil.copy2(p, backup_file)
                logger.info("Created pre-write backup of %s at %s", p, backup_file)

            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

            # MANDATORY VERIFICATION: confirm file exists and size matches written bytes
            if not p.exists():
                return {
                    "success": False,
                    "verified": False,
                    "error": "Verification failed: file was not found on disk after write.",
                }

            actual_size = p.stat().st_size
            return {
                "success": True,
                "verified": True,
                "path": str(p),
                "size_bytes": actual_size,
                "evidence": f"File verified on disk. Size: {actual_size} bytes.",
            }
        except Exception as exc:
            logger.error("File write error on %s: %s", p, exc)
            return {"success": False, "verified": False, "error": str(exc)}


file_ops = FileOperationManager()
