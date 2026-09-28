import json
from unittest.mock import patch
import time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.database import Base
from src.orchestration.services import confidence


def _make_session_factory():
    """In-memory SQLite engine + schema, matching tests/backend/test_audit.py."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)


# ---------------------------------------------------------------------------
# apply_confidence_gate (search) -- pure marking
# ---------------------------------------------------------------------------

def test_score_above_threshold_not_flagged():
    results = [{"standard_number": "IS 1", "score": 0.95}]
    gated = confidence.apply_confidence_gate(results, threshold=0.62)
    assert gated[0]["needs_review"] is False


def test_score_below_threshold_flagged():
    results = [{"standard_number": "IS 2", "score": 0.40}]
    gated = confidence.apply_confidence_gate(results, threshold=0.62)
    assert gated[0]["needs_review"] is True


def test_score_exactly_at_threshold_is_high_confidence():
    """The boundary itself passes: score >= threshold is treated as confident."""
    results = [{"standard_number": "IS 3", "score": 0.62}]
    gated = confidence.apply_confidence_gate(results, threshold=0.62)
    assert gated[0]["needs_review"] is False


def test_missing_score_flagged_for_review():
    results = [{"standard_number": "IS 4"}]  # no "score" key at all
    gated = confidence.apply_confidence_gate(results, threshold=0.62)
    assert gated[0]["needs_review"] is True


def test_invalid_score_types_flagged_for_review():
    for bad_score in (None, "high", float("nan"), -0.1, 1.5, True):
        results = [{"standard_number": "IS 5", "score": bad_score}]
        gated = confidence.apply_confidence_gate(results, threshold=0.62)
        assert gated[0]["needs_review"] is True, f"score={bad_score!r} should flag"


def test_empty_results_list_returns_empty_list():
    assert confidence.apply_confidence_gate([], threshold=0.62) == []


# ---------------------------------------------------------------------------
# flag_low_confidence_search_results -- persistence, non-blocking guarantee
# ---------------------------------------------------------------------------

def test_flag_low_confidence_search_results_calls_create_review_item():
    results = [
        {"standard_number": "IS 1", "score": 0.95, "needs_review": False},
        {"standard_number": "IS 2", "score": 0.40, "needs_review": True},
    ]
    with patch.object(confidence, "create_review_item") as mock_create:
        confidence.flag_low_confidence_search_results(results, query="wire")
    mock_create.assert_called_once()
    _, kwargs = mock_create.call_args
    assert kwargs["source"] == "search"
    assert kwargs["context"]["standard_number"] == "IS 2"


def test_flag_low_confidence_search_results_never_raises_on_broken_contract():
    """Defense-in-depth: even if create_review_item violates its own
    no-raise contract, the caller (search_standards) must never see it."""
    results = [{"standard_number": "IS 6", "score": 0.10, "needs_review": True}]
    with patch.object(confidence, "create_review_item", side_effect=RuntimeError("boom")):
        confidence.flag_low_confidence_search_results(results, query="wire")  # must not raise


# ---------------------------------------------------------------------------
# evaluate_recommendation_confidence / flag_low_confidence_recommendation
# ---------------------------------------------------------------------------

def test_recommendation_fallback_status_flagged():
    result = {"item_id": "item-1", "status": "fallback", "compliant": False}
    out = confidence.evaluate_recommendation_confidence(result)
    assert out["needs_review"] is True


def test_recommendation_non_compliant_flagged():
    result = {"item_id": "item-2", "compliant": False}
    out = confidence.evaluate_recommendation_confidence(result)
    assert out["needs_review"] is True


def test_recommendation_verified_compliant_not_flagged():
    result = {"item_id": "item-3", "compliant": True}
    out = confidence.evaluate_recommendation_confidence(result)
    assert out["needs_review"] is False


def test_flag_low_confidence_recommendation_calls_create_review_item():
    result = {"item_id": "item-4", "needs_review": True, "status": "fallback"}
    with patch.object(confidence, "create_review_item") as mock_create:
        confidence.flag_low_confidence_recommendation(result)
    mock_create.assert_called_once()
    assert mock_create.call_args.kwargs["source"] == "recommendation"


def test_flag_low_confidence_recommendation_skips_when_not_flagged():
    result = {"item_id": "item-5", "needs_review": False}
    with patch.object(confidence, "create_review_item") as mock_create:
        confidence.flag_low_confidence_recommendation(result)
    mock_create.assert_not_called()


def test_flag_low_confidence_recommendation_never_raises_on_broken_contract():
    result = {"item_id": "item-6", "needs_review": True}
    with patch.object(confidence, "create_review_item", side_effect=RuntimeError("boom")):
        confidence.flag_low_confidence_recommendation(result)  # must not raise


# ---------------------------------------------------------------------------
# create_review_item -- real DB, matching tests/backend/test_audit.py's convention
# ---------------------------------------------------------------------------

def test_create_review_item_writes_expected_row():
    factory = _make_session_factory()

    with patch.object(confidence, "SessionLocal", factory):
        ok = confidence.create_review_item(
            source="search",
            context={
                "query": "fireproof wire",
                "standard_number": "IS 694:1990",
                "score": 0.4,
                "threshold": 0.62,
            },
        )

    assert ok is True

    session = factory()
    rows = session.query(confidence.ReviewQueue).all()
    assert len(rows) == 1

    row = rows[0]
    assert row.status == "pending"
    assert row.submitted_by == "system:confidence_firewall"
    assert row.document_name == "search:fireproof wire"

    notes = json.loads(row.review_notes)
    assert notes["source"] == "search"
    assert notes["standard_number"] == "IS 694:1990"
    assert notes["score"] == 0.4
    assert notes["threshold"] == 0.62


def test_create_review_item_db_failure_is_caught_not_raised():
    """A DB error must be swallowed -- the caller must never see it."""

    class _BrokenSessionLocal:
        def __call__(self):
            raise RuntimeError("database unavailable")

    with patch.object(confidence, "SessionLocal", _BrokenSessionLocal()):
        ok = confidence.create_review_item(source="search", context={"query": "x"})

    assert ok is False


# ---------------------------------------------------------------------------
# CONFIDENCE_THRESHOLD env handling
# ---------------------------------------------------------------------------

def test_env_float_default_when_unset(monkeypatch):
    monkeypatch.delenv("CONFIDENCE_THRESHOLD", raising=False)
    assert confidence._env_float("CONFIDENCE_THRESHOLD", 0.62) == 0.62


def test_env_float_respects_valid_override(monkeypatch):
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.75")
    assert confidence._env_float("CONFIDENCE_THRESHOLD", 0.62) == 0.75


def test_env_float_raises_on_malformed_value(monkeypatch):
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "not-a-float")
    with pytest.raises(ValueError):
        confidence._env_float("CONFIDENCE_THRESHOLD", 0.62)

def test_flag_recommendation_does_not_block_when_persistence_hangs(monkeypatch):
    monkeypatch.setattr(confidence, "PERSIST_TIMEOUT_SECONDS", 0.05)
    with patch.object(confidence, "create_review_item", side_effect=lambda **k: time.sleep(2)):
        start = time.perf_counter()
        confidence.flag_low_confidence_recommendation({"item_id": "x", "needs_review": True})
    assert time.perf_counter() - start < 0.5