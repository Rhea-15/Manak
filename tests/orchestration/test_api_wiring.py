from unittest.mock import patch

from fastapi.testclient import TestClient

from src.orchestration.main import app

client = TestClient(app)


def test_search_valid_request():
    mock_result = {
        "query": "fireproof wire",
        "results": [
            {
                "standard_number": "IS 694:2010",
                "title": "PVC insulated cables",
                "score": 0.91,
                "status": "active",
                "active_version": "2010",
                "compliance": {},
                "graph": {
                    "found": True,
                    "standard_number": "IS 694:2010",
                    "linked_standards": [],
                },
            }
        ],
        "vector_results_found": 1,
        "results_returned": 1,
        "source": "qdrant_postgresql_neo4j",
    }

    with patch(
        "src.orchestration.routers.search.search_standards",
        return_value=mock_result,
    ):
        resp = client.post(
            "/api/v1/search",
            json={"query": "fireproof wire", "language": "en", "top_k": 3},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "results" in body
    assert isinstance(body["results"], list)


def test_search_invalid_request_missing_query():
    resp = client.post("/api/v1/search", json={"language": "en"})
    assert resp.status_code == 422


def test_recommendation_valid_request():
    resp = client.post(
        "/api/v1/recommendation",
        json={
            "item_id": "item-1",
            "original_spec": "PVC Insulated Wires as per IS 694:1990",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["source"] == "rules_engine"


def test_score_valid_request():
    resp = client.post("/api/v1/score", json={"tender_id": "TND/2026/0431"})
    assert resp.status_code == 200
    assert 0 <= resp.json()["score"] <= 100


def test_score_invalid_request_missing_tender_id():
    resp = client.post("/api/v1/score", json={})
    assert resp.status_code == 422


def test_routes_registered():
    def collect_paths(routes):
        paths = []

        for r in routes:
            p = getattr(r, "path", None)

            if p is not None:
                paths.append(p)

            orig = getattr(r, "original_router", None)

            if orig is not None:
                paths.extend(collect_paths(orig.routes))

            nested = getattr(r, "routes", None)

            if nested:
                paths.extend(collect_paths(nested))

        return paths

    paths = collect_paths(app.routes)

    assert "/api/v1/search" in paths
    assert "/api/v1/recommendation" in paths
    assert "/api/v1/score" in paths
    assert "/audit/logs" in paths
    assert "/compliance/{standard_id}" in paths
    assert "/quality-score/{standard_id}" in paths
    assert "/review/queue" in paths
    assert "/verification/{standard_id}" in paths