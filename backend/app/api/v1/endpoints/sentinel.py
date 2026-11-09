"""API endpoints for Sentinel Cybersecurity and Browser Safety Monitoring."""
from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.models.database_models import User
from backend.app.security.sentinel import sentinel_monitor

router = APIRouter()


class UrlCheckRequest(BaseModel):
    url: str


class TextCheckRequest(BaseModel):
    text: str


@router.post("/check-url")
async def check_url_safety(
    data: UrlCheckRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Evaluates a URL for phishing, typosquatting, and malicious flags."""
    assessment = sentinel_monitor.evaluate_url(data.url)
    return assessment.to_dict()


@router.post("/scan-text")
async def scan_text_threat(
    data: TextCheckRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Evaluates message/email text for scam, coercion, or prompt injection indicators."""
    assessment = sentinel_monitor.analyze_communication(data.text)
    return assessment.to_dict()
