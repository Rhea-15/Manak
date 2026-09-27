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
        "item_id": "item-1",
        "original_spec": "PVC Insulated Wires as per IS 694:1990",
        "ai_suggested_spec": "PVC Insulated Wires as per IS 694:2010",
        "compliant": True,
        "mandatory_marks": ["safety", "quality"],
        "allied_standards": ["IS 1554"],
        "source": "rules_engine",
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


def test_search_english_bypasses_translation(monkeypatch):
    """language=en never invokes the translation service at all."""
    called = {"hit": False}

    def fake_translation_service(query):
        called["hit"] = True
        return {"original": query, "normalized": query, "language": "eng_Latn", "is_translation": False}

    import src.orchestration.routers.search as search_router
    monkeypatch.setattr(search_router, "translation_service", fake_translation_service)

    resp = client.post("/api/v1/search", json={"query": "fireproof wire", "language": "en"})
    assert resp.status_code == 200
    assert called["hit"] is False


def test_search_hindi_invokes_translation(monkeypatch):
    """language=hi calls translation_service with the raw query."""
    calls = []

    def fake_translation_service(query):
        calls.append(query)
        return {"original": query, "normalized": "fireproof wire", "language": "hin_Deva", "is_translation": True}

    import src.orchestration.routers.search as search_router
    monkeypatch.setattr(search_router, "translation_service", fake_translation_service)

    resp = client.post("/api/v1/search", json={"query": "आग रोधक तार", "language": "hi"})
    assert resp.status_code == 200
    assert calls == ["आग रोधक तार"]


def test_search_response_echoes_original_not_translated(monkeypatch):
    """SearchResponse.query always shows the original user text, never the translated one."""
    def fake_translation_service(query):
        return {"original": query, "normalized": "fireproof wire", "language": "hin_Deva", "is_translation": True}

    import src.orchestration.routers.search as search_router
    monkeypatch.setattr(search_router, "translation_service", fake_translation_service)

    resp = client.post("/api/v1/search", json={"query": "आग रोधक तार", "language": "hi"})
    assert resp.json()["query"] == "आग रोधक तार"


def test_search_receives_canonical_translated_query(monkeypatch):
    """search_standards is called with the translated/normalized query, not the raw original."""
    received = {}

    def fake_search_standards(query, top_k):
        received["query"] = query
        return {
            "query": query,
            "results": [],
            "vector_results_found": 0,
            "results_returned": 0,
            "source": "qdrant_postgresql_neo4j",
        }

    def fake_translation_service(query):
        return {"original": query, "normalized": "fireproof wire", "language": "hin_Deva", "is_translation": True}

    import src.orchestration.routers.search as search_router
    monkeypatch.setattr(search_router, "search_standards", fake_search_standards)
    monkeypatch.setattr(search_router, "translation_service", fake_translation_service)

    client.post("/api/v1/search", json={"query": "आग रोधक तार", "language": "hi"})
    assert received["query"] == "fireproof wire"


def test_search_hinglish_does_not_error(monkeypatch):
    """With langdetect installed but transformers still absent, hinglish is expected
    to fall back to a passthrough — this only asserts the request completes cleanly,
    not that real translation occurred."""
    resp = client.post("/api/v1/search", json={"query": "fireproof taar chahiye", "language": "hinglish"})
    assert resp.status_code == 200


def test_search_translation_failure_returns_500(monkeypatch):
    """An unexpected exception from translation_service maps to a clean 500, no traceback leaked."""
    def broken_translation_service(query):
        raise RuntimeError("simulated unexpected failure")

    import src.orchestration.routers.search as search_router
    monkeypatch.setattr(search_router, "translation_service", broken_translation_service)

    resp = client.post("/api/v1/search", json={"query": "आग रोधक तार", "language": "hi"})
    assert resp.status_code == 500
    assert resp.json()["detail"] == "translation_service_unavailable"


