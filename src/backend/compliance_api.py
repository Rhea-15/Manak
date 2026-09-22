from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backend.compliance_rules import check_compliance_rules
from src.backend.database import get_db
from src.backend.rbac import require_role

router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.get("/{standard_id}")
def get_compliance_status(
    standard_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    role: str = require_role("MANAGER"),
):
    return check_compliance_rules(db, standard_id)
