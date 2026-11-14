"""
JARVIS Laptop Controller — Canonical Re-export Layer
Re-exports from unified_computer_controller for 100% backwards compatibility.
"""
from backend.app.tools.unified_computer_controller import (
    UnifiedComputerController,
    LaptopController,
    unified_controller,
    laptop_controller,
)

__all__ = [
    "UnifiedComputerController",
    "LaptopController",
    "unified_controller",
    "laptop_controller",
]
