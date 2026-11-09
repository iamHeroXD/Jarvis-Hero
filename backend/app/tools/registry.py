"""
JARVIS Central Tool Registry & Permission Engine
Maps all callable actions to explicit permission levels (0–4)
and enforces owner approval requirements for consequential operations.
"""
from __future__ import annotations

from typing import Any, Callable
from pydantic import BaseModel
from backend.app.security.auth import PermissionLevel
from backend.app.security.profiles import profile_manager
from backend.app.tools.app_launcher import app_launcher
from backend.app.tools.file_ops import file_ops
from backend.app.tools.command_runner import command_runner
from backend.app.security.sentinel import sentinel_monitor
from backend.app.core.logging_config import get_logger

logger = get_logger("tools.registry")


class RegisteredTool(BaseModel):
    tool_id: str
    name: str
    description: str
    permission_level: int
    requires_approval: bool
    category: str


class ToolExecutionRequest(BaseModel):
    tool_id: str
    arguments: dict[str, Any]
    approval_granted: bool = False


class ToolRegistry:
    """Central registry and policy enforcement engine for all computer control tools."""

    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {
            "launch_application": RegisteredTool(
                tool_id="launch_application",
                name="Launch Approved Application",
                description="Launches an approved desktop application (VS Code, Chrome, Terminal, Antigravity).",
                permission_level=PermissionLevel.REVERSIBLE_LOCAL,
                requires_approval=False,
                category="system",
            ),
            "list_files": RegisteredTool(
                tool_id="list_files",
                name="List Workspace Files",
                description="Lists files in an approved workspace directory.",
                permission_level=PermissionLevel.READ_ONLY,
                requires_approval=False,
                category="file",
            ),
            "read_file": RegisteredTool(
                tool_id="read_file",
                name="Read File Content",
                description="Reads content of a file located within an approved directory.",
                permission_level=PermissionLevel.READ_ONLY,
                requires_approval=False,
                category="file",
            ),
            "create_file": RegisteredTool(
                tool_id="create_file",
                name="Create or Update File",
                description="Creates or modifies a file in an approved directory with pre-write backup.",
                permission_level=PermissionLevel.CONFIRMED_MODIFY,
                requires_approval=True,  # Level 2 modification
                category="file",
            ),
            "run_developer_command": RegisteredTool(
                tool_id="run_developer_command",
                name="Run Developer Command",
                description="Executes allowlisted git, test, or build commands with structured arguments.",
                permission_level=PermissionLevel.CONFIRMED_MODIFY,
                requires_approval=True,
                category="terminal",
            ),
            "scan_url_safety": RegisteredTool(
                tool_id="scan_url_safety",
                name="Scan URL Safety",
                description="Heuristic scan of a destination URL for phishing and spoofing.",
                permission_level=PermissionLevel.READ_ONLY,
                requires_approval=False,
                category="security",
            ),
        }

    def list_tools(self) -> list[dict[str, Any]]:
        return [t.model_dump() for t in self._tools.values()]

    def get_tool(self, tool_id: str) -> RegisteredTool | None:
        return self._tools.get(tool_id)

    def execute_tool(self, req: ToolExecutionRequest) -> dict[str, Any]:
        tool = self._tools.get(req.tool_id)
        if not tool:
            return {"success": False, "verified": False, "error": f"Tool '{req.tool_id}' not found."}

        # 1. Profile permission boundary check
        perms = profile_manager.get_active_permissions()
        if tool.permission_level > perms.max_permission_level:
            return {
                "success": False,
                "verified": False,
                "error": f"Active profile '{profile_manager.active_profile.value}' has max permission level {perms.max_permission_level}, but tool requires level {tool.permission_level}.",
            }

        # 2. Human approval requirement check
        if tool.requires_approval and not req.approval_granted:
            return {
                "success": False,
                "verified": False,
                "requires_approval": True,
                "approval_reason": f"Tool '{tool.name}' requires explicit owner approval for modifications.",
                "pending_arguments": req.arguments,
            }

        # 3. Route to execution implementation
        args = req.arguments
        if req.tool_id == "launch_application":
            return app_launcher.launch(
                app_id=args.get("app_id", ""),
                extra_args=args.get("extra_args"),
            )
        elif req.tool_id == "list_files":
            return file_ops.list_files(
                directory=args.get("directory", ""),
                max_items=args.get("max_items", 100),
            )
        elif req.tool_id == "read_file":
            return file_ops.read_file(
                file_path=args.get("file_path", ""),
                max_bytes=args.get("max_bytes", 100_000),
            )
        elif req.tool_id == "create_file":
            return file_ops.create_or_update_file(
                file_path=args.get("file_path", ""),
                content=args.get("content", ""),
            )
        elif req.tool_id == "run_developer_command":
            return command_runner.run_command(
                binary=args.get("binary", ""),
                args=args.get("args", []),
                cwd=args.get("cwd"),
            )
        elif req.tool_id == "scan_url_safety":
            assessment = sentinel_monitor.evaluate_url(args.get("url", ""))
            return assessment.to_dict()

        return {"success": False, "verified": False, "error": "Execution dispatcher missing."}


tool_registry = ToolRegistry()
