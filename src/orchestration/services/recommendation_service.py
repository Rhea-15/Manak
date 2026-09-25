import re

from src.backend.compliance_rules import check_compliance_rules
from src.backend.database import SessionLocal
from src.backend.verification_engine import verify_compliance_data
from src.db_graph.models import Standard
from src.orchestration.services.search_service import run_with_timeout

IS_PATTERN = re.compile(r"\bIS\s+\d{1,6}:\d{4}\b", re.IGNORECASE)


def _fallback_recommendation(item_id: str, original_spec: str) -> dict:
    return {
        "item_id": item_id,
        "original_spec": original_spec,
        "ai_suggested_spec": "Verification required",
        "compliant": False,
        "mandatory_marks": [],
        "allied_standards": [],
        "source": "rules_engine",
        "status": "fallback",
    }


def _recommend_standard_impl(item_id: str, original_spec: str) -> dict:
    matches = IS_PATTERN.findall(original_spec)

    if not matches:
        return _fallback_recommendation(item_id, original_spec)

    standard_number = matches[0].upper().replace(" ", " ")

    db = SessionLocal()

    try:
        standard = (
            db.query(Standard)
            .filter(Standard.standard_number == standard_number)
            .first()
        )

        if standard is None:
            return _fallback_recommendation(item_id, original_spec)

        compliance = check_compliance_rules(db, standard.id)
        verification = verify_compliance_data(db, standard.id)

        mandatory_marks = []
        verified_types = set()

        for result in verification.get("results", []):
            if result.get("status") != "verified":
                continue

            requirement_type = result.get("type")
            verified_types.add(requirement_type)

            if requirement_type == "ISI":
                mandatory_marks.append("ISI mark")
            elif requirement_type == "CRS":
                mandatory_marks.append("CRS registration")
            elif requirement_type == "HALLMARKING":
                mandatory_marks.append("Hallmark")
            elif requirement_type == "QCO":
                mandatory_types = result.get("source")
                if mandatory_types:
                    mandatory_marks.append(
                        f"QCO requirement verified from {mandatory_types}"
                    )

        has_verification_data = verification.get("status") == "checked"

        if not has_verification_data:
            suggested_spec = "Verification required"
            compliant = False
        else:
            suggested_spec = (
                f"{standard.standard_number} - {standard.title}"
            )
            compliant = not any(
                alert.get("status") == "verification_required"
                for alert in compliance.get("alerts", [])
            )

        return {
            "item_id": item_id,
            "original_spec": original_spec,
            "ai_suggested_spec": suggested_spec,
            "compliant": compliant,
            "mandatory_marks": list(dict.fromkeys(mandatory_marks)),
            "allied_standards": [],
            "source": "rules_engine",
        }

    finally:
        db.close()


def recommend_standard(item_id: str, original_spec: str) -> dict:
    return run_with_timeout(
        _recommend_standard_impl,
        item_id,
        original_spec,
        timeout_seconds=2.0,
        fallback=_fallback_recommendation(item_id, original_spec),
    )