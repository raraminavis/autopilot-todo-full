from __future__ import annotations

import uuid
from sqlalchemy import String, Text, DateTime, Integer, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .db import Base

def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    tz: Mapped[str] = mapped_column(String, default="America/New_York")
    locale: Mapped[str] = mapped_column(String, default="en-US")
    autonomy_mode: Mapped[str] = mapped_column(String, default="CONFIRM")
    onboarding_state: Mapped[str] = mapped_column(String, default="new")

class Task(Base):
    __tablename__ = "tasks"
    task_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"), index=True)

    raw_text: Mapped[str] = mapped_column(Text)
    normalized_text: Mapped[str] = mapped_column(Text)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    due_type: Mapped[str] = mapped_column(String, default="soft_window")
    due_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_window_start: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_window_end: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    recurrence_rule: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_id: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[str] = mapped_column(String, default="unassigned")
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30)

    # upfront splitting policy
    splittable: Mapped[bool] = mapped_column(Boolean, default=True)
    min_chunk_minutes: Mapped[int] = mapped_column(Integer, default=30)
    preferred_chunk_minutes: Mapped[int] = mapped_column(Integer, default=60)
    max_chunk_minutes: Mapped[int] = mapped_column(Integer, default=120)
    max_chunks: Mapped[int] = mapped_column(Integer, default=4)
    split_penalty_weight: Mapped[float] = mapped_column(Float, default=1.0)

class ScheduleProposal(Base):
    __tablename__ = "schedule_proposals"
    proposal_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"), index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    strategy: Mapped[str] = mapped_column(String)
    objective_weights: Mapped[dict] = mapped_column(JSON, default=dict)
    diff: Mapped[dict] = mapped_column(JSON, default=dict)
    requires_confirmation: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String, default="pending")

class ProposalAction(Base):
    __tablename__ = "proposal_actions"
    action_id: Mapped[str] = mapped_column(String, primary_key=True)
    proposal_id: Mapped[str] = mapped_column(String, ForeignKey("schedule_proposals.proposal_id"), index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"), index=True)
    action_type: Mapped[str] = mapped_column(String)
    action_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class TaskInstance(Base):
    __tablename__ = "task_instances"
    task_instance_id: Mapped[str] = mapped_column(String, primary_key=True)
    task_id: Mapped[str] = mapped_column(String, ForeignKey("tasks.task_id"), index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"), index=True)

    start_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    calendar_event_id: Mapped[str | None] = mapped_column(String, nullable=True)

    locked_by_user: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_state: Mapped[str] = mapped_column(String, default="assumed_done")
    remaining_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # upfront splitting
    chunk_group_id: Mapped[str | None] = mapped_column(String, nullable=True)
    chunk_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planned_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class EventLog(Base):
    __tablename__ = "event_log"
    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"), index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
