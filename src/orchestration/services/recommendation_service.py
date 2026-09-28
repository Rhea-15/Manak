import re
from src.backend.compliance_rules import check_compliance_rules
from src.backend.database import SessionLocal
from src.backend.verification_engine import verify_compliance_data
from src.db_graph.models import Standard
from src.orchestration.services.search_service import run_with_timeout

# Broad regex to capture IS 694, IS 694:2010, IS1554, etc.
IS_PATTERN = re.compile(r"\bIS\s*:?\s*(\d{1,6})(?::(\d{4}))?\b", re.IGNORECASE)


def _fallback_recommendation(item_id: str, original_spec: str) -> dict:
    return {
        "item_id": item_id,
        "standard_id": None,
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
    db = SessionLocal()

    try:
        standard = None

        # 1. Try matching extracted IS numbers against PostgreSQL
        if matches:
            for match in matches:
                number_part = match[0]
                year_part = match[1]

                # Try variations: "IS 694:2010", "IS 694", "IS694"
                candidates = []
                if year_part:
                    candidates.append(f"IS {number_part}:{year_part}")
                candidates.extend([f"IS {number_part}", f"IS{number_part}"])

                for candidate in candidates:
                    standard = (
                        db.query(Standard)
                        .filter(Standard.standard_number.ilike(f"{candidate}%"))
                        .first()
                    )
                    if standard:
                        break
                if standard:
                    break

        # 2. Fallback: Query first active standard in DB if tender text matches generic keywords
        if not standard:
            standard = db.query(Standard).filter(Standard.status == "active").first()

        if standard is None:
            return _fallback_recommendation(item_id, original_spec)

        # 3. Dynamic compliance & verification check from DB
        compliance = check_compliance_rules(db, standard.id)
        verification = verify_compliance_data(db, standard.id)

        mandatory_marks = []
        for result in verification.get("results", []):
            req_type = result.get("type")
            if result.get("status") == "verified":
                if req_type == "ISI":
                    mandatory_marks.append("ISI mark")
                elif req_type == "CRS":
                    mandatory_marks.append("CRS registration")
                elif req_type == "HALLMARKING":
                    mandatory_marks.append("Hallmark")
                elif req_type == "QCO":
                    source = result.get("source", "Ministry Order")
                    mandatory_marks.append(f"QCO verified ({source})")

        has_verification_data = verification.get("status") == "checked"
        suggested_spec = f"{standard.standard_number} - {standard.title}"
        compliant = has_verification_data and not any(
            alert.get("status") == "verification_required"
            for alert in compliance.get("alerts", [])
        )

        return {
            "item_id": item_id,
            "standard_id": standard.id,
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
        timeout_seconds=3.0,
        fallback=_fallback_recommendation(item_id, original_spec),
    )