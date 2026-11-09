"""
JARVIS Verification Engine
Validates that physical or software actions actually succeeded.
Never claims an operation succeeded without verified evidence.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import psutil
from backend.app.core.logging_config import get_logger

logger = get_logger("tasks.verification")


class VerificationResult:
    def __init__(self, verified: bool, evidence: str, errors: list[str] | None = None) -> None:
        self.verified = verified
        self.evidence = evidence
        self.errors = errors or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "verified": self.verified,
            "evidence": self.evidence,
            "errors": self.errors,
        }


class VerificationEngine:
    """Verifies that requested changes occurred in reality."""

    def verify_file_exists(self, file_path: str | Path, min_bytes: int = 1) -> VerificationResult:
        p = Path(file_path).resolve()
        if not p.exists():
            return VerificationResult(
                verified=False,
                evidence="File existence check failed.",
                errors=[f"File '{p}' does not exist on disk."],
            )
        size = p.stat().st_size
        if size < min_bytes:
            return VerificationResult(
                verified=False,
                evidence=f"File exists but is empty ({size} bytes).",
                errors=[f"Expected minimum {min_bytes} bytes, found {size} bytes."],
            )
        return VerificationResult(
            verified=True,
            evidence=f"File verified on disk at '{p}' with size {size} bytes.",
        )

    def verify_process_running(self, pid: int) -> VerificationResult:
        try:
            proc = psutil.Process(pid)
            if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                return VerificationResult(
                    verified=True,
                    evidence=f"Process with PID {pid} ({proc.name()}) is running actively.",
                )
            return VerificationResult(
                verified=False,
                evidence=f"Process {pid} found but is in state {proc.status()}.",
                errors=[f"Process {pid} not in active state."],
            )
        except psutil.NoSuchProcess:
            return VerificationResult(
                verified=False,
                evidence=f"Process {pid} does not exist.",
                errors=[f"PID {pid} could not be verified in operating system process table."],
            )

    def verify_test_suite_passed(self, exit_code: int, stdout: str) -> VerificationResult:
        if exit_code == 0:
            return VerificationResult(
                verified=True,
                evidence=f"Test suite exited with code 0 (Success). Output: {stdout[:200]}...",
            )
        return VerificationResult(
            verified=False,
            evidence=f"Test suite failed with exit code {exit_code}.",
            errors=["One or more assertions or test cases failed."],
        )


verification_engine = VerificationEngine()
