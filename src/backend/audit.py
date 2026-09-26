from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backend.database import SessionLocal, get_db
from src.backend.rbac import require_role
from src.db_graph.models import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit"])


def create_audit_log(
    user_id: str,
    endpoint: str,
    action: str,
    details: str,
    db: Session | None = None,
):
    """Persist an audit entry, closing the session when this function opens it."""
    session = db or SessionLocal()

    try:
        audit_entry = AuditLog(
            user_id=user_id,
            endpoint=endpoint,
            action=action,
            details=details,
            created_at=datetime.now(timezone.utc),
        )

        session.add(audit_entry)
        session.commit()
        session.refresh(audit_entry)

        return audit_entry
    finally:
        if db is None:
            session.close()


def get_audit_logs(db: Session):
    """Return audit entries with the newest entries first."""
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()


@router.get("/logs")
def list_audit_logs(
    db: Session = Depends(get_db),  # noqa: B008
    role: str = require_role("ADMIN"),
):
    """Return serialized audit entries to an administrator."""
    logs = get_audit_logs(db)

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "endpoint": log.endpoint,
            "action": log.action,
            "details": log.details,
            "created_at": log.created_at,
        }
        for log in logs
    ]
