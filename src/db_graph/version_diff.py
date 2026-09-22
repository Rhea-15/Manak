from sqlalchemy.orm import Session

from src.db_graph.models import StandardVersion


def compare_versions(db: Session, old_version_id: int, new_version_id: int):
    old_version = (
        db.query(StandardVersion).filter(StandardVersion.id == old_version_id).first()
    )

    new_version = (
        db.query(StandardVersion).filter(StandardVersion.id == new_version_id).first()
    )

    if not old_version:
        return {"error": "Old version not found"}

    if not new_version:
        return {"error": "New version not found"}

    if old_version.standard_id != new_version.standard_id:
        return {"error": "Versions belong to different standards"}

    differences = {}

    if old_version.version_number != new_version.version_number:
        differences["version_number"] = {
            "old": old_version.version_number,
            "new": new_version.version_number,
        }

    if old_version.effective_date != new_version.effective_date:
        differences["effective_date"] = {
            "old": str(old_version.effective_date),
            "new": str(new_version.effective_date),
        }

    if old_version.status != new_version.status:
        differences["status"] = {"old": old_version.status, "new": new_version.status}

    if old_version.document_path != new_version.document_path:
        differences["document_path"] = {
            "old": old_version.document_path,
            "new": new_version.document_path,
        }

    return {
        "standard_id": old_version.standard_id,
        "old_version_id": old_version.id,
        "new_version_id": new_version.id,
        "differences": differences,
    }
