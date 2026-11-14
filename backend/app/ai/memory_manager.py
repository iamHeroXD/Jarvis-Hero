"""
JARVIS Layered Memory Manager (Mark IX)
Extracts semantic, episodic, and preference memories from user interactions,
indexes them in SQLite FTS5, and retrieves relevant context for prompt augmentation.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, UTC
from typing import Any
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.database_models import Memory, User
from backend.app.core.logging_config import get_logger

logger = get_logger("ai.memory_manager")

# Fast heuristic triggers for memory extraction
MEMORY_TRIGGERS = [
    r"\b(?:my name is|i am|call me)\s+([a-zA-Z\s]+)",
    r"\b(?:i prefer|i like|i love|my favorite|i always use)\s+([^\.\n]+)",
    r"\b(?:remember that|note that|keep in mind that|don't forget that)\s+([^\.\n]+)",
    r"\b(?:i'm working on|i am working on|my project is|i develop)\s+([^\.\n]+)",
    r"\b(?:i have|my laptop has|my system has|my specs are)\s+([^\.\n]+)",
]


class MemoryManager:
    """Manages long-term semantic and episodic memory for JARVIS."""

    async def extract_and_store_memories(
        self,
        user_id: int,
        message: str,
        conversation_id: int | None,
        db: AsyncSession,
    ) -> list[Memory]:
        """
        Scans user message for memorable facts, preferences, and project updates.
        Stores newly identified memories in the SQLite database.
        """
        text_clean = message.strip()
        if len(text_clean) < 8 or len(text_clean) > 800:
            return []

        stored_memories: list[Memory] = []
        lower = text_clean.lower()

        # Heuristic rules
        facts: list[tuple[str, str, str]] = []  # (category, title, content)

        # 1. Identity / User name
        m_name = re.search(r"\b(?:my name is|i am|call me)\s+([A-Z][a-z]+)\b", text_clean)
        if m_name and not any(w in lower for w in ["feeling", "doing", "just", "sorry", "tired"]):
            facts.append(("personal", "User Identity", f"User's name is {m_name.group(1)}."))

        # 2. Preferences
        m_pref = re.search(r"\b(?:i prefer|my favorite is|i really like)\s+([^,.;!?]+)", text_clean, re.I)
        if m_pref:
            detail = m_pref.group(1).strip()
            if len(detail) > 3 and not any(w in detail.lower() for w in ["that", "it", "to", "this"]):
                facts.append(("preference", f"Preference: {detail[:40]}", f"User stated preference: {detail}."))

        # 3. Explicit Memory Directives
        m_rem = re.search(r"\b(?:remember that|don't forget that|keep in mind)\s+([^.;!?]+)", text_clean, re.I)
        if m_rem:
            detail = m_rem.group(1).strip()
            if len(detail) > 4:
                facts.append(("conversation", f"Directive: {detail[:40]}", detail))

        # 4. Project context
        m_proj = re.search(r"\b(?:i am working on|i'm working on|developing|my project)\s+([^,.;!?]+)", text_clean, re.I)
        if m_proj:
            detail = m_proj.group(1).strip()
            if len(detail) > 3:
                facts.append(("project", f"Project: {detail[:40]}", f"User is developing/working on {detail}."))

        # 5. Hardware / Environment
        m_hw = re.search(r"\b(?:my laptop|my computer|my pc|my system)\s+(?:has|runs|is)\s+([^,.;!?]+)", text_clean, re.I)
        if m_hw:
            detail = m_hw.group(1).strip()
            if len(detail) > 3:
                facts.append(("technical", "System Environment", f"User system configuration: {detail}."))

        # Insert extracted facts if not already present
        for cat, title, content in facts:
            # Check for existing duplicate
            existing = await db.execute(
                select(Memory).where(
                    Memory.user_id == user_id,
                    Memory.title == title,
                )
            )
            if existing.scalars().first():
                continue

            mem = Memory(
                user_id=user_id,
                category=cat,
                title=title,
                content=content,
                source_type="conversation",
                source_ref=str(conversation_id) if conversation_id else None,
                tags=json.dumps([cat, "auto-extracted"]),
                is_verified=True,
            )
            db.add(mem)
            stored_memories.append(mem)
            logger.info("Auto-extracted memory: '%s' [%s]", title, cat)

        if stored_memories:
            await db.flush()

        return stored_memories

    async def retrieve_relevant_memories(
        self,
        user_id: int,
        query: str,
        db: AsyncSession,
        limit: int = 5,
    ) -> list[Memory]:
        """
        Retrieves relevant long-term memories using full-text search (FTS5)
        and priority recency weighting.
        """
        clean_words = [w for w in re.findall(r"[a-zA-Z0-9]+", query) if len(w) > 3]
        if not clean_words:
            # Return pinned or recent memories
            res = await db.execute(
                select(Memory)
                .where(Memory.user_id == user_id)
                .order_by(Memory.is_pinned.desc(), Memory.updated_at.desc())
                .limit(limit)
            )
            return list(res.scalars().all())

        fts_query = " OR ".join(clean_words[:6])
        try:
            # FTS5 ranked query
            res = await db.execute(
                text("""
                    SELECT m.id FROM memories m
                    JOIN memories_fts f ON m.id = f.rowid
                    WHERE memories_fts MATCH :query
                    AND m.user_id = :user_id
                    ORDER BY rank
                    LIMIT :limit
                """),
                {"query": fts_query, "user_id": user_id, "limit": limit},
            )
            mem_ids = [row[0] for row in res.fetchall()]
            if mem_ids:
                stmt = select(Memory).where(Memory.id.in_(mem_ids))
                items = (await db.execute(stmt)).scalars().all()
                return list(items)
        except Exception as e:
            logger.debug("FTS5 match error (falling back to simple query): %s", e)

        # Fallback query
        res = await db.execute(
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.is_pinned.desc(), Memory.updated_at.desc())
            .limit(limit)
        )
        return list(res.scalars().all())

    def format_memories_for_prompt(self, memories: list[Memory]) -> str:
        """Formats retrieved memories into concise system instruction block."""
        if not memories:
            return ""

        lines = ["\n[LONG-TERM MEMORY & CONTEXT OF OWNER ROHAN]:"]
        for m in memories:
            lines.append(f"- [{m.category.upper()}]: {m.content}")
        lines.append("Use this context naturally without explicitly reciting that you pulled it from memory.\n")
        return "\n".join(lines)


memory_manager = MemoryManager()
