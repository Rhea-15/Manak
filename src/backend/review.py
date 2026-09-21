from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backend.audit import create_audit_log
from src.backend.database import get_db
from src.db_graph.models import ReviewQueue


router = APIRouter(
    prefix="/review",
    tags=["Review Queue"]
)


@router.get("/queue")
def get_review_queue(
    db: Session = Depends(get_db)
):
    items = (
        db.query(ReviewQueue)
        .order_by(ReviewQueue.created_at.desc())
        .all()
    )

    return [
        {
            "id": item.id,
            "document_name": item.document_name,
            "document_path": item.document_path,
            "status": item.status,
            "submitted_by": item.submitted_by,
            "reviewed_by": item.reviewed_by,
            "review_notes": item.review_notes,
            "created_at": item.created_at
        }
        for item in items
    ]


@router.put("/{review_id}/approve")
def approve_document(
    review_id: int,
    db: Session = Depends(get_db)
):
    item = (
        db.query(ReviewQueue)
        .filter(ReviewQueue.id == review_id)
        .first()
    )

    if not item:
        return {
            "success": False,
            "message": "Review item not found"
        }

    item.status = "approved"
    item.reviewed_by = "admin"

    db.commit()
    db.refresh(item)
    create_audit_log(
    user_id="admin",
    endpoint=f"/review/{review_id}/approve",
    action="APPROVE_DOCUMENT",
    details=f"Document {item.document_name} approved"
)

    return {
        "success": True,
        "review_id": item.id,
        "status": item.status,
        "reviewed_by": item.reviewed_by
    }


@router.put("/{review_id}/reject")
def reject_document(
    review_id: int,
    db: Session = Depends(get_db)
):
    item = (
        db.query(ReviewQueue)
        .filter(ReviewQueue.id == review_id)
        .first()
    )

    if not item:
        return {
            "success": False,
            "message": "Review item not found"
        }

    item.status = "rejected"
    item.reviewed_by = "admin"

    db.commit()
    db.refresh(item)
    create_audit_log(
    user_id="admin",
    endpoint=f"/review/{review_id}/reject",
    action="REJECT_DOCUMENT",
    details=f"Document {item.document_name} rejected"
)
    return {
        "success": True,
        "review_id": item.id,
        "status": item.status,
        "reviewed_by": item.reviewed_by
    }