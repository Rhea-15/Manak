from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.db_graph.models import (
    CRSRequirement,
    HallmarkingRequirement,
    ISIRequirement,
    QCORequirement,
    Standard,
)

REQUIREMENT_MODELS = {
    "QCO": QCORequirement,
    "ISI": ISIRequirement,
    "CRS": CRSRequirement,
    "HALLMARKING": HallmarkingRequirement,
}


def check_requirement_status(requirement, today=None):
    if today is None:
        today = datetime.now(timezone.utc).date()

    if not requirement.is_active:
        return {"status": "inactive", "reason": "Requirement is inactive"}

    if not requirement.verified:
        return {
            "status": "verification_required",
            "reason": "Requirement is not verified",
        }

    if requirement.effective_from and today < requirement.effective_from:
        return {
            "status": "not_yet_effective",
            "reason": "Requirement is not yet effective",
        }

    if requirement.effective_to and today > requirement.effective_to:
        return {"status": "expired", "reason": "Requirement has expired"}

    if not requirement.source_id:
        return {
            "status": "verification_required",
            "reason": "Source information is missing",
        }

    return {"status": "active_verified", "reason": "Requirement is active and verified"}


def check_compliance_rules(db: Session, standard_id: int, today=None):
    standard = db.query(Standard).filter(Standard.id == standard_id).first()

    if not standard:
        return {
            "standard_id": standard_id,
            "status": "standard_not_found",
            "alerts": [],
        }

    alerts = []
    summary = {"QCO": 0, "ISI": 0, "CRS": 0, "HALLMARKING": 0}

    for requirement_type, model in REQUIREMENT_MODELS.items():
        requirements = db.query(model).filter(model.standard_id == standard_id).all()

        for requirement in requirements:
            summary[requirement_type] += 1

            result = check_requirement_status(requirement, today)

            if result["status"] != "active_verified":
                requirement_name = getattr(requirement, "requirement_name", None)

                qco_reference = getattr(requirement, "qco_reference", None)

                alerts.append(
                    {
                        "type": requirement_type,
                        "requirement_id": requirement.id,
                        "requirement_name": (requirement_name or qco_reference),
                        "status": result["status"],
                        "reason": result["reason"],
                    }
                )

    return {
        "standard_id": standard_id,
        "standard_number": standard.standard_number,
        "status": "checked",
        "summary": summary,
        "alerts": alerts,
    }
