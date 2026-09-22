def mock_search(query: str, top_k: int = 5) -> dict:
    """Return a fixed set of mock IS-standard search results for a given query.

    Stands in for Dev 3's future hybrid search (bge-m3 + Qdrant + BM25 + RRF);
    the return shape matches the real service's future contract.
    """
    candidates = [
        {
            "is_code": "IS 694:2010",
            "title": "PVC insulated cables for working voltages up to 1100V",
            "score": 0.91,
            "status": "active",
            "snippet": "Flame Retardant Low Smoke (FRLS) copper conductor cables...",
        },
        {
            "is_code": "IS 694:1990",
            "title": "PVC insulated cables (superseded edition)",
            "score": 0.74,
            "status": "superseded",
            "snippet": "Superseded by IS 694:2010 — retained for historical lookup only.",
        },
        {
            "is_code": "IS 10810",
            "title": "Methods of test for cables",
            "score": 0.68,
            "status": "active",
            "snippet": "Mandatory test methods referenced by IS 694:2010, Clause 4.2.",
        },
        {
            "is_code": "IS 8130",
            "title": "Conductors for insulated electric cables and flexible cords",
            "score": 0.61,
            "status": "active",
            "snippet": "Annealed copper conductor specification, cross-referenced allied standard.",
        },
    ]
    return {
        "query": query,
        "results": candidates[:top_k],
        "took_ms": 42,
    }

def mock_recommendation(item_id: str, original_spec: str) -> dict:
    """Return a fixed mock recommendation, standing in for Dev 1's real rules engine output."""
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
    """Return a fixed mock Tender Quality Score, standing in for Dev 2's real scoring formula."""
    return {
        "tender_id": tender_id,
        "score": 52,
        "verdict": "Needs Revision",
        "critical_alerts": [
            {
                "type": "outdated_spec",
                "message": "IS 694:1990 superseded by IS 694:2010",
                "severity": "high",
            },
            {
                "type": "mandatory_qco",
                "message": "ISI marking under QCO 2023 strictly mandatory for Item #1",
                "severity": "high",
            },
        ],
    }
