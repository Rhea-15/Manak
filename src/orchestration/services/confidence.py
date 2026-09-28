"""Confidence threshold gate for search and recommendation results.

Flags low-confidence matches with `needs_review` and best-effort logs
them to the existing ReviewQueue for human review. Marking (pure,
cheap) and persistence (I/O, best-effort) are deliberately separate
functions -- see search_service.py / recommendation_service.py for how
they're sequenced, and why persistence always runs outside any
timeout-bounded or cached code path.

Threshold notes:
- CONFIDENCE_THRESHOLD is calibrated for Qdrant's raw cosine similarity
  score ([0, 1]) -- the only score search_service.py actually produces
  today. If Reciprocal Rank Fusion (src/ai_search/hybrid_search.py) is
  ever wired into search_service.py, this threshold is meaningless
  against RRF's much smaller (~0-0.033) scale and must be re-tuned,
  not reused as-is.
- 0.62 is the technical blueprint's illustrative "empirically tuned"
  value. It has NOT been verified against real Qdrant score
  distributions on this project's actual corpus/embedding model.
  Treat it as a provisional default pending team sign-off on real
  score data, not a final number.
"""

import json
import logging
import os
import threading

from src.backend.audit import create_audit_log
from src.backend.database import SessionLocal
from src.db_graph.models import ReviewQueue

logger = logging.getLogger(__name__)


def _env_float(key: str, default: float) -> float:
    """Read a float from the environment, matching AISearchSettings' pattern.

    Fails fast (at import time) on a malformed value rather than
    silently falling back or failing per-request later.
    """
    raw = os.getenv(key)
    if raw is None:
        return default
    return float(raw)  # intentionally uncaught -- fail fast at startup


CONFIDENCE_THRESHOLD = _env_float("CONFIDENCE_THRESHOLD", 0.62)

# Upper bound on how long a request may wait for ReviewQueue persistence.
# Postgres being down or hanging must degrade only the audit trail, never
# the user-facing response time.
PERSIST_TIMEOUT_SECONDS = _env_float("CONFIDENCE_PERSIST_TIMEOUT", 0.75)


def _run_bounded(func, *args) -> bool:
    """Run func in a daemon thread and wait at most PERSIST_TIMEOUT_SECONDS.

    Returns True if it finished in time. On timeout the thread is left to
    finish (or fail) in the background and the caller moves on. func must
    handle its own exceptions; this helper never raises.
    """
    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start()
    thread.join(PERSIST_TIMEOUT_SECONDS)

    if thread.is_alive():
        logger.warning(
            "confidence gate: ReviewQueue write exceeded %.2fs; continuing without waiting",
            PERSIST_TIMEOUT_SECONDS,
        )
        return False

    return True


def _is_valid_score(score) -> bool:
    """Return True only for a real, in-range numeric score.

    Excludes bool explicitly (bool is a subclass of int in Python, so
    `True`/`False` would otherwise pass as 1.0/0.0). NaN is rejected
    naturally: any comparison against NaN is False.
    """
    if isinstance(score, bool):
        return False
    if not isinstance(score, (int, float)):
        return False
    return 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# Search: pure marking, then separate best-effort persistence
# ---------------------------------------------------------------------------

def apply_confidence_gate(
    results: list[dict],
    threshold: float = CONFIDENCE_THRESHOLD,
) -> list[dict]:
    """Mark each search result's `needs_review` flag. Pure -- no I/O, no DB.

    Fails toward caution: a missing or invalid score is treated as
    needing review, never silently trusted. Safe to call inside a
    timeout-bounded or cached code path.
    """
    for result in results:
        score = result.get("score")

        if not _is_valid_score(score):
            result["needs_review"] = True
            logger.warning(
                "confidence gate: missing/invalid score for standard_number=%s",
                result.get("standard_number"),
            )
        elif score < threshold:
            result["needs_review"] = True
        else:
            result["needs_review"] = False

    return results


