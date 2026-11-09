"""
ATLAS — Development Specialist Agent
Handles software architecture, git repository analysis, bug investigations,
code reviews, and automated test execution.
"""
from __future__ import annotations

from typing import Any
from backend.app.agents.schema import AgentResult
from backend.app.tools.command_runner import command_runner
from backend.app.tools.file_ops import file_ops
from backend.app.core.logging_config import get_logger

logger = get_logger("agents.atlas")


class AtlasAgent:
    """Specialist development agent collaborating under JARVIS."""

    def __init__(self) -> None:
        self.name = "ATLAS"
        self.role = "Development & Architecture Specialist"

    def inspect_repository(self, task_id: str, repo_path: str | None = None) -> AgentResult:
        """Inspects git repository status, branch, and uncommitted modifications."""
        status_res = command_runner.run_command("git", ["status", "--short"], cwd=repo_path)
        log_res = command_runner.run_command("git", ["log", "-n", "3", "--oneline"], cwd=repo_path)

        findings = []
        warnings = []

        if not status_res["success"]:
            warnings.append(f"Git status failed: {status_res.get('error')}")
        else:
            changes = [line for line in status_res["stdout"].splitlines() if line.strip()]
            findings.append({
                "type": "uncommitted_changes",
                "count": len(changes),
                "modified_files": changes[:15],
            })

        if log_res["success"]:
            recent_commits = log_res["stdout"].splitlines()
            findings.append({
                "type": "recent_commits",
                "commits": recent_commits,
            })

        return AgentResult(
            agent=self.name,
            task_id=task_id,
            status="completed" if not warnings else "completed_with_warnings",
            summary=f"Repository analysis complete. Found {len(findings)} telemetry metrics.",
            findings=findings,
            warnings=warnings,
            requires_approval=False,
            evidence=[status_res.get("evidence", ""), log_res.get("evidence", "")],
        )

    def run_tests(self, task_id: str, test_target: str = "tests/") -> AgentResult:
        """Executes automated test suite and reports verified outcomes."""
        test_res = command_runner.run_command("pytest", [test_target, "-q"])
        exit_code = test_res.get("exit_code", -1)
        passed = (exit_code == 0)

        return AgentResult(
            agent=self.name,
            task_id=task_id,
            status="completed" if passed else "failed",
            summary="All test suites passed cleanly." if passed else "Test suite reported failures.",
            findings=[{
                "exit_code": exit_code,
                "stdout": test_res.get("stdout", "")[:2000],
                "stderr": test_res.get("stderr", "")[:2000],
            }],
            warnings=[] if passed else ["Regressions or failures detected in test run."],
            requires_approval=False,
            evidence=[test_res.get("evidence", "")],
        )


atlas_agent = AtlasAgent()
