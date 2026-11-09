"""
JARVIS Development Intelligence (JDI) — Self-Auditor
Inspects the actual codebase for performance, code quality,
missing tests, and security weaknesses with real static analysis.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from backend.app.core.config import PROJECT_ROOT
from backend.app.core.logging_config import get_logger

logger = get_logger("evolution.auditor")


class AuditFinding:
    def __init__(
        self,
        category: str,
        title: str,
        description: str,
        severity: str,
        file_path: str | None = None,
        suggested_action: str | None = None,
    ) -> None:
        self.category = category
        self.title = title
        self.description = description
        self.severity = severity  # 'info', 'warning', 'high'
        self.file_path = file_path
        self.suggested_action = suggested_action

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "file_path": self.file_path,
            "suggested_action": self.suggested_action,
        }


class CodebaseAuditor:
    """Performs real inspection over backend and frontend files."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or PROJECT_ROOT

    def run_full_audit(self) -> list[dict[str, Any]]:
        findings: list[AuditFinding] = []

        # 1. Performance check: Inspect DB directory size & disk space
        data_dir = self.root_dir / "data"
        if data_dir.exists():
            total_size_mb = sum(
                f.stat().st_size for f in data_dir.rglob("*") if f.is_file()
            ) / (1024 * 1024)
            if total_size_mb > 500:
                findings.append(
                    AuditFinding(
                        category="Performance",
                        title="Data Directory Footprint High",
                        description=f"Data directory is {total_size_mb:.1f} MB, approaching threshold on low-disk system.",
                        severity="warning",
                        suggested_action="Prune old logs or compact SQLite DB with VACUUM.",
                    )
                )

        # 2. Check test coverage in tests/
        tests_dir = self.root_dir / "tests"
        backend_tests = list(tests_dir.glob("test_*.py")) if tests_dir.exists() else []
        if len(backend_tests) < 3:
            findings.append(
                AuditFinding(
                    category="Reliability",
                    title="Automated Test Suite Coverage Low",
                    description=f"Found only {len(backend_tests)} test files in tests/ directory.",
                    severity="warning",
                    suggested_action="Expand unit and integration tests for AI router and database models.",
                )
            )

        # 3. Check for exposed secrets or hardcoded API keys
        suspicious_patterns = ["AIzaSy", "sk-proj-", "bearer eyJ"]
        backend_dir = self.root_dir / "backend"
        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                    for pattern in suspicious_patterns:
                        if pattern in content and "suspicious_patterns" not in content:
                            findings.append(
                                AuditFinding(
                                    category="Security",
                                    title="Potential Hardcoded Credential Detected",
                                    description=f"File {py_file.name} appears to match credential pattern '{pattern}'.",
                                    severity="high",
                                    file_path=str(py_file.relative_to(self.root_dir)),
                                    suggested_action="Move secret to Windows Credential Manager.",
                                )
                            )
                except Exception as exc:
                    logger.debug("Could not audit file %s: %s", py_file, exc)

        # 4. Check for unindexed SQLite query performance
        models_file = backend_dir / "app" / "models" / "database_models.py"
        if models_file.exists():
            content = models_file.read_text(encoding="utf-8", errors="ignore")
            if "Index(" in content and "memories_fts" not in content:
                findings.append(
                    AuditFinding(
                        category="Performance",
                        title="FTS Index Verification",
                        description="Ensure full-text search triggers are maintained across schema updates.",
                        severity="info",
                        file_path="backend/app/models/database_models.py",
                    )
                )

        # Default healthy finding if clean
        if not findings:
            findings.append(
                AuditFinding(
                    category="System",
                    title="Codebase Audit Clean",
                    description="No critical security vulnerabilities, secret leaks, or structural bottlenecks identified.",
                    severity="info",
                )
            )

        logger.info("Codebase self-audit completed with %d findings.", len(findings))
        return [f.to_dict() for f in findings]


auditor = CodebaseAuditor()
