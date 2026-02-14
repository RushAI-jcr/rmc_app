"""SQLAlchemy ORM models for application state."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class with deterministic naming conventions for Alembic."""

    metadata_naming_convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    # Override metadata to use naming convention
    from sqlalchemy import MetaData

    metadata = MetaData(naming_convention=metadata_naming_convention)


# Enums
session_status_enum = Enum(
    "uploaded", "validated", "approved", "processing", "complete", "failed",
    name="session_status",
)
run_status_enum = Enum(
    "pending", "running", "complete", "failed",
    name="run_status",
)
pipeline_step_enum = Enum(
    "ingestion", "llm_scoring", "cleaning", "features", "ml_scoring", "triage",
    name="pipeline_step",
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="staff")
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    last_login = Column(DateTime(timezone=True), nullable=True)

    upload_sessions = relationship("UploadSession", back_populates="uploader")
    audit_logs = relationship("AuditLog", back_populates="user")
    review_decisions = relationship("ReviewDecision", back_populates="reviewer")


class UploadSession(Base):
    __tablename__ = "upload_sessions"
    __table_args__ = (
        Index("ix_upload_sessions_cycle_status", "cycle_year", "status"),
        Index(
            "ix_upload_sessions_active",
            "is_active",
            unique=True,
            postgresql_where=Column("is_active") == True,  # noqa: E712
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    cycle_year = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    file_manifest = Column(JSONB, nullable=True)
    validation_result = Column(JSONB, nullable=True)
    status = Column(session_status_enum, nullable=False, default="uploaded")

    uploader = relationship("User", back_populates="upload_sessions")
    pipeline_runs = relationship("PipelineRun", back_populates="upload_session")


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    __table_args__ = (
        Index("ix_pipeline_runs_session_status", "upload_session_id", "status"),
        # Prevent duplicate active runs per session (allows retry after completion/failure)
        Index(
            "uq_pipeline_runs_active",
            "upload_session_id",
            unique=True,
            postgresql_where=text("status IN ('pending', 'running')"),
        ),
        CheckConstraint("progress_pct BETWEEN 0 AND 100", name="progress_pct_range"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("upload_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    current_step = Column(pipeline_step_enum, nullable=True)
    progress_pct = Column(Integer, nullable=False, default=0)
    result_summary = Column(JSONB, nullable=True)
    error_log = Column(Text, nullable=True)
    status = Column(run_status_enum, nullable=False, default="pending")

    upload_session = relationship("UploadSession", back_populates="pipeline_runs")


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        Index("ix_audit_log_user_created", "user_id", "created_at"),
        Index("ix_audit_log_resource", "resource_type", "resource_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(255), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    user = relationship("User", back_populates="audit_logs")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"
    __table_args__ = (
        UniqueConstraint("amcas_id", "cycle_year", name="uq_review_decisions_applicant_cycle"),
        Index("ix_review_decisions_cycle_reviewer", "cycle_year", "reviewer_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amcas_id = Column(Integer, nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    cycle_year = Column(Integer, nullable=False)
    decision = Column(String(20), nullable=False)
    flag_reason = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    predicted_score = Column(Float, nullable=True)
    predicted_tier = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=_utcnow)

    reviewer = relationship("User", back_populates="review_decisions")
