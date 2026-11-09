"""
JARVIS Database Models — SQLAlchemy ORM
All tables in one place for Phase 1. Migrations via Alembic.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ── Users ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    preferences: Mapped[list["UserPreference"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    memories: Mapped[list["Memory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    user: Mapped["User"] = relationship(back_populates="preferences")

    __table_args__ = (UniqueConstraint("user_id", "key"),)


# ── Conversations ─────────────────────────────────────────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False, default="New conversation")
    mode: Mapped[str] = mapped_column(String(32), nullable=False, default="casual")
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_provider: Mapped[str] = mapped_column(String(32), nullable=False, default="gemini")
    model_name: Mapped[str] = mapped_column(String(64), nullable=False, default="gemini-3.8-flash")
    # Server-side interaction ID for stateful continuation
    last_interaction_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # 'user' | 'assistant' | 'system' | 'tool'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tool_calls: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    is_error: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


# ── Memory ────────────────────────────────────────────────────────────────────

class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    # Categories: personal | project | work | conversation | technical | preference | learning
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="conversation")
    source_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)  # e.g. conversation_id
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON array
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    user: Mapped["User"] = relationship(back_populates="memories")

    __table_args__ = (
        Index("ix_memories_category_user", "category", "user_id"),
    )


# ── Projects ──────────────────────────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    # active | paused | completed | archived
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    repository_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    goals: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON
    tags: Mapped[str] = mapped_column(Text, nullable=False, default="[]")   # JSON
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    notes: Mapped[list["ProjectNote"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectNote(Base):
    __tablename__ = "project_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[str] = mapped_column(String(32), nullable=False, default="note")
    # note | decision | blocker | milestone
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    project: Mapped["Project"] = relationship(back_populates="notes")


# ── Tasks ─────────────────────────────────────────────────────────────────────

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    task_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created", index=True)
    # created | planning | awaiting_approval | running | verifying | completed | failed | needs_attention | cancelled
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="normal")
    assigned_agent: Mapped[str | None] = mapped_column(String(32), nullable=True)
    permission_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    plan: Mapped[str] = mapped_column(Text, nullable=False, default="")
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON
    errors: Mapped[str] = mapped_column(Text, nullable=False, default="[]")    # JSON
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    user: Mapped["User"] = relationship(back_populates="tasks")
    project: Mapped["Project | None"] = relationship(back_populates="tasks")
    events: Mapped[list["TaskEvent"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class TaskEvent(Base):
    __tablename__ = "task_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # state_change | log | error | approval | verification
    from_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    task: Mapped["Task"] = relationship(back_populates="events")


# ── Reminders ─────────────────────────────────────────────────────────────────

class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    recurrence: Mapped[str | None] = mapped_column(String(64), nullable=True)  # cron-style or 'daily', 'weekly'
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_snoozed: Mapped[bool] = mapped_column(Boolean, default=False)
    snoozed_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    speak_aloud: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    fired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="reminders")


# ── Automations ───────────────────────────────────────────────────────────────

class Automation(Base):
    __tablename__ = "automations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    trigger_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # time | command | event
    trigger_config: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON
    conditions: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON
    actions: Mapped[str] = mapped_column(Text, nullable=False, default="[]")     # JSON
    permissions: Mapped[str] = mapped_column(Text, nullable=False, default="[]") # JSON
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_run_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


# ── Agents ────────────────────────────────────────────────────────────────────

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True, index=True)
    agent_name: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    # JARVIS | ATLAS | ORACLE | NEXUS | ATHENA | ECHO | SENTINEL
    input_summary: Mapped[str] = mapped_column(Text, nullable=False)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")
    findings: Mapped[str] = mapped_column(Text, nullable=False, default="[]")   # JSON
    warnings: Mapped[str] = mapped_column(Text, nullable=False, default="[]")   # JSON
    artifacts: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ── Tool Registry ─────────────────────────────────────────────────────────────

class ToolRegistry(Base):
    __tablename__ = "tool_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    # file | system | browser | terminal | communication
    permission_level: Mapped[int] = mapped_column(Integer, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


# ── Approval Requests ─────────────────────────────────────────────────────────

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    approval_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    # low | medium | high | critical
    affected_paths: Mapped[str] = mapped_column(Text, nullable=False, default="[]")     # JSON
    proposed_changes: Mapped[str] = mapped_column(Text, nullable=False, default="[]")   # JSON
    permission_level: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    # pending | approved | rejected | expired
    decision_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


# ── Activity Log ──────────────────────────────────────────────────────────────

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True, index=True)
    agent_name: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tool_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    permission_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    approval_given: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    result: Mapped[str] = mapped_column(String(32), nullable=False)
    # success | partial | failed | denied
    details: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


# ── Provider Settings ─────────────────────────────────────────────────────────

class ProviderSetting(Base):
    __tablename__ = "provider_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    # gemini | ollama
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    max_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extra_config: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


# ── Device Sessions (Mobile companion) ───────────────────────────────────────

class DeviceSession(Base):
    __tablename__ = "device_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    device_name: Mapped[str] = mapped_column(String(128), nullable=False)
    device_type: Mapped[str] = mapped_column(String(32), nullable=False, default="mobile")
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
