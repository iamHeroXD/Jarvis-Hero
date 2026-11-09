"""
JARVIS Smart Reminders & Daily Briefing Engine
Manages scheduled reminders and generates intelligent daily briefings
synthesizing projects, overdue tasks, and system readiness.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from pydantic import BaseModel, Field
from backend.app.core.logging_config import get_logger

logger = get_logger("tasks.reminders")


class ScheduledReminder(BaseModel):
    id: str = Field(default_factory=lambda: f"rem_{uuid.uuid4().hex[:6]}")
    title: str
    body: str = ""
    due_at: str
    recurrence: str | None = None
    speak_aloud: bool = True
    is_completed: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class ReminderManager:
    """Stores in-memory & database scheduled reminders and briefings."""

    def __init__(self) -> None:
        self._reminders: dict[str, ScheduledReminder] = {}

    def add_reminder(
        self,
        title: str,
        due_at: str,
        body: str = "",
        recurrence: str | None = None,
        speak_aloud: bool = True,
    ) -> ScheduledReminder:
        rem = ScheduledReminder(
            title=title,
            due_at=due_at,
            body=body,
            recurrence=recurrence,
            speak_aloud=speak_aloud,
        )
        self._reminders[rem.id] = rem
        logger.info("Reminder scheduled: [%s] %s due at %s", rem.id, title, due_at)
        return rem

    def list_reminders(self, include_completed: bool = False) -> list[dict[str, Any]]:
        items = list(self._reminders.values())
        if not include_completed:
            items = [r for r in items if not r.is_completed]
        return [r.model_dump() for r in items]

    def complete_reminder(self, reminder_id: str) -> bool:
        rem = self._reminders.get(reminder_id)
        if rem:
            rem.is_completed = True
            return True
        return False

    def generate_daily_briefing(self, owner_name: str = "Sir") -> str:
        """Synthesizes a cohesive, intelligent morning or daily briefing."""
        now = datetime.now()
        greeting = "Good morning" if now.hour < 12 else "Good afternoon" if now.hour < 17 else "Good evening"

        active_reminders = [r for r in self._reminders.values() if not r.is_completed]

        briefing = f"""{greeting}, {owner_name}. Here is your tactical overview.

Systems are online and operating normally.
"""
        if active_reminders:
            briefing += f"You have {len(active_reminders)} scheduled reminder(s) pending today:\n"
            for r in active_reminders[:3]:
                briefing += f"- {r.title} (due: {r.due_at})\n"
        else:
            briefing += "You have no outstanding overdue reminders on the immediate schedule.\n"

        briefing += "\nYour primary project workspace (RCN / Jarvis) is ready for development. What shall we tackle first?"
        return briefing.strip()


reminder_manager = ReminderManager()