def test_search_day2_tests_still_pass_smoke():
    """Sanity check that language=en path is unaffected by Day 4's translation change.

    No live Qdrant/Postgres/Neo4j in this test environment, so the real
    search_standards() legitimately falls back to the documented empty/
    "fallback" shape rather than returning populated results — this
    asserts the fallback contract, not a specific result count.
    """
    resp = client.post("/api/v1/search", json={"query": "wire", "top_k": 3})
    assert resp.status_code == 200
    assert resp.json()["source"] == "qdrant_postgresql_neo4j"

def test_search_response_schema_fields_includes_needs_review():
    """Each search result includes needs_review alongside the existing contract fields."""
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
        "needs_review",
    ):
        assert field in result


def test_search_low_confidence_result_flagged_needs_review():
    """A result below the confidence threshold is marked needs_review, still returns 200."""
    low_confidence_result = _search_result(1)
    low_confidence_result["results"][0]["score"] = 0.10
    low_confidence_result["results"][0]["needs_review"] = True
    with patch(
        "src.orchestration.routers.search.search_standards",
        return_value=low_confidence_result,
    ):
        resp = client.post("/api/v1/search", json={"query": "wire"})
    assert resp.status_code == 200
    assert resp.json()["results"][0]["needs_review"] is True


def test_search_high_confidence_result_not_flagged():
    """A result at/above the confidence threshold is not marked needs_review."""
    with patch(
        "src.orchestration.routers.search.search_standards",
        return_value=_search_result(1),  # score=0.91 by default, no needs_review key -> defaults False
    ):
        resp = client.post("/api/v1/search", json={"query": "wire"})
    assert resp.json()["results"][0]["needs_review"] is False


def test_recommendation_fallback_flagged_needs_review():
    """A fallback (unverified) recommendation is marked needs_review."""
    fallback_result = {
        "item_id": "item-1",
        "standard_id": None,
        "original_spec": "some spec with no IS code",
        "ai_suggested_spec": "Verification required",
        "compliant": False,
        "mandatory_marks": [],
        "allied_standards": [],
        "source": "rules_engine",
        "status": "fallback",
        "needs_review": True,
    }
    with patch(
        "src.orchestration.routers.recommendation.recommendation_service",
        return_value=fallback_result,
    ):
        resp = client.post(
            "/api/v1/recommendation",
            json={"item_id": "item-1", "original_spec": "some spec with no IS code"},
        )
    assert resp.status_code == 200
    assert resp.json()["needs_review"] is True


def test_recommendation_verified_not_flagged():
    """A fully verified recommendation is not marked needs_review."""
    verified_result = {
        "item_id": "item-1",
        "standard_id": 1,
        "original_spec": "PVC Insulated Wires as per IS 694:1990",
        "ai_suggested_spec": "IS 694:2010 - PVC insulated cables",
        "compliant": True,
        "mandatory_marks": ["ISI mark"],
        "allied_standards": [],
        "source": "rules_engine",
        "needs_review": False,
    }
    with patch(
        "src.orchestration.routers.recommendation.recommendation_service",
        return_value=verified_result,
    ):
        resp = client.post(
            "/api/v1/recommendation",
            json={"item_id": "item-1", "original_spec": "PVC Insulated Wires as per IS 694:1990"},
        )
    assert resp.json()["needs_review"] is False
    
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


def test_orchestration_routes_registered():
    """The three orchestration endpoints (Dev 4's scope) are registered."""
    paths = collect_paths(app.routes)

    assert "/api/v1/search" in paths
    assert "/api/v1/recommendation" in paths
    assert "/api/v1/score" in paths


def test_backend_routes_registered():
    """RBAC/audit/compliance/review routers (Dev 1/Dev 2 scope) are mounted.

    [NEEDS TEAM CONFIRMATION] — src/backend/{audit,compliance_api,
    quality_score,review,verification}.py all exist in the repo but are
    not imported or app.include_router()'d in main.py.
    """
    paths = collect_paths(app.routes)

    assert "/audit/logs" in paths
    assert "/compliance/{standard_id}" in paths
    assert "/quality-score/{standard_id}" in paths
    assert "/review/queue" in paths
    assert "/verification/{standard_id}" in paths