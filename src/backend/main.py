from fastapi import FastAPI, Depends
from src.backend.review import router as review_router
from sqlalchemy.orm import Session
from src.db_graph.version_diff import compare_versions
from src.backend.database import get_db
from src.backend.unified_api import router as unified_router
from src.backend.audit_api import router as audit_router
from src.backend.graph_api import router as graph_router
from src.backend.documents import router as documents_router
from src.backend.quality_score import router as quality_score_router
from src.backend.verification import router as verification_router
from src.db_graph.versioning import (
    get_versions,
    get_active_version,
    validate_standard_status
)

app = FastAPI(
    title="MANAK API",
    version="1.0.0"
)
app.include_router(documents_router)
app.include_router(review_router)
app.include_router(audit_router)
app.include_router(quality_score_router)
app.include_router(verification_router)
app.include_router(graph_router)
app.include_router(unified_router)

@app.get("/")
def root():
    return {
        "message": "MANAK API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/standards/{standard_id}/versions")
def standard_versions(
    standard_id: int,
    db: Session = Depends(get_db)
):
    versions = get_versions(db, standard_id)

    return [
        {
            "id": version.id,
            "version_number": version.version_number,
            "effective_date": version.effective_date,
            "status": version.status
        }
        for version in versions
    ]


@app.get("/standards/{standard_id}/active-version")
def active_version(
    standard_id: int,
    db: Session = Depends(get_db)
):
    version = get_active_version(db, standard_id)

    if not version:
        return {
            "status": "no_active_version"
        }

    return {
        "id": version.id,
        "version_number": version.version_number,
        "effective_date": version.effective_date,
        "status": version.status
    }


@app.get("/standards/{standard_id}/validate")
def validate_standard(
    standard_id: int,
    db: Session = Depends(get_db)
):
    return validate_standard_status(db, standard_id)
<<<<<<< HEAD


=======
>>>>>>> 240e0e8a30bc687b7b154b536634473b3a5f11e6
@app.get("/versions/diff/{old_version_id}/{new_version_id}")
def version_difference(
    old_version_id: int,
    new_version_id: int,
    db: Session = Depends(get_db)
):
    return compare_versions(
        db,
        old_version_id,
        new_version_id
    )