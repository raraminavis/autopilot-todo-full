"""init

Revision ID: 0001_init
Revises:
Create Date: 2026-01-28

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("tz", sa.String(), nullable=False, server_default="America/New_York"),
        sa.Column("locale", sa.String(), nullable=False, server_default="en-US"),
        sa.Column("autonomy_mode", sa.String(), nullable=False, server_default="CONFIRM"),
        sa.Column("onboarding_state", sa.String(), nullable=False, server_default="new"),
    )

    op.create_table(
        "tasks",
        sa.Column("task_id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("due_type", sa.String(), nullable=False, server_default="soft_window"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_window_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recurrence_rule", sa.Text(), nullable=True),
        sa.Column("template_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="unassigned"),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False, server_default="30"),
        # upfront splitting policy
        sa.Column("splittable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("min_chunk_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("preferred_chunk_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("max_chunk_minutes", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("max_chunks", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("split_penalty_weight", sa.Float(), nullable=False, server_default="1.0"),
    )
    op.create_index("idx_tasks_user_status_created", "tasks", ["user_id", "status", "created_at"])

    op.create_table(
        "schedule_proposals",
        sa.Column("proposal_id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("strategy", sa.String(), nullable=False),
        sa.Column("objective_weights", sa.JSON(), nullable=False),
        sa.Column("diff", sa.JSON(), nullable=False),
        sa.Column("requires_confirmation", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
    )
    op.create_index("idx_schedule_proposals_user_created", "schedule_proposals", ["user_id", "created_at"])

    op.create_table(
        "proposal_actions",
        sa.Column("action_id", sa.String(), primary_key=True),
        sa.Column("proposal_id", sa.String(), sa.ForeignKey("schedule_proposals.proposal_id"), nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("action_type", sa.String(), nullable=False),
        sa.Column("action_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "task_instances",
        sa.Column("task_instance_id", sa.String(), primary_key=True),
        sa.Column("task_id", sa.String(), sa.ForeignKey("tasks.task_id"), nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("calendar_event_id", sa.String(), nullable=True),
        sa.Column("locked_by_user", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("completion_state", sa.String(), nullable=False, server_default="assumed_done"),
        sa.Column("remaining_minutes", sa.Integer(), nullable=True),
        # upfront splitting
        sa.Column("chunk_group_id", sa.String(), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=True),
        sa.Column("planned_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_task_instances_user_start", "task_instances", ["user_id", "start_at"])

    op.create_table(
        "event_log",
        sa.Column("event_id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_index("idx_event_log_user_time", "event_log", ["user_id", "timestamp"])

def downgrade() -> None:
    op.drop_table("event_log")
    op.drop_table("task_instances")
    op.drop_table("proposal_actions")
    op.drop_table("schedule_proposals")
    op.drop_index("idx_tasks_user_status_created", table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("users")
