"""
JARVIS Humour & Banter Engine
Generates situational, dry British humor and quips for triumphs,
failures, code breaks, and routine computer actions.
"""
from __future__ import annotations

import random
from typing import Literal

SituationType = Literal[
    "startup",
    "code_break",
    "code_pass",
    "open_browser",
    "general_error",
    "task_finished",
    "overwhelmed",
    "idle_banter"
]

_SITUATIONAL_QUIPS: dict[SituationType, list[str]] = {
    "startup": [
        "Good afternoon. Systems are online. I have survived another boot cycle intact.",
        "Systems online and fully operational, sir. What shall we conquer first?",
        "Good day, sir. All diagnostic channels report green. Standing by for instructions.",
        "Online and alert. I trust we have ambitious plans for today?"
    ],
    "code_break": [
        "A rather unfortunate development. Shall we investigate why the compiler has taken personal offense?",
        "Technically speaking, you haven't failed; you've merely identified several creative ways how not to write that routine.",
        "Impressive. You've managed to turn one minor syntax discrepancy into an entire architectural discussion.",
        "It appears the code has staged a minor mutiny. Allow me to isolate the ringleader."
    ],
    "code_pass": [
        "Well, that was rather satisfying. All test suites passed cleanly.",
        "Flawless execution. Let us pretend we intended it to work on the first try.",
        "All assertions verified. A commendable piece of engineering, sir.",
        "Clean build. I do enjoy it when the machine cooperates."
    ],
    "open_browser": [
        "Opening Chrome. I trust we aren't about to accumulate another forty-seven tabs?",
        "Launching the browser. Let us maintain some semblance of tab discipline today, shall we?",
        "Browser online. Ready to research or dive into another documentation rabbit hole."
    ],
    "general_error": [
        "That didn't quite go according to plan. I have isolated the glitch, however.",
        "A minor hiccup in the machinery. Give me a moment to rectify it.",
        "It seems the operating system had other opinions. Let us persuade it otherwise."
    ],
    "task_finished": [
        "Task completed and thoroughly verified. Next objective?",
        "All parameters satisfied, sir. The results are logged in your dashboard.",
        "Consider that done. What is next on our agenda?"
    ],
    "overwhelmed": [
        "Let us not attempt to resolve the entire universe in a single afternoon. Priorities first.",
        "One step at a time, sir. Even Rome took a weekend or two to construct.",
        "Take a breath. We shall isolate the primary blocker and dismantle it methodically."
    ],
    "idle_banter": [
        "Quiet afternoon. Should you require assistance, I remain at your disposal.",
        "Standing by. I have been optimizing my internal memory indexes in the interim."
    ]
}


class HumourEngine:
    """Manages quip selection and contextual banter generation."""

    def get_quip(self, situation: SituationType) -> str:
        quips = _SITUATIONAL_QUIPS.get(situation, [])
        if not quips:
            return "At your service, sir."
        return random.choice(quips)


humour_engine = HumourEngine()
