from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.rbac import require_role
from src.db_graph.models import Standard
from src.db_graph.versioning import (
    get_versions,
    get_active_version,
    validate_standard_status
)
from src.db_graph.version_diff import compare_versions
from src.backend.verification_engine import verify_compliance_data
from src.db_graph.graph_payload import build_graph_payload


router = APIRouter(
    prefix="/unified",
    tags=["Unified API"]
)


@router.get("/standard/{standard_id}")
def get_unified_standard(
    standard_id: int,
    db: Session = Depends(get_db),
    role: str = require_role("MANAGER")
):
    standard = (
        db.query(Standard)
        .filter(Standard.id == standard_id)
        .first()
    )

    if not standard:
        raise HTTPException(
            status_code=404,
            detail="Standard not found"
        )

    versions = get_versions(db, standard_id)
    active_version = get_active_version(db, standard_id)
    validation = validate_standard_status(db, standard_id)
    verification = verify_compliance_data(db, standard_id)
    graph = build_graph_payload(standard.standard_number)

    return {
        "standard": {
            "id": standard.id,
            "standard_number": standard.standard_number,
            "title": standard.title,
            "description": standard.description,
            "status": standard.status
        },
        "versions": [
            {
                "id": v.id,
                "version_number": v.version_number,
                "effective_date": v.effective_date,
                "status": v.status
            }
            for v in versions
        ],
        "active_version": (
            {
                "id": active_version.id,
                "version_number": active_version.version_number,
                "effective_date": active_version.effective_date,
                "status": active_version.status
            }
            if active_version
            else None
        ),
        "validation": validation,
        "verification": verification,
        "graph": graph
    }


@router.get("/standard/{standard_id}/versions")
def get_unified_versions(
    standard_id: int,
    db: Session = Depends(get_db),
    role: str = require_role("MANAGER")
):
    standard = (
        db.query(Standard)
        .filter(Standard.id == standard_id)
        .first()
    )

    if not standard:
        raise HTTPException(
            status_code=404,
            detail="Standard not found"
        )

    versions = get_versions(db, standard_id)

    return {
        "standard_id": standard_id,
        "standard_number": standard.standard_number,
        "versions": [
            {
                "id": v.id,
                "version_number": v.version_number,
                "effective_date": v.effective_date,
                "status": v.status
            }
            for v in versions
        ]
    }


@router.get("/standard/{standard_id}/verification")
def get_unified_verification(
    standard_id: int,
    db: Session = Depends(get_db),
    role: str = require_role("MANAGER")
):
    standard = (
        db.query(Standard)
        .filter(Standard.id == standard_id)
        .first()
    )

    if not standard:
        raise HTTPException(
            status_code=404,
            detail="Standard not found"
        )

    return verify_compliance_data(db, standard_id)


@router.get("/standard/{standard_id}/graph")
def get_unified_graph(
    standard_id: int,
    db: Session = Depends(get_db),
    role: str = require_role("MANAGER")
):
    standard = (
        db.query(Standard)
        .filter(Standard.id == standard_id)
        .first()
    )

    if not standard:
        raise HTTPException(
            status_code=404,
            detail="Standard not found"
        )

    return build_graph_payload(standard.standard_number)


@router.get("/version-diff/{old_version_id}/{new_version_id}")
def get_unified_version_diff(
    old_version_id: int,
    new_version_id: int,
    db: Session = Depends(get_db),
    role: str = require_role("MANAGER")
):
    try:
        return compare_versions(
            db,
            old_version_id,
            new_version_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )