"""
JARVIS Autonomous Self-Code Healing & Runtime Maintenance Engine
Allows JARVIS to:
1. Inspect runtime exceptions, tracebacks, and test failures.
2. Locate the offending codebase file and line number.
3. Formulate targeted, syntactically-valid code patches.
4. Apply the patch with automated backup and safety rollback.
5. Verify the fix using AST validation and automated test execution.
"""
from __future__ import annotations

import ast
import difflib
import os
import re
import shutil
import subprocess
import sys
import traceback
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.app.core.config import PROJECT_ROOT
from backend.app.core.logging_config import get_logger

logger = get_logger("evolution.self_healing")


@dataclass
class DiagnosticReport:
    error_type: str
    error_message: str
    file_path: Path
    line_number: int
    faulty_code: str
    traceback_snippet: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class CodePatch:
    file_path: Path
    original_snippet: str
    replacement_snippet: str
    line_number: int
    rationale: str
    backup_path: Path | None = None


@dataclass
class HealingResult:
    success: bool
    file_healed: str
    diagnosis: str
    diff_applied: str
    verification_passed: bool
    message: str
    duration_ms: float = 0.0


class SelfHealingEngine:
    """Autonomous self-diagnosis and code repair for JARVIS codebase."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or PROJECT_ROOT
        self.history: list[dict[str, Any]] = []

    def _format_path(self, path: Path) -> str:
        """Format path safely relative to root if inside root, else absolute."""
        try:
            return str(path.relative_to(self.root_dir))
        except ValueError:
            return str(path)

    def diagnose_traceback(
        self, tb_text: str, fallback_file: Path | None = None
    ) -> DiagnosticReport | None:
        """Parse an exception traceback to isolate the faulty file, line, and message."""
        lines = tb_text.strip().splitlines()
        error_type = "UnknownError"
        error_msg = "Unknown runtime error"

        # Look for last line: "ExceptionType: details"
        for line in reversed(lines):
            match = re.match(r"^([A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception)): (.*)$", line.strip())
            if match:
                error_type = match.group(1)
                error_msg = match.group(2)
                break
            elif "SyntaxError:" in line:
                error_type = "SyntaxError"
                error_msg = line.split("SyntaxError:", 1)[1].strip()
                break

        # Look for File "path", line X, in Y
        faulty_file: Path | None = None
        faulty_line = 1
        faulty_code = ""

        # Search from bottom to top for files belonging to this repository
        file_matches = re.findall(r'File "([^"]+)", line (\d+)(?:, in (\w+))?', tb_text)
        for fpath, lnum, _ in reversed(file_matches):
            p = Path(fpath)
            # Check if this file is inside project root or relative
            resolved = (self.root_dir / p) if not p.is_absolute() else p
            if resolved.exists() and not str(resolved).endswith(os.path.join("site-packages", "")):
                faulty_file = resolved
                faulty_line = int(lnum)
                break

        if not faulty_file:
            faulty_file = fallback_file or (self.root_dir / "backend" / "app" / "main.py")

        if faulty_file.exists():
            try:
                code_lines = faulty_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                if 1 <= faulty_line <= len(code_lines):
                    faulty_code = code_lines[faulty_line - 1].strip()
            except Exception:
                pass

        return DiagnosticReport(
            error_type=error_type,
            error_message=error_msg,
            file_path=faulty_file,
            line_number=faulty_line,
            faulty_code=faulty_code,
            traceback_snippet=tb_text[-1200:],
        )

    def formulate_patch(self, diagnosis: DiagnosticReport) -> CodePatch | None:
        """Formulate a corrective code patch based on AST analysis and pattern matching."""
        file_path = diagnosis.file_path
        if not file_path.exists():
            return None

        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines(keepends=True)
        idx = max(0, diagnosis.line_number - 1)
        original_line = lines[idx] if idx < len(lines) else ""

        # ── Pattern 1: Missing colon in def/if/for/while/class ──
        if diagnosis.error_type == "SyntaxError" and (
            "expected ':'" in diagnosis.error_message
            or "invalid syntax" in diagnosis.error_message
        ):
            stripped = original_line.rstrip("\r\n")
            if re.match(r"^\s*(def |class |if |elif |else|while |for |try|except|finally|with )", stripped):
                if not stripped.endswith(":"):
                    fixed_line = stripped + ":\n"
                    return CodePatch(
                        file_path=file_path,
                        original_snippet=original_line,
                        replacement_snippet=fixed_line,
                        line_number=diagnosis.line_number,
                        rationale="Appended missing colon to block declaration.",
                    )

        # ── Pattern 2: Undefined Name (NameError) due to missing default or typo ──
        if diagnosis.error_type == "NameError":
            var_match = re.search(r"name '(\w+)' is not defined", diagnosis.error_message)
            if var_match:
                missing_var = var_match.group(1)
                # Check if it's a common missing module import
                known_modules = {
                    "os": "import os\n",
                    "sys": "import sys\n",
                    "json": "import json\n",
                    "re": "import re\n",
                    "datetime": "from datetime import datetime\n",
                    "Path": "from pathlib import Path\n",
                    "Any": "from typing import Any\n",
                    "logger": "from backend.app.core.logging_config import get_logger\nlogger = get_logger('core')\n",
                }
                if missing_var in known_modules:
                    header = known_modules[missing_var]
                    return CodePatch(
                        file_path=file_path,
                        original_snippet=lines[0] if lines else "",
                        replacement_snippet=header + (lines[0] if lines else ""),
                        line_number=1,
                        rationale=f"Injected missing standard import for '{missing_var}'.",
                    )
                # Otherwise, provide a safe fallback definition before line
                indent = re.match(r"^\s*", original_line).group(0)
                safe_def = f"{indent}{missing_var} = None  # Auto-healed by JARVIS\n{original_line}"
                return CodePatch(
                    file_path=file_path,
                    original_snippet=original_line,
                    replacement_snippet=safe_def,
                    line_number=diagnosis.line_number,
                    rationale=f"Declared undefined identifier '{missing_var}' with safe default None.",
                )

        # ── Pattern 3: AttributeError / NoneType has no attribute ──
        if diagnosis.error_type == "AttributeError":
            if "NoneType" in diagnosis.error_message:
                indent = re.match(r"^\s*", original_line).group(0)
                safe_guard = f"{indent}if {diagnosis.faulty_code.split('.')[0].strip()} is not None:\n    {original_line}"
                return CodePatch(
                    file_path=file_path,
                    original_snippet=original_line,
                    replacement_snippet=safe_guard,
                    line_number=diagnosis.line_number,
                    rationale="Added NoneType safety check guard.",
                )

        # ── Pattern 4: ZeroDivisionError ──
        if diagnosis.error_type == "ZeroDivisionError":
            indent = re.match(r"^\s*", original_line).group(0)
            fixed_line = re.sub(r"/\s*(\w+)", r"/ (\1 if \1 != 0 else 1e-9)", original_line)
            return CodePatch(
                file_path=file_path,
                original_snippet=original_line,
                replacement_snippet=fixed_line,
                line_number=diagnosis.line_number,
                rationale="Added zero-division denominator protection.",
            )

        # ── Pattern 5: Missing closing parenthesis/bracket/quote ──
        if diagnosis.error_type == "SyntaxError":
            stripped = original_line.rstrip("\r\n")
            open_parens = stripped.count("(") - stripped.count(")")
            open_brackets = stripped.count("[") - stripped.count("]")
            open_braces = stripped.count("{") - stripped.count("}")

            suffix = ""
            if open_parens > 0:
                suffix += ")" * open_parens
            if open_brackets > 0:
                suffix += "]" * open_brackets
            if open_braces > 0:
                suffix += "}" * open_braces

            if suffix:
                fixed_line = stripped + suffix + "\n"
                return CodePatch(
                    file_path=file_path,
                    original_snippet=original_line,
                    replacement_snippet=fixed_line,
                    line_number=diagnosis.line_number,
                    rationale=f"Balanced unmatched delimiters by appending '{suffix}'.",
                )

        return None

    def apply_patch(self, patch: CodePatch) -> bool:
        """Apply a patch to target file with automatic .bak backup and AST safety check."""
        file_path = patch.file_path
        if not file_path.exists():
            return False

        content = file_path.read_text(encoding="utf-8", errors="ignore")
        if patch.original_snippet not in content:
            # Fallback to line-based replacement
            lines = content.splitlines(keepends=True)
            idx = patch.line_number - 1
            if 0 <= idx < len(lines):
                lines[idx] = patch.replacement_snippet
                new_content = "".join(lines)
            else:
                return False
        else:
            new_content = content.replace(patch.original_snippet, patch.replacement_snippet, 1)

        # Guarantee syntax validity before saving
        if file_path.suffix == ".py":
            try:
                ast.parse(new_content)
            except SyntaxError as e:
                logger.error("Patch rejected due to syntax invalidity: %s", e)
                return False

        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        shutil.copy2(file_path, backup_path)
        patch.backup_path = backup_path

        # Write modified content
        file_path.write_text(new_content, encoding="utf-8")
        logger.info("Applied code patch to %s at line %d", file_path.name, patch.line_number)
        return True

    def rollback(self, patch: CodePatch) -> None:
        """Roll back to safety backup if verification fails."""
        if patch.backup_path and patch.backup_path.exists():
            shutil.copy2(patch.backup_path, patch.file_path)
            patch.backup_path.unlink(missing_ok=True)
            logger.warning("Rolled back patch on %s", patch.file_path.name)

    def verify_patch(self, patch: CodePatch, test_command: str | None = None) -> bool:
        """Verify the patched code compiles and optionally passes pytest."""
        # 1. AST compilation check
        if patch.file_path.suffix == ".py":
            try:
                content = patch.file_path.read_text(encoding="utf-8")
                compile(content, str(patch.file_path), "exec")
            except Exception as e:
                logger.error("Verification compile error: %s", e)
                return False

        # 2. Test command execution if provided
        if test_command:
            try:
                env = os.environ.copy()
                env["PYTHONPATH"] = str(self.root_dir)
                res = subprocess.run(
                    test_command,
                    shell=True,
                    cwd=str(self.root_dir),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                if res.returncode != 0:
                    logger.error("Verification test failed: %s", res.stderr[:300])
                    return False
            except Exception as err:
                logger.error("Verification test execution exception: %s", err)
                return False

        # Clean up backup on verified success
        if patch.backup_path and patch.backup_path.exists():
            patch.backup_path.unlink(missing_ok=True)

        return True

    def diagnose_and_repair(
        self,
        error_input: str | Exception,
        target_file: Path | None = None,
        test_command: str | None = None,
    ) -> HealingResult:
        """End-to-end autonomous healing: diagnose -> patch -> apply -> verify."""
        import time
        start_time = time.perf_counter()

        tb_text = (
            "".join(traceback.format_exception(type(error_input), error_input, error_input.__traceback__))
            if isinstance(error_input, Exception)
            else str(error_input)
        )

        diagnosis = self.diagnose_traceback(tb_text, fallback_file=target_file)
        if not diagnosis:
            return HealingResult(
                success=False,
                file_healed="",
                diagnosis="Failed to isolate error context from traceback.",
                diff_applied="",
                verification_passed=False,
                message="Unable to isolate error context.",
            )

        patch = self.formulate_patch(diagnosis)
        if not patch:
            return HealingResult(
                success=False,
                file_healed=self._format_path(diagnosis.file_path),
                diagnosis=f"{diagnosis.error_type}: {diagnosis.error_message}",
                diff_applied="",
                verification_passed=False,
                message=f"No safe autonomous patch pattern matched for {diagnosis.error_type} on line {diagnosis.line_number}.",
            )

        diff = "".join(
            difflib.unified_diff(
                patch.original_snippet.splitlines(keepends=True),
                patch.replacement_snippet.splitlines(keepends=True),
                fromfile="original",
                tofile="patched",
            )
        )

        applied = self.apply_patch(patch)
        if not applied:
            return HealingResult(
                success=False,
                file_healed=self._format_path(diagnosis.file_path),
                diagnosis=f"{diagnosis.error_type}: {diagnosis.error_message}",
                diff_applied="",
                verification_passed=False,
                message="Patch application failed AST syntax validation check.",
            )

        verified = self.verify_patch(patch, test_command=test_command)
        if not verified:
            self.rollback(patch)
            return HealingResult(
                success=False,
                file_healed=self._format_path(diagnosis.file_path),
                diagnosis=f"{diagnosis.error_type}: {diagnosis.error_message}",
                diff_applied=diff,
                verification_passed=False,
                message="Patch was rolled back because verification tests failed.",
            )

        duration = (time.perf_counter() - start_time) * 1000

        res = HealingResult(
            success=True,
            file_healed=self._format_path(diagnosis.file_path),
            diagnosis=f"{diagnosis.error_type}: {diagnosis.error_message}",
            diff_applied=diff,
            verification_passed=True,
            message=f"Successfully repaired {diagnosis.file_path.name} at line {diagnosis.line_number}: {patch.rationale}",
            duration_ms=round(duration, 2),
        )

        self.history.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "file": res.file_healed,
            "diagnosis": res.diagnosis,
            "rationale": patch.rationale,
            "duration_ms": res.duration_ms,
        })

        return res

    def scan_and_heal_syntax(self) -> list[HealingResult]:
        """Scans backend python files for syntax defects and autonomously heals them."""
        results: list[HealingResult] = []
        backend_dir = self.root_dir / "backend" / "app"
        if not backend_dir.exists():
            return results

        for py_path in backend_dir.rglob("*.py"):
            try:
                content = py_path.read_text(encoding="utf-8")
                ast.parse(content, filename=str(py_path))
            except SyntaxError as e:
                logger.warning("Detected syntax flaw in %s: %s", py_path.name, e)
                diag = DiagnosticReport(
                    error_type="SyntaxError",
                    error_message=str(e),
                    file_path=py_path,
                    line_number=e.lineno or 1,
                    faulty_code=e.text.strip() if e.text else "",
                    traceback_snippet=traceback.format_exc(),
                )
                patch = self.formulate_patch(diag)
                if patch and self.apply_patch(patch):
                    if self.verify_patch(patch):
                        results.append(
                            HealingResult(
                                success=True,
                                file_healed=self._format_path(py_path),
                                diagnosis=f"SyntaxError: {e}",
                                diff_applied=patch.rationale,
                                verification_passed=True,
                                message=f"Autonomously healed syntax in {py_path.name}",
                            )
                        )
                    else:
                        self.rollback(patch)

        return results


self_healing_engine = SelfHealingEngine()
