"""Tasks endpoints — Phase 7 full implementation. Stubs for Phase 1."""
from fastapi import APIRouter, Depends
from typing import Annotated
from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.models.database_models import User

router = APIRouter()

@router.get("")
async def list_tasks(current_user: Annotated[User, Depends(get_current_user)]):
    return []
