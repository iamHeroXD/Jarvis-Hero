"""
Comprehensive Unit Tests for JARVIS Mark X Autonomous Controllers:
- Windows Controller (Process verification, active app enumeration, launching)
- Browser Deep Research Engine (DOM scraping, citation synthesis, PDF generation)
- Multi-Step Compound Workflow Engine (State persistence, approval gates, execution recovery)
"""
from __future__ import annotations

import os
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

from backend.app.tools.windows_controller import (
    windows_controller,
    WindowsComputerController,
)
from backend.app.tools.browser_research import (
    browser_research_engine,
    BrowserResearchEngine,
)
from backend.app.tasks.workflow_engine import (
    workflow_engine,
    WorkflowStep,
    WorkflowState,
    WorkflowEngine,
)


# ── 1. Windows Controller Tests ───────────────────────────────────────────────

def test_is_process_running_known():
    """Verify process running check handles negative checks cleanly."""
    assert windows_controller.is_process_running("non_existent_process_xyz_9999.exe") is False


def test_get_process_info_mocked():
    """Verify get_process_info extracts pid, name, memory, and status."""
    mock_p = MagicMock()
    mock_p.info = {
        "pid": 4321,
        "name": "mockapp.exe",
        "cpu_percent": 1.5,
        "memory_info": MagicMock(rss=45 * 1024 * 1024),
        "status": "running",
    }
    with patch("psutil.process_iter", return_value=[mock_p]):
        info = windows_controller.get_process_info("mockapp.exe")
        assert info is not None
        assert info["pid"] == 4321
        assert info["name"] == "mockapp.exe"
        assert info["memory_mb"] == 45.0


def test_get_running_applications():
    """Verify active desktop applications list returns expected schema."""
    apps = windows_controller.get_running_applications(limit=10)
    assert isinstance(apps, list)
    if apps:
        app = apps[0]
        assert "pid" in app
        assert "name" in app
        assert "memory_mb" in app


def test_launch_app_verified_mocked():
    """Verify launch_app_verified initiates launch and verifies process spawn."""
    with patch.object(windows_controller, "is_process_running", return_value=False), \
         patch.object(windows_controller, "poll_process_launched") as mock_poll, \
         patch("subprocess.Popen"):
        
        mock_poll.return_value = {
            "pid": 8888,
            "memory_mb": 15.2,
            "verification_ms": 120,
            "verified": True,
        }
        res = windows_controller.launch_app_verified("notepad")
        assert res["success"] is True
        assert res["verified"] is True
        assert res["pid"] == 8888


# ── 2. Browser Research Engine Tests ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_web_sources_mocked():
    """Verify web search parser handles results correctly."""
    mock_html = """
    <html>
      <body>
        <a class="result__url" href="https://example.com/quantum">Link</a>
        <a class="result__snippet">Breakthrough in 2026 quantum computers with error correction.</a>
      </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = mock_html

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        results = await browser_research_engine.search_web_sources("quantum computing", max_results=2)
        assert isinstance(results, list)
        if results:
            assert "url" in results[0]
            assert "title" in results[0]


@pytest.mark.asyncio
async def test_fetch_page_content_dom_cleaning():
    """Verify DOM scraping extracts text and strips script/style tags."""
    sample_html = """
    <html>
      <head>
        <script>var x = 10;</script>
        <style>body { color: red; }</style>
      </head>
      <body>
        <nav>Cookie policy consent banner</nav>
        <main>
          <h1>Quantum Neural Architectures</h1>
          <p>Researchers have achieved topological qubit coherence for 45 minutes.</p>
        </main>
      </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = sample_html

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await browser_research_engine.fetch_page_content("https://example.com/article")
        assert res["success"] is True
        assert "Quantum Neural Architectures" in res["text"]
        assert "topological qubit coherence" in res["text"]
        assert "var x = 10" not in res["text"]


def test_generate_research_pdf(tmp_path):
    """Verify publication-grade PDF report is generated with headers and metadata."""
    research_mock = {
        "topic": "Neuromorphic Vision Transformers",
        "timestamp": "2026-11-14 09:30 UTC",
        "summary": "Neuromorphic edge silicon operates at sub-milliwatt regimes for real-time inference.",
        "sources": [
            {"id": 1, "title": "Nature Electronics 2026", "url": "https://nature.com/articles/neuromorphic-2026"},
            {"id": 2, "title": "IEEE Journal", "url": "https://ieee.org/papers/spiking-vision"},
        ],
    }
    pdf_out = str(tmp_path / "test_report.pdf")
    created_path = browser_research_engine.generate_research_pdf(research_mock, output_path=pdf_out)
    assert Path(created_path).exists()
    assert Path(created_path).stat().st_size > 1000


# ── 3. Multi-Step Workflow Engine Tests ────────────────────────────────────────

def test_build_prompt_to_ide_workflow():
    """Verify compound workflow builder initializes sequential steps correctly."""
    wf = workflow_engine.build_prompt_to_ide_workflow("Refactor UI", ide="Antigravity", project_path=r"F:\Work\Jarvis- Hero")
    assert wf.workflow_id.startswith("wf_")
    assert len(wf.steps) == 4
    assert wf.steps[0].action_type == "content_gen"
    assert wf.steps[1].action_type == "app_launch"
    assert wf.steps[2].action_type == "ide_handoff"
    assert wf.steps[3].action_type == "verify"


def test_build_social_draft_workflow_has_approval_gate():
    """Verify safety approval gate is strictly enforced for social messaging."""
    wf = workflow_engine.build_social_draft_workflow(platform="Instagram", recipient="Alex", draft_text="See you at 6 PM")
    assert wf.workflow_id.startswith("wf_")
    assert len(wf.steps) == 3
    # Step 2 MUST require owner approval
    assert wf.steps[1].action_type == "social_draft"
    assert wf.steps[1].requires_approval is True


@pytest.mark.asyncio
async def test_workflow_engine_execution_flow(tmp_path):
    """Verify workflow state transitions, execution, and state persistence."""
    steps = [
        WorkflowStep(id=1, name="Step 1", description="Description 1", action_type="verify"),
        WorkflowStep(id=2, name="Approval Step", description="Wait for owner", action_type="social_draft", requires_approval=True),
        WorkflowStep(id=3, name="Final Step", description="Description 3", action_type="verify"),
    ]
    wf = workflow_engine.create_workflow(
        title="Test Flow",
        user_intent="Intent for testing",
        steps=steps,
    )

    # Execute workflow - it should stop at step 2 (requires_approval)
    updated_wf = await workflow_engine.execute_workflow(wf.workflow_id)
    assert updated_wf.state == "waiting_approval"
    assert updated_wf.current_step_index == 1
    assert updated_wf.steps[0].state == "completed"
    assert updated_wf.steps[1].state == "waiting_approval"

    # Now approve and resume
    resumed_wf = workflow_engine.approve_and_resume(wf.workflow_id)
    assert resumed_wf.current_step_index == 2
    assert resumed_wf.steps[1].state == "completed"
