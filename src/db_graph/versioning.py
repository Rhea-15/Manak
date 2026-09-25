from datetime import date

from sqlalchemy.orm import Session

from src.db_graph.models import Standard, StandardVersion


def get_versions(db: Session, standard_id: int):
    return (
        db.query(StandardVersion)
        .filter(StandardVersion.standard_id == standard_id)
        .order_by(StandardVersion.effective_date)
        .all()
    )


def get_active_version(db: Session, standard_id: int):
    return (
        db.query(StandardVersion)
        .filter(
            StandardVersion.standard_id == standard_id,
            StandardVersion.status == "active",
        )
        .first()
    )


def create_new_version(
    db: Session,
    standard_id: int,
    version_number: str,
    effective_date: date,
    source_id: int | None = None,
):
    old_version = get_active_version(db, standard_id)

    if old_version:
        old_version.status = "superseded"

    new_version = StandardVersion(
        standard_id=standard_id,
        source_id=source_id,
        version_number=version_number,
        effective_date=effective_date,
        status="active",
    )

    db.add(new_version)
    db.commit()
    db.refresh(new_version)

    return new_version


def validate_standard_status(db: Session, standard_id: int):
    standard = db.query(Standard).filter(Standard.id == standard_id).first()

    if not standard:
        return {"valid": False, "status": "not_found"}

    active_version = get_active_version(db, standard_id)

    if active_version:
        return {
            "valid": True,
            "standard_id": standard.id,
            "standard_number": standard.standard_number,
            "status": "active",
            "active_version": active_version.version_number,
        }

    return {
        "valid": False,
        "standard_id": standard.id,
        "standard_number": standard.standard_number,
        "status": "no_active_version",
    }
