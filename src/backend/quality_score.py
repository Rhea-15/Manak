from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.rbac import require_role

from src.db_graph.models import (
    Standard,
    StandardVersion,
    QCORequirement,
    ISIRequirement,
    CRSRequirement,
    HallmarkingRequirement
)


router = APIRouter(
    prefix="/quality-score",
    tags=["Quality Score"]
)


def calculate_quality_score(db: Session, standard_id: int):

    standard = (
        db.query(Standard)
        .filter(Standard.id == standard_id)
        .first()
    )

    if not standard:
        return {
            "standard_id": standard_id,
            "score": 0,
            "status": "standard_not_found"
        }

    score = 0

    versions = (
        db.query(StandardVersion)
        .filter(StandardVersion.standard_id == standard_id)
        .all()
    )

    if versions:
        score += 35

    active_version = (
        db.query(StandardVersion)
        .filter(
            StandardVersion.standard_id == standard_id,
            StandardVersion.status == "active"
        )
        .first()
    )

    if active_version:
        score += 25

    requirement_models = [
        QCORequirement,
        ISIRequirement,
        CRSRequirement,
        HallmarkingRequirement
    ]

    requirements = []

    for model in requirement_models:
        requirements.extend(
            db.query(model)
            .filter(
                model.standard_id == standard_id,
                model.is_active == True
            )
            .all()
        )

    if requirements:
        verified_count = sum(
            1 for requirement in requirements
            if requirement.verified
        )

        verification_score = (
            verified_count / len(requirements)
        ) * 25

        score += verification_score
    else:
        verification_score = 0

    source_ids = [
        requirement.source_id
        for requirement in requirements
        if requirement.source_id is not None
    ]

    if source_ids:
        from src.db_graph.models import DataSource

        sources = (
            db.query(DataSource)
            .filter(DataSource.id.in_(source_ids))
            .all()
        )

        authoritative_count = sum(
            1 for source in sources
            if source.is_authoritative
        )

        traceability_score = (
            authoritative_count / len(source_ids)
        ) * 15

        score += traceability_score
    else:
        traceability_score = 0

    score = round(min(score, 100), 2)

    return {
        "standard_id": standard_id,
        "standard_number": standard.standard_number,
        "score": score,
        "breakdown": {
            "standards_coverage": 35,
            "version_validity": 25,
            "compliance_verification": round(
                verification_score, 2
            ),
            "source_traceability": round(
                traceability_score, 2
            )
        }
    }


@router.get("/{standard_id}")
def get_quality_score(
    standard_id: int,
    db: Session = Depends(get_db),
    role: str = require_role("MANAGER")
):
    return calculate_quality_score(
        db,
        standard_id
    )