def flag_low_confidence_search_results(
    results: list[dict],
    query: str | None = None,
    threshold: float = CONFIDENCE_THRESHOLD,
) -> None:
    """Best-effort ReviewQueue write for every already-marked low-confidence result.

    Call this AFTER any timeout-bounded work and cache write have
    already completed -- persistence here must never risk pushing a
    search over its own timeout budget or blocking a cache hit.
    Never raises.
    """
    def _flag_all() -> None:
        for result in results:
            if not result.get("needs_review"):
                continue

            try:
                create_review_item(
                    source="search",
                    context={
                        "query": query,
                        "standard_number": result.get("standard_number"),
                        "score": result.get("score"),
                        "threshold": threshold,
                    },
                )
            except Exception:  # noqa: BLE001 -- persistence must never break search
                logger.exception(
                    "confidence gate: unexpected error flagging standard_number=%s",
                    result.get("standard_number"),
                )

    if any(r.get("needs_review") for r in results):
        _run_bounded(_flag_all)


# ---------------------------------------------------------------------------
# Recommendation: no numeric score exists today -- gate on the existing
# fallback/compliance signal instead of fabricating one.
# ---------------------------------------------------------------------------

def evaluate_recommendation_confidence(result: dict) -> dict:
    """Mark `needs_review` from the existing fallback/compliance signal. Pure.

    Recommendation has no numeric confidence score today -- its only
    signal is the existing fallback trigger (status == "fallback",
    i.e. no IS code matched or no standard found) or a verified-but-
    non-compliant result. This treats that binary signal as the
    low-confidence case rather than inventing a fake numeric score.
    """
    is_low_confidence = (
        result.get("status") == "fallback"
        or not result.get("compliant", True)
    )
    result["needs_review"] = bool(is_low_confidence)
    return result


def flag_low_confidence_recommendation(result: dict) -> None:
    """Best-effort ReviewQueue write if the recommendation needs review.

    Call this AFTER the timeout-bounded recommendation lookup has
    already completed. Never raises.
    """
    if not result.get("needs_review"):
        return

    def _flag() -> None:
        try:
            create_review_item(
                source="recommendation",
                context={
                    "item_id": result.get("item_id"),
                    "standard_id": result.get("standard_id"),
                    "status": result.get("status"),
                    "compliant": result.get("compliant"),
                },
            )
        except Exception:  # noqa: BLE001 -- persistence must never break recommendation
            logger.exception(
                "confidence gate: unexpected error flagging item_id=%s",
                result.get("item_id"),
            )

    _run_bounded(_flag)


# ---------------------------------------------------------------------------
# Shared ReviewQueue writer -- reuse, no schema change (see PR notes)
# ---------------------------------------------------------------------------

def create_review_item(source: str, context: dict) -> bool:
    """Best-effort insert a ReviewQueue row describing a low-confidence match.

    No ReviewQueue/Postgres schema change: the score/threshold/query
    context that has no dedicated column is serialized into the
    existing `review_notes` text column as JSON.

    Never raises. Returns False (and logs) on any failure, so a
    Postgres hiccup degrades only the audit trail, never the
    user-facing search/recommendation response.
    """
    db = None

    try:
        db = SessionLocal()

        label = context.get("query") or context.get("item_id") or "unknown"

        review_item = ReviewQueue(
            document_name=f"{source}:{label}",
            document_path=None,
            status="pending",
            submitted_by="system:confidence_firewall",
            reviewed_by=None,
            review_notes=json.dumps({"source": source, **context}, default=str),
        )

        db.add(review_item)
        db.commit()

        try:
            create_audit_log(
                user_id="system:confidence_firewall",
                endpoint=f"/api/v1/{source}",
                action="FLAGGED_LOW_CONFIDENCE",
                details=json.dumps({"source": source, **context}, default=str),
                db=db,
            )
        except Exception:  # noqa: BLE001 -- audit logging must never break the gate
            logger.exception(
                "confidence gate: failed to write audit log for %s review item",
                source,
            )

        return True

    except Exception:  # noqa: BLE001 -- persistence must never break the caller
        logger.exception(
            "confidence gate: failed to create ReviewQueue item for source=%s",
            source,
        )
        return False

    finally:
        if db is not None:
            db.close()