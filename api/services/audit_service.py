"""FERPA-compliant audit logging."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from api.db.models import AuditLog


def log_action(
    db: Session,
    user_id: uuid.UUID | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    """Write an audit log entry. Actions: login, logout, upload, preview, approve, retry, pipeline_complete, pipeline_failed."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_=metadata,
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    db.commit()
