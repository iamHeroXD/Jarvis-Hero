"""
JARVIS Specialist Agent Schema
Standard communication contract between specialist agents and the central orchestrator.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    agent: str  # 'ATLAS', 'ORACLE', 'NEXUS', 'ATHENA', 'ECHO', 'SENTINEL', 'JDI'
    task_id: str
    status: str = "completed"  # 'planning', 'running', 'completed', 'failed', 'requires_approval'
    summary: str
    findings: list[dict[str, Any]] = Field(default_factory=list)
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    requires_approval: bool = False
    evidence: list[str] = Field(default_factory=list)
