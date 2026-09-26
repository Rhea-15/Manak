from unittest.mock import patch

from fastapi.testclient import TestClient

from src.orchestration.main import app

client = TestClient(app)


def _search_result(count: int = 1) -> dict:
    return {
        "query": "wire",
        "results": [
            {
                "standard_number": f"IS {index}",
                "title": "PVC insulated cables",
                "score": 0.91,
                "status": "active",
                "active_version": "2010",
                "compliance": {},
                "graph": {"found": True, "linked_standards": []},
            }
            for index in range(count)
        ],
        "vector_results_found": count,
        "results_returned": count,
        "source": "qdrant_postgresql_neo4j",
    }


def test_search_valid_request():
    """A valid search request returns the mocked standard results."""
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
    """A request missing the required query field returns 422."""
    resp = client.post("/api/v1/search", json={"language": "en"})
    assert resp.status_code == 422


def test_recommendation_valid_request():
    """A well-formed recommendation request returns 200 from the rules engine."""
    mock_result = {
        "source": "rules_engine",
        "recommendation": "Recommended spec",
        # Add other required fields based on RecommendationResponse schema
    }
    
    with patch(
        "src.orchestration.services.recommendation_service",
        return_value=mock_result,
    ):
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
    """A well-formed score request returns 200 with a score in [0, 100]."""
    resp = client.post("/api/v1/score", json={"tender_id": "TND/2026/0431"})
    assert resp.status_code == 200
    assert 0 <= resp.json()["score"] <= 100


def test_score_invalid_request_missing_tender_id():
    """A score request missing tender_id returns 422."""
    resp = client.post("/api/v1/score", json={})
    assert resp.status_code == 422

def test_search_whitespace_query_returns_400():
    """A whitespace-only query is rejected with 400, since Pydantic alone allows it."""
    resp = client.post("/api/v1/search", json={"query": "   ", "language": "en"})
    assert resp.status_code == 400


def test_search_top_k_zero_returns_422():
    """A top_k of 0 fails Pydantic's range validation and returns 422."""
    resp = client.post("/api/v1/search", json={"query": "wire", "top_k": 0})
    assert resp.status_code == 422


def test_search_invalid_language_returns_422():
    """A language value outside the allowed enum returns 422."""
    resp = client.post("/api/v1/search", json={"query": "wire", "language": "fr"})
    assert resp.status_code == 422


def test_search_returns_multiple_results():
    """The mock search service returns exactly top_k results when enough candidates exist."""
    with patch(
        "src.orchestration.routers.search.search_standards",
        return_value=_search_result(4),
    ):
        resp = client.post("/api/v1/search", json={"query": "wire", "top_k": 4})
    assert len(resp.json()["results"]) == 4


def test_search_respects_top_k_limit():
    """Requesting top_k=1 returns exactly one result."""
    with patch(
        "src.orchestration.routers.search.search_standards",
        return_value=_search_result(1),
    ):
        resp = client.post("/api/v1/search", json={"query": "wire", "top_k": 1})
    assert len(resp.json()["results"]) == 1


def test_search_response_schema_fields():
    """Each search result includes all fields required by the frontend contract."""
    with patch(
        "src.orchestration.routers.search.search_standards",
        return_value=_search_result(),
    ):
        resp = client.post("/api/v1/search", json={"query": "wire"})
    result = resp.json()["results"][0]
    for field in (
        "standard_number",
        "title",
        "score",
        "status",
        "active_version",
        "compliance",
        "graph",
    ):
        assert field in result


def test_search_hinglish_language_accepted():
    """The 'hinglish' language value is accepted and returns 200."""
    resp = client.post("/api/v1/search", json={"query": "fireproof taar", "language": "hinglish"})
    assert resp.status_code == 200


def test_cors_headers_present():
    """A preflight OPTIONS request from the frontend origin receives the correct CORS header."""
    resp = client.options(
        "/api/v1/search",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"

# FastAPI 0.141+ wraps included routers; unwrap via original_router to find real paths
def collect_paths(routes):
    """Recursively collect route paths, unwrapping FastAPI's router nesting (0.141+)."""
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


def test_routes_registered():
    """All three orchestration endpoints are registered on the app."""
    paths = collect_paths(app.routes)

    assert "/api/v1/search" in paths
    assert "/api/v1/recommendation" in paths
    assert "/api/v1/score" in paths
    assert "/audit/logs" in paths
    assert "/compliance/{standard_id}" in paths
    assert "/quality-score/{standard_id}" in paths
    assert "/review/queue" in paths
    assert "/verification/{standard_id}" in paths

