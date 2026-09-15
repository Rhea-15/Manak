def mock_search(query: str, top_k: int = 5) -> dict:
    return {
        "query": query,
        "results": [
            {
                "is_code": "IS 694:2010",
                "title": "PVC insulated cables for working voltages up to 1100V",
                "score": 0.91,
                "status": "active",
                "snippet": "Flame Retardant Low Smoke (FRLS) copper conductor cables...",
            }
        ][:top_k],
        "took_ms": 42,
    }


def mock_recommendation(item_id: str, original_spec: str) -> dict:
    return {
        "item_id": item_id,
        "original_spec": original_spec,
        "ai_suggested_spec": "PVC Insulated Flame Retardant Low Smoke Wires as per IS 694:2010 (incorporating Amendment 4)",
        "compliant": True,
        "mandatory_marks": ["ISI mark under QCO 2023"],
        "allied_standards": ["IS 10810", "ISO 9001"],
        "source": "rules_engine",
    }


def mock_score(tender_id: str) -> dict:
    return {
        "tender_id": tender_id,
        "score": 52,
        "verdict": "Needs Revision",
        "critical_alerts": [
            {"type": "outdated_spec", "message": "IS 694:1990 superseded by IS 694:2010", "severity": "high"},
            {"type": "mandatory_qco", "message": "ISI marking under QCO 2023 strictly mandatory for Item #1", "severity": "high"},
        ],
    } 