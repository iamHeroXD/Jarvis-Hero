"""
JARVIS Development Intelligence (JDI) — Prompt Generator
Generates structured, production-grade Antigravity development prompts
with problem context, architecture, constraints, tests, and rollback plan.
"""
from __future__ import annotations

from typing import Any


class AntigravityPromptGenerator:
    """Produces technical implementation prompts for Google Antigravity."""

    def generate_prompt(
        self,
        feature_name: str,
        problem_statement: str,
        affected_modules: list[str],
        technical_constraints: list[str] | None = None,
        acceptance_criteria: list[str] | None = None,
        rollback_plan: str | None = None,
    ) -> str:
        constraints = technical_constraints or [
            "Maintain Windows 11 compatibility with 8 GB RAM and Intel integrated graphics.",
            "Do not introduce expensive GPU dependencies or heavy local model inference.",
            "Secrets must remain in Windows Credential Manager; no plaintext API keys.",
            "Preserve all existing comments, docstrings, and database migrations.",
        ]

        criteria = acceptance_criteria or [
            "Feature passes automated unit tests without regressions.",
            "Backend endpoints respond with verified status and proper error handling.",
            "Frontend UI components integrate seamlessly into JARVIS Mission Control.",
        ]

        rollback = rollback_plan or "Git stash or revert commit on isolated worktree branch before master release."

        prompt = f"""# ANTIGRAVITY TASK SPECIFICATION: {feature_name.upper()}

## 1. OBJECTIVE & PROBLEM STATEMENT
{problem_statement}

## 2. AFFECTED MODULES & ARCHITECTURE
"""
        for mod in affected_modules:
            prompt += f"- `{mod}`\n"

        prompt += "\n## 3. TECHNICAL CONSTRAINTS\n"
        for c in constraints:
            prompt += f"- {c}\n"

        prompt += "\n## 4. ACCEPTANCE CRITERIA\n"
        for a in criteria:
            prompt += f"- [ ] {a}\n"

        prompt += f"""
## 5. SECURITY & PERMISSIONS
- Strict Level 1/2 permissions apply; no arbitrary shell execution.
- Sensitive files require authenticated user confirmation.

## 6. VERIFICATION & ROLLBACK
- Test command: `pytest tests/` and `npm run test`
- Rollback Strategy: {rollback}
"""
        return prompt.strip()


prompt_generator = AntigravityPromptGenerator()
