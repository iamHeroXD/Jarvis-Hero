"""
JARVIS Central Tool Registry & Laptop Controller Integration
Registers callable actions with explicit permission levels (0-4),
supporting both developer tools and native Windows laptop controller tools.
"""
from __future__ import annotations

from typing import Any
from backend.app.security.auth import PermissionLevel
from backend.app.tools.laptop_controller import laptop_controller
from backend.app.tools.registry import (
    ToolRegistry as BaseToolRegistry,
    RegisteredTool,
    ToolExecutionRequest,
    tool_registry as base_tool_registry,
)


class ToolRegistry(BaseToolRegistry):
    """Central registry including laptop control tools."""

    def __init__(self) -> None:
        super().__init__()
        self._register_laptop_tools()

    def _register_laptop_tools(self) -> None:
        laptop_tools = {
            "get_battery_status": RegisteredTool(
                tool_id="get_battery_status",
                name="Get Battery Status",
                description="Retrieves real-time laptop battery percentage and charging telemetry.",
                permission_level=PermissionLevel.READ_ONLY,
                requires_approval=False,
                category="telemetry",
            ),
            "get_system_diagnostics": RegisteredTool(
                tool_id="get_system_diagnostics",
                name="Get System Diagnostics",
                description="Retrieves CPU, RAM, disk, and battery hardware telemetry.",
                permission_level=PermissionLevel.READ_ONLY,
                requires_approval=False,
                category="telemetry",
            ),
            "set_volume": RegisteredTool(
                tool_id="set_volume",
                name="Set Master Volume",
                description="Adjusts master system audio volume (up, down, mute, unmute).",
                permission_level=PermissionLevel.REVERSIBLE_LOCAL,
                requires_approval=False,
                category="system",
            ),
            "launch_app": RegisteredTool(
                tool_id="launch_app",
                name="Launch Laptop Application",
                description="Launches an installed Windows application or Start Menu shortcut by name.",
                permission_level=PermissionLevel.REVERSIBLE_LOCAL,
                requires_approval=False,
                category="system",
            ),
            "organize_downloads": RegisteredTool(
                tool_id="organize_downloads",
                name="Organize Downloads Folder",
                description="Categorizes and organizes files in the user Downloads folder by extension.",
                permission_level=PermissionLevel.CONFIRMED_MODIFY,
                requires_approval=True,
                category="file",
            ),
            "execute_directive": RegisteredTool(
                tool_id="execute_directive",
                name="Execute Laptop Directive",
                description="Executes a natural language directive for instant local laptop control.",
                permission_level=PermissionLevel.REVERSIBLE_LOCAL,
                requires_approval=False,
                category="system",
            ),
        }
        self._tools.update(laptop_tools)

    def execute_tool(self, req: ToolExecutionRequest) -> dict[str, Any]:
        tool = self._tools.get(req.tool_id)
        if not tool:
            return {"success": False, "verified": False, "error": f"Tool '{req.tool_id}' not found."}

        # 1. Profile permission boundary check
        from backend.app.security.profiles import profile_manager
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

        # 3. Route to laptop controller functions
        args = req.arguments
        if req.tool_id == "get_battery_status":
            return laptop_controller.get_battery_status()
        elif req.tool_id == "get_system_diagnostics":
            return laptop_controller.get_system_diagnostics()
        elif req.tool_id in ("set_volume", "adjust_volume"):
            action = args.get("action") or args.get("volume") or "up"
            return laptop_controller.adjust_volume(action)
        elif req.tool_id == "launch_app":
            app_name = args.get("app_name") or args.get("app") or args.get("name", "")
            return laptop_controller.launch_app(app_name)
        elif req.tool_id == "organize_downloads":
            return laptop_controller.organize_downloads()
        elif req.tool_id == "execute_directive":
            directive = args.get("directive") or args.get("text") or args.get("prompt", "")
            res = laptop_controller.execute_directive(directive)
            if res is None:
                return {"success": False, "message": "Directive requires deep AI reasoning, not a local command."}
            return res

        # Fallback to base developer tools
        return super().execute_tool(req)


# Exported instances and classes
tool_registry = ToolRegistry()

# Synchronize with base_tool_registry singleton
base_tool_registry._tools.update(tool_registry._tools)
_orig_base_execute = base_tool_registry.execute_tool


def _sync_execute_tool(req: ToolExecutionRequest) -> dict[str, Any]:
    if req.tool_id in tool_registry._tools and req.tool_id not in (
        "launch_application", "list_files", "read_file", "create_file", "run_developer_command", "scan_url_safety"
    ):
        return tool_registry.execute_tool(req)
    return _orig_base_execute(req)


base_tool_registry.execute_tool = _sync_execute_tool
