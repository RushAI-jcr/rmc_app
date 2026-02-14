"""Add review_decisions table and users.is_active column

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_active to users
    op.add_column("users", sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"))

    # Create review_decisions table
    op.create_table(
        "review_decisions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("amcas_id", sa.Integer, nullable=False),
        sa.Column("reviewer_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("cycle_year", sa.Integer, nullable=False),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("flag_reason", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("predicted_score", sa.Float, nullable=True),
        sa.Column("predicted_tier", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("amcas_id", "cycle_year", name="uq_review_decisions_applicant_cycle"),
    )
    op.create_index(
        "ix_review_decisions_cycle_reviewer",
        "review_decisions",
        ["cycle_year", "reviewer_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_review_decisions_cycle_reviewer", table_name="review_decisions")
    op.drop_table("review_decisions")
    op.drop_column("users", "is_active")
