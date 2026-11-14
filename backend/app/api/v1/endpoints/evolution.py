"""API endpoints for JARVIS Self-Evolution, JDI Codebase Auditing & Antigravity Bridge."""
from __future__ import annotations

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import require_owner, get_current_user
from backend.app.models.database_models import User
from backend.app.evolution.auditor import auditor
from backend.app.evolution.prompt_generator import prompt_generator
from backend.app.evolution.self_healing import self_healing_engine
from backend.app.integrations.antigravity.adapter import antigravity_bridge

router = APIRouter()


class SelfHealRequest(BaseModel):
    error_traceback: str | None = None
    target_file: str | None = None
    test_command: str | None = None


@router.post("/self-heal")
async def trigger_self_healing(
    data: SelfHealRequest,
    current_user: Annotated[User, Depends(require_owner)],
):
    """Diagnoses and heals an error or performs codebase syntax sweep."""
    if data.error_traceback:
        result = self_healing_engine.diagnose_and_repair(
            error_input=data.error_traceback,
            target_file=data.target_file,
            test_command=data.test_command,
        )
        return {
            "status": "completed",
            "success": result.success,
            "message": result.message,
            "file_healed": result.file_healed,
            "diff": result.diff_applied,
            "duration_ms": result.duration_ms,
        }
    else:
        results = self_healing_engine.scan_and_heal_syntax()
        return {
            "status": "completed",
            "healed_count": len(results),
            "results": [
                {
                    "file": r.file_healed,
                    "message": r.message,
                    "success": r.success,
                }
                for r in results
            ],
        }


@router.get("/self-heal/history")
async def get_healing_history(current_user: Annotated[User, Depends(get_current_user)]):
    """Retrieves history of autonomous code repairs."""
    return {"history": self_healing_engine.history}


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
