"""
JARVIS Intelligence Evaluation Engine (JIEE)
Evaluates response quality and handles adaptive correction when the user indicates:
"That's not what I meant", "You missed the point", "No, make it better".
Performs mismatch analysis and synthesizes an upgraded, refined output.
"""
from __future__ import annotations

import re
from typing import Any
from backend.app.core.logging_config import get_logger

logger = get_logger("guidance.jiee")

CORRECTION_TRIGGERS = [
    r"not what i meant",
    r"you missed the point",
    r"this isn't good",
    r"not what i wanted",
    r"that is wrong",
    r"make it better",
    r"do it properly",
    r"i expected something better",
    r"try again differently",
]

_TRIGGER_PATTERN = re.compile("|".join(CORRECTION_TRIGGERS), re.IGNORECASE)


class MismatchAnalysis:
    def __init__(
        self,
        is_correction: bool,
        detected_issue: str | None = None,
        recommendation: str | None = None,
    ) -> None:
        self.is_correction = is_correction
        self.detected_issue = detected_issue
        self.recommendation = recommendation

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_correction": self.is_correction,
            "detected_issue": self.detected_issue,
            "recommendation": self.recommendation,
        }


class IntelligenceEvaluationEngine:
    """
    Monitors conversations for user feedback and correction patterns.
    Enables JARVIS to learn from misunderstandings and auto-pivot.
    """

    def detect_correction_intent(self, user_message: str) -> bool:
        """Determines if the user's latest input is a critical correction or dissatisfaction."""
        return bool(_TRIGGER_PATTERN.search(user_message))

    def build_mismatch_prompt(
        self,
        previous_user_input: str,
        previous_model_output: str,
        user_correction: str,
    ) -> str:
        """
        Creates an introspective prompt forcing the AI to analyze its prior mistake
        and produce a genuinely improved response without repetitive fluff.
        """
        return f"""[JIEE — INTROSPECTIVE CORRECTION REQUIRED]
The user expressed dissatisfaction with your previous output.
Original User Prompt: "{previous_user_input}"
Your Previous Response: "{previous_model_output[:300]}..." [truncated]
User Feedback/Correction: "{user_correction}"

MANDATORY INSTRUCTIONS:
1. Identify specifically where you misunderstood the intention, tone, or technical constraints.
2. Formulate a substantially better, more sophisticated, or accurately targeted response.
3. Open with a brief, intelligent acknowledgement of the specific pivot (e.g., "Understood, sir. I see where I missed the mark. Let us take the more restrained/direct approach:").
4. Provide the complete revised work directly without empty apologies or excuses.
"""


jiee = IntelligenceEvaluationEngine()
