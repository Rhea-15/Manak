from sqlalchemy.orm import Session
from src.db_graph.models import (
    Standard,
    DataSource,
    QCORequirement,
    ISIRequirement,
    CRSRequirement,
    HallmarkingRequirement
)


def verify_compliance_data(db: Session, standard_id: int):

    standard = db.query(Standard).filter(
        Standard.id == standard_id
    ).first()

    if not standard:
        return {
            "standard_id": standard_id,
            "status": "standard_not_found",
            "results": []
        }

    results = []

    requirement_tables = [
        ("QCO", QCORequirement),
        ("ISI", ISIRequirement),
        ("CRS", CRSRequirement),
        ("HALLMARKING", HallmarkingRequirement)
    ]

    for requirement_type, model in requirement_tables:

        requirements = db.query(model).filter(
            model.standard_id == standard_id,
            model.is_active == True
        ).all()

        for requirement in requirements:

            source = None

            if requirement.source_id:
                source = db.query(DataSource).filter(
                    DataSource.id == requirement.source_id
                ).first()

            if not requirement.verified:
                results.append({
                    "type": requirement_type,
                    "status": "verification_required",
                    "reason": "Requirement is not verified",
                    "requirement_id": requirement.id
                })
                continue

            if not source:
                results.append({
                    "type": requirement_type,
                    "status": "verification_required",
                    "reason": "Source information is missing",
                    "requirement_id": requirement.id
                })
                continue

            if not source.is_authoritative:
                results.append({
                    "type": requirement_type,
                    "status": "verification_required",
                    "reason": "Source is not marked authoritative",
                    "requirement_id": requirement.id
                })
                continue

            results.append({
                "type": requirement_type,
                "status": "verified",
                "requirement_id": requirement.id,
                "source": source.source_name
            })

    if not results:
        return {
            "standard_id": standard_id,
            "standard_number": standard.standard_number,
            "status": "no_verified_compliance_data",
            "results": []
        }

    return {
        "standard_id": standard_id,
        "standard_number": standard.standard_number,
        "status": "checked",
        "results": results
    }