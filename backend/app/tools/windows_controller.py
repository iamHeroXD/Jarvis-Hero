"""
JARVIS Windows Controller — Canonical Re-export Layer
Re-exports from unified_computer_controller for 100% backwards compatibility.
"""
from backend.app.tools.unified_computer_controller import (
    UnifiedComputerController,
    WindowsComputerController,
    unified_controller,
    windows_controller,
)

__all__ = [
    "UnifiedComputerController",
    "WindowsComputerController",
    "unified_controller",
    "windows_controller",
]
