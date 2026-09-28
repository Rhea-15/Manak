from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.db_graph.models import AuditLog


router = APIRouter(
    prefix="/audit",
    tags=["Audit Logs"]
)


@router.get("/logs")
def get_audit_logs(
    db: Session = Depends(get_db)
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "endpoint": log.endpoint,
            "action": log.action,
            "details": log.details,
            "created_at": log.created_at
        }
        for log in logs
    ]