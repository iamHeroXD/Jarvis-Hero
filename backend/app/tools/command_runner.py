"""
JARVIS Safe Terminal Command Runner
Executes only allowlisted developer commands with structured arguments.
Strictly disallows raw unrestricted shell execution or administrator escalation.
"""
from __future__ import annotations

import subprocess
from typing import Any
from backend.app.core.config import PROJECT_ROOT
from backend.app.core.logging_config import get_logger

logger = get_logger("tools.terminal")

# Allowlisted binary commands
_ALLOWLISTED_BINARIES = {
    "git": ["status", "diff", "log", "branch", "checkout", "pull", "add", "commit", "--version", "-v", "version"],
    "pytest": [],  # Any test arguments
    "python": ["-m", "--version", "-c"],
    "npm": ["test", "run", "--version", "audit"],
    "cargo": ["check", "test", "--version"],
}


class CommandRunner:
    """Manages verified developer command execution."""

    def is_command_permitted(self, binary: str, args: list[str]) -> tuple[bool, str]:
        bin_clean = binary.lower().replace(".exe", "").replace(".cmd", "")
        if bin_clean not in _ALLOWLISTED_BINARIES:
            return False, f"Binary '{binary}' is not permitted in allowlisted command registry."

        allowed_subcmds = _ALLOWLISTED_BINARIES[bin_clean]
        if allowed_subcmds and args:
            first_arg = args[0].lower()
            if first_arg not in allowed_subcmds:
                return False, f"Subcommand '{first_arg}' for '{bin_clean}' is not in allowlist."

        # Scan for dangerous characters that might be passed in arguments
        for arg in args:
            if any(char in arg for char in [";", "&", "|", "`", "$", "\n", "\r"]):
                return False, f"Argument '{arg}' contains illegal chaining characters."

        return True, "Permitted"

    def run_command(
        self,
        binary: str,
        args: list[str],
        cwd: str | None = None,
        timeout_seconds: int = 45,
    ) -> dict[str, Any]:
        permitted, reason = self.is_command_permitted(binary, args)
        if not permitted:
            return {
                "success": False,
                "verified": False,
                "exit_code": -1,
                "error": reason,
            }

        work_dir = cwd or str(PROJECT_ROOT)
        cmd = [binary] + args

        try:
            res = subprocess.run(
                cmd,
                cwd=work_dir,
                shell=False,  # Enforce direct executable invocation, NO shell
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )

            is_success = (res.returncode == 0)
            return {
                "success": is_success,
                "verified": True,
                "command": " ".join(cmd),
                "exit_code": res.returncode,
                "stdout": res.stdout[:50_000],
                "stderr": res.stderr[:20_000],
                "evidence": f"Executed with exit code {res.returncode}",
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "verified": False,
                "error": f"Command timed out after {timeout_seconds} seconds.",
            }
        except Exception as exc:
            logger.error("Command execution error on %s: %s", cmd, exc)
            return {"success": False, "verified": False, "error": str(exc)}


command_runner = CommandRunner()
