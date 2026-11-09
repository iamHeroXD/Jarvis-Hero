"""
JARVIS Multi-Profile Access Control Engine
Separates Owner (Rohan), Family Member (Work), and Guest profiles.
Strictly isolates memories, private projects, credentials, and settings.
"""
from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel


class ProfileType(str, Enum):
    OWNER = "owner"
    FAMILY = "family"
    GUEST = "guest"


class ProfilePermissions(BaseModel):
    can_access_owner_memory: bool = False
    can_execute_computer_actions: bool = False
    can_modify_system_settings: bool = False
    can_access_antigravity_bridge: bool = False
    can_view_development_evolution: bool = False
    max_permission_level: int = 0  # 0 = Read only


_PROFILE_PERMISSIONS_MAP: dict[ProfileType, ProfilePermissions] = {
    ProfileType.OWNER: ProfilePermissions(
        can_access_owner_memory=True,
        can_execute_computer_actions=True,
        can_modify_system_settings=True,
        can_access_antigravity_bridge=True,
        can_view_development_evolution=True,
        max_permission_level=3,
    ),
    ProfileType.FAMILY: ProfilePermissions(
        can_access_owner_memory=False,
        can_execute_computer_actions=True,  # e.g., open approved work tools
        can_modify_system_settings=False,
        can_access_antigravity_bridge=False,
        can_view_development_evolution=False,
        max_permission_level=1,
    ),
    ProfileType.GUEST: ProfilePermissions(
        can_access_owner_memory=False,
        can_execute_computer_actions=False,
        can_modify_system_settings=False,
        can_access_antigravity_bridge=False,
        can_view_development_evolution=False,
        max_permission_level=0,
    ),
}


class ProfileManager:
    """Controls access boundaries for the active laptop user."""

    def __init__(self) -> None:
        self.active_profile: ProfileType = ProfileType.OWNER

    def switch_profile(self, target: ProfileType) -> ProfilePermissions:
        self.active_profile = target
        return _PROFILE_PERMISSIONS_MAP[target]

    def get_active_permissions(self) -> ProfilePermissions:
        return _PROFILE_PERMISSIONS_MAP[self.active_profile]

    def can_access_memory_category(self, category: str) -> bool:
        """Restricts private memory categories from Family and Guest accounts."""
        if self.active_profile == ProfileType.OWNER:
            return True
        # Family and Guest can never access personal or work memories of the owner
        return False


profile_manager = ProfileManager()
