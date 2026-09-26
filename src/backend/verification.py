from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.rbac import require_role
from src.backend.verification_engine import verify_compliance_data

router = APIRouter(prefix="/verification", tags=["Verification"])


@router.get("/{standard_id}")
def verify_standard(
    standard_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    role: str = require_role("MANAGER"),
):
    """Run compliance verification for a standard requested by a manager."""
    return verify_compliance_data(db, standard_id)
