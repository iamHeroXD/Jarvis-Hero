"""API endpoints for JARVIS Self-Evolution, JDI Codebase Auditing & Antigravity Bridge."""
from __future__ import annotations

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import require_owner, get_current_user
from backend.app.models.database_models import User
from backend.app.evolution.auditor import auditor
from backend.app.evolution.prompt_generator import prompt_generator
from backend.app.integrations.antigravity.adapter import antigravity_bridge

router = APIRouter()


class PromptRequest(BaseModel):
    feature_name: str
    problem_statement: str
    affected_modules: list[str]


@router.get("/audit")
async def run_codebase_audit(current_user: Annotated[User, Depends(require_owner)]):
    """Executes a real codebase self-audit."""
    findings = auditor.run_full_audit()
    return {"status": "completed", "findings": findings}


@router.post("/generate-prompt")
async def generate_antigravity_prompt(
    data: PromptRequest,
    current_user: Annotated[User, Depends(require_owner)],
):
    """Generates an Antigravity prompt for code evolution."""
    prompt = prompt_generator.generate_prompt(
        feature_name=data.feature_name,
        problem_statement=data.problem_statement,
        affected_modules=data.affected_modules,
    )
    artifact_path = antigravity_bridge.export_development_task(
        task_id="EVO-01",
        title=data.feature_name,
        prompt_content=prompt,
    )
    return {
        "status": "generated",
        "prompt": prompt,
        "artifact_file": str(artifact_path),
    }


@router.get("/bridge-status")
async def get_bridge_status(current_user: Annotated[User, Depends(get_current_user)]):
    """Reports Antigravity integration capabilities."""
    return antigravity_bridge.check_environment_capabilities()
