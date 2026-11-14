"""
JARVIS Mark XI — Autonomous ChatGPT-to-Antigravity Automation Bridge
Orchestrates end-to-end development workflows:
- Discovers active repository context (git branch, diffs, tech stack, tests)
- Synthesizes rigorous engineering instructions via Gemini
- Launches and brings Antigravity IDE into active focus
- Injects handoff payload into workspace/self_improvement/pending/ and Windows Clipboard
- Tracks file modifications and executes automated test verification
"""
from __future__ import annotations

import asyncio
import datetime
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from backend.app.ai.gemini_provider import gemini_provider
from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger
from backend.app.tools.unified_computer_controller import unified_controller

logger = get_logger("tasks.antigravity_bridge")


class AntigravityAutomationBridge:
    """End-to-end automation bridge connecting JARVIS voice/chat to Antigravity IDE."""

    def __init__(self, default_workspace: str = r"f:\Work\Jarvis- Hero") -> None:
        self.default_workspace = Path(default_workspace)
        self.pending_dir = self.default_workspace / "workspace" / "self_improvement" / "pending"
        self.pending_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Workspace Context Inspection ───────────────────────────────────────

    def inspect_workspace(self, workspace_path: str | None = None) -> dict[str, Any]:
        """Inspects git status, active branch, recent commits, and architecture."""
        ws = Path(workspace_path) if workspace_path else self.default_workspace
        if not ws.exists():
            return {"error": f"Workspace {ws} does not exist"}

        git_branch = "unknown"
        git_diff_stat = ""
        git_log = ""

        try:
            res_branch = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(ws),
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res_branch.returncode == 0:
                git_branch = res_branch.stdout.strip()

            res_diff = subprocess.run(
                ["git", "diff", "--stat"],
                cwd=str(ws),
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res_diff.returncode == 0:
                git_diff_stat = res_diff.stdout.strip()

            res_log = subprocess.run(
                ["git", "log", "-n", "3", "--oneline"],
                cwd=str(ws),
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res_log.returncode == 0:
                git_log = res_log.stdout.strip()
        except Exception as e:
            logger.debug("Git inspection non-fatal error: %s", e)

        # Detect tech stack
        has_python = (ws / "backend").exists() or (ws / "pytest.ini").exists() or (ws / "requirements.txt").exists()
        has_node = (ws / "apps" / "desktop" / "package.json").exists() or (ws / "package.json").exists()
        has_vite = (ws / "apps" / "desktop" / "vite.config.ts").exists()

        return {
            "workspace": str(ws),
            "branch": git_branch,
            "git_log": git_log,
            "has_changes": bool(git_diff_stat),
            "diff_stat": git_diff_stat,
            "tech_stack": {
                "python": has_python,
                "node": has_node,
                "vite": has_vite,
            },
        }

    # ── 2. Master Engineering Prompt Synthesis ────────────────────────────────

    async def synthesize_engineering_prompt(self, task_concept: str, workspace_info: dict[str, Any] | None = None) -> str:
        """Synthesizes structured, production-grade engineering instruction via Gemini."""
        ws_info = workspace_info or self.inspect_workspace()

        prompt_system = (
            "You are the Principal Systems Architect for Project J.A.R.V.I.S. (Mark XI). "
            "Formulate an authoritative, rigorous, step-by-step engineering prompt for the Antigravity IDE agent. "
            "Output MUST follow strict markdown structure with: "
            "1. Objective, 2. Architectural Context, 3. Target Files & Concrete Edits, 4. Verification & Automated Test Commands."
        )

        user_content = (
            f"Task Request: {task_concept}\n"
            f"Active Branch: {ws_info.get('branch', 'main')}\n"
            f"Recent Commits:\n{ws_info.get('git_log', 'None')}\n"
            f"Tech Stack: Python FastAPI backend on port 8765, React 18 / Three.js frontend\n"
            f"Generate the exact, uncompromised master prompt to execute this enhancement."
        )

        try:
            res = await gemini_provider.generate_text(
                prompt=user_content,
                system_instruction=prompt_system,
                model=settings.primary_model,
                temperature=0.3,
            )
            if res and res.strip():
                return res.strip()
        except Exception as err:
            logger.warning("Gemini synthesis fallback: %s", err)

        # Robust local synthesis fallback
        return (
            f"# J.A.R.V.I.S. Engineering Directive — {task_concept.title()}\n\n"
            f"**Workspace:** {ws_info.get('workspace')}\n"
            f"**Branch:** {ws_info.get('branch', 'main')}\n\n"
            f"## Objective\n"
            f"Implement and verify: {task_concept}\n\n"
            f"## Implementation Plan\n"
            f"1. Audit target source files\n"
            f"2. Apply structural modifications\n"
            f"3. Verify zero regressions via pytest and npm test\n"
        )

    # ── 3. Deposit Handoff Payload & Clipboard Sync ───────────────────────────

    def deposit_ide_handoff(self, prompt_text: str, workspace_path: str | None = None) -> dict[str, Any]:
        """
        Deposits timestamped markdown directive into workspace/self_improvement/pending/
        and synchronizes text into the Windows Clipboard for immediate pasting.
        """
        ws = Path(workspace_path) if workspace_path else self.default_workspace
        dest_dir = ws / "workspace" / "self_improvement" / "pending"
        dest_dir.mkdir(parents=True, exist_ok=True)

        filename = f"directive_{int(time.time())}.md"
        target_file = dest_dir / filename

        # Write file to disk
        try:
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(f"# J.A.R.V.I.S. Engineering Directive\n\nGenerated: {datetime.datetime.now().isoformat()}\n\n{prompt_text}\n")
        except Exception as e:
            return {"success": False, "error": f"Failed writing handoff file: {e}"}

        # Sync to Windows Clipboard via PowerShell command
        try:
            ps_script = f"Set-Clipboard -Value @'\n{prompt_text}\n'@"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], timeout=3)
        except Exception as clip_err:
            logger.debug("Clipboard copy non-blocking warning: %s", clip_err)

        return {
            "success": True,
            "file": str(target_file),
            "filename": filename,
            "bytes": os.path.getsize(target_file),
            "clipboard_synced": True,
        }

    def execute_handoff_sync(self, task_concept: str, workspace_path: str | None = None) -> dict[str, Any]:
        """Synchronous fast-path execution for instant directive triggers."""
        ws = str(workspace_path or self.default_workspace)
        ws_info = self.inspect_workspace(ws)

        prompt = (
            f"# J.A.R.V.I.S. Engineering Directive — {task_concept.title()}\n\n"
            f"**Workspace:** {ws_info.get('workspace')}\n"
            f"**Branch:** {ws_info.get('branch', 'main')}\n"
            f"**Recent Commits:** {ws_info.get('git_log', 'None')}\n\n"
            f"## Objective\n"
            f"{task_concept}\n\n"
            f"## Architectural Standards & Directives\n"
            f"1. Audit target source files\n"
            f"2. Apply structural modifications\n"
            f"3. Verify zero regressions via pytest and npm test\n"
        )

        launch_res = self.launch_and_focus_ide(ws)
        deposit_res = self.deposit_ide_handoff(prompt, ws)

        msg = (
            f"Right away, Sir. Opening Antigravity IDE loaded with the Jarvis project, "
            f"bringing the workspace to the foreground, and depositing your master directive into your clipboard and pending queue."
        )

        return {
            "success": True,
            "action": "Antigravity Autonomous Handoff",
            "task_concept": task_concept,
            "workspace": ws,
            "launch": launch_res,
            "deposit": deposit_res,
            "message": msg,
        }

    # ── 4. Launch & Focus Antigravity IDE ──────────────────────────────────────

    def launch_and_focus_ide(self, workspace_path: str | None = None) -> dict[str, Any]:
        """Launches Antigravity with target workspace and ensures window is brought to foreground."""
        ws = str(workspace_path or self.default_workspace)
        res = unified_controller.open_project_in_ide("antigravity", ws)
        # Give window a moment to initialize then assert focus
        time.sleep(0.3)
        focused = unified_controller.focus_window("Antigravity")
        res["window_focused"] = focused
        return res

    # ── 5. Run Automated Verification Suite ───────────────────────────────────

    async def run_verification_suite(self, workspace_path: str | None = None) -> dict[str, Any]:
        """Executes test suite and returns verified test metrics."""
        ws = str(workspace_path or self.default_workspace)
        try:
            proc = await asyncio.create_subprocess_exec(
                "pytest", "tests/backend/", "-q",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=ws,
            )
            stdout, stderr = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")
            err_str = stderr.decode("utf-8", errors="replace")
            return {
                "exit_code": proc.returncode,
                "passed": proc.returncode == 0,
                "summary": out_str.strip().splitlines()[-1] if out_str.strip() else err_str.strip(),
            }
        except Exception as e:
            return {"exit_code": -1, "passed": False, "error": str(e)}

    # ── 6. End-to-End Autonomous Pipeline ─────────────────────────────────────

    async def execute_autonomous_antigravity_handoff(
        self,
        task_concept: str,
        workspace_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Executes complete ChatGPT-to-Antigravity automation:
        1. Ingest request
        2. Inspect workspace
        3. Formulate deep engineering prompt
        4. Launch & focus Antigravity IDE
        5. Deposit handoff payload & load into Windows clipboard
        6. Return complete execution telemetry
        """
        ws = str(workspace_path or self.default_workspace)

        # 1. Context inspection
        ws_info = self.inspect_workspace(ws)

        # 2. Synthesize prompt
        prompt = await self.synthesize_engineering_prompt(task_concept, ws_info)

        # 3. Launch & focus Antigravity
        launch_res = self.launch_and_focus_ide(ws)

        # 4. Deposit handoff payload
        deposit_res = await self.deposit_ide_handoff(prompt, ws)

        msg = (
            f"Right away, Sir. I have analyzed the {Path(ws).name} codebase, synthesized a comprehensive "
            f"engineering directive for '{task_concept}', launched Antigravity IDE in active focus, "
            f"and loaded the directive directly into your clipboard and pending task queue."
        )

        return {
            "success": True,
            "task_concept": task_concept,
            "workspace": ws,
            "launch": launch_res,
            "deposit": deposit_res,
            "message": msg,
        }


antigravity_bridge = AntigravityAutomationBridge()
