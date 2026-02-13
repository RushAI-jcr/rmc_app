"""Initial schema: users, upload_sessions, pipeline_runs, audit_log

Revision ID: 0001
Revises:
Create Date: 2026-02-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums
    session_status = sa.Enum(
        "uploaded", "validated", "approved", "processing", "complete", "failed",
        name="session_status",
    )
    run_status = sa.Enum(
        "pending", "running", "complete", "failed",
        name="run_status",
    )
    pipeline_step = sa.Enum(
        "ingestion", "llm_scoring", "cleaning", "features", "ml_scoring", "triage",
        name="pipeline_step",
    )

    # Users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(150), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="staff"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )

    # Upload Sessions
    op.create_table(
        "upload_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("uploaded_by", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cycle_year", sa.Integer, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("file_manifest", JSONB, nullable=True),
        sa.Column("validation_result", JSONB, nullable=True),
        sa.Column("status", session_status, nullable=False, server_default="uploaded"),
    )
    op.create_index("ix_upload_sessions_cycle_status", "upload_sessions", ["cycle_year", "status"])
    op.create_index(
        "ix_upload_sessions_active", "upload_sessions", ["is_active"],
        unique=True, postgresql_where=sa.text("is_active = true"),
    )

    # Pipeline Runs
    op.create_table(
        "pipeline_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("upload_session_id", UUID(as_uuid=True), sa.ForeignKey("upload_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("current_step", pipeline_step, nullable=True),
        sa.Column("progress_pct", sa.Integer, nullable=False, server_default="0"),
        sa.Column("result_summary", JSONB, nullable=True),
        sa.Column("error_log", sa.Text, nullable=True),
        sa.Column("status", run_status, nullable=False, server_default="pending"),
        sa.CheckConstraint("progress_pct BETWEEN 0 AND 100", name="ck_pipeline_runs_progress_pct_range"),
    )
    op.create_index("ix_pipeline_runs_session_status", "pipeline_runs", ["upload_session_id", "status"])
    # Partial unique index: only one pending/running run per session
    op.create_index(
        "uq_pipeline_runs_active",
        "pipeline_runs",
        ["upload_session_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'running')"),
    )

    # Audit Log
    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_log_user_created", "audit_log", ["user_id", "created_at"])
    op.create_index("ix_audit_log_resource", "audit_log", ["resource_type", "resource_id"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("pipeline_runs")
    op.drop_table("upload_sessions")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS pipeline_step")
    op.execute("DROP TYPE IF EXISTS run_status")
    op.execute("DROP TYPE IF EXISTS session_status")
