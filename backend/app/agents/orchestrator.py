"""
JARVIS Central Orchestrator
Primary coordinator that determines required specialist agent,
delegates execution, enforces permissions, and aggregates verified results.
"""
from __future__ import annotations

import uuid
from typing import Any
from backend.app.agents.schema import AgentResult
from backend.app.agents.atlas import atlas_agent
from backend.app.agents.oracle import oracle_agent
from backend.app.agents.specialists import nexus_agent, athena_agent, echo_agent
from backend.app.evolution.auditor import auditor
from backend.app.core.logging_config import get_logger

logger = get_logger("agents.orchestrator")


class JarvisOrchestrator:
    """Central agent coordinator."""

    def dispatch(
        self,
        intent: str,
        parameters: dict[str, Any],
        task_id: str | None = None,
    ) -> AgentResult:
        tid = task_id or f"task_{uuid.uuid4().hex[:8]}"
        intent_lower = intent.lower()

        logger.info("Orchestrator dispatching intent '%s' (task: %s)", intent, tid)

        # 1. Research & Documentation → ORACLE
        if any(kw in intent_lower for kw in ["research", "compare sources", "find documentation", "investigate"]):
            return oracle_agent.analyze_research_topic(
                tid,
                parameters.get("topic", intent),
                parameters.get("sources"),
            )

        # 2. Business & Strategy → NEXUS
        elif any(kw in intent_lower for kw in ["business", "pricing", "market", "revenue", "strategy"]):
            return nexus_agent.evaluate_opportunity(tid, parameters.get("initiative", intent))

        # 3. Learning & Study → ATHENA
        elif any(kw in intent_lower for kw in ["study", "explain concept", "quiz", "revision"]):
            return athena_agent.formulate_study_breakdown(tid, parameters.get("concept", intent))

        # 4. External communication & Email → ECHO
        elif any(kw in intent_lower for kw in ["email", "draft", "message", "outreach"]):
            return echo_agent.draft_communication(
                tid,
                parameters.get("recipient", "Unknown"),
                parameters.get("context", intent),
            )

        # 5. Self-improvement & JDI → JDI
        elif any(kw in intent_lower for kw in ["improve yourself", "audit", "self-evolution", "jdi"]):
            findings = auditor.run_full_audit()
            return AgentResult(
                agent="JDI",
                task_id=tid,
                status="completed",
                summary="Self-audit of JARVIS completed.",
                findings=findings,
                requires_approval=False,
                evidence=[f"Audited repository. Generated {len(findings)} findings."],
            )

        # 6. Development & Code analysis → ATLAS
        elif any(kw in intent_lower for kw in ["git", "repo", "run test", "pytest", "code", "bug", "build"]):
            if "run test" in intent_lower or "pytest" in intent_lower:
                return atlas_agent.run_tests(tid)
            return atlas_agent.inspect_repository(tid, parameters.get("repo_path"))

        # Default fallback: ATLAS code/system status
        return atlas_agent.inspect_repository(tid)


jarvis_orchestrator = JarvisOrchestrator()
