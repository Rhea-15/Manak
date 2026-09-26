import hashlib
import threading
from typing import Any

from src.ai_search.embedding_pipeline import EmbeddingModel
from src.ai_search.qdrant_schema import QdrantConfig, QdrantSchemaManager
from src.backend.cache import cache_get, cache_set
from src.backend.compliance_rules import check_compliance_rules
from src.backend.database import SessionLocal
from src.db_graph.graph_service import get_standard_graph
from src.db_graph.models import Standard
import src.db_graph.versioning

_embedding_model = None
_qdrant = None


def run_with_timeout(
    func,
    *args,
    timeout_seconds: float = 2.0,
    fallback: Any = None,
    **kwargs,
):
    """Run a callable in a daemon thread and return a fallback on timeout."""
    result = {}
    error = None

    def target():
        nonlocal error

        try:
            result["value"] = func(*args, **kwargs)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            error = exc

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout_seconds)

    if thread.is_alive():
        return fallback

    if error is not None:
        if fallback is not None:
            return fallback
        raise error

    return result.get("value")


def get_search_dependencies():
    """Initialize and reuse the embedding model and Qdrant manager."""
    global _embedding_model, _qdrant

    if _embedding_model is None:
        _embedding_model = EmbeddingModel()

    if _qdrant is None:
        _qdrant = QdrantSchemaManager(QdrantConfig())

    return _embedding_model, _qdrant


def _empty_search_result(query: str, top_k: int = 5) -> dict:
    """Build an empty search response when a lookup cannot complete."""
    return {
        "query": query,
        "results": [],
        "vector_results_found": 0,
        "results_returned": 0,
        "source": "qdrant_postgresql_neo4j",
        "status": "fallback",
        "top_k": top_k,
    }


def _search_standards_impl(query: str, top_k: int = 5) -> dict:
    """Enrich vector matches with standard, compliance, and graph data."""
    embedding_model, qdrant = get_search_dependencies()

    query_vector = embedding_model.encode(query)

    vector_results = qdrant.search(
        query_vector=query_vector,
        limit=top_k,
    )

    results = []
    db = SessionLocal()

    try:
        for item in vector_results:
            payload = item.get("payload") or {}

            standard_number = (
                payload.get("standard_code")
                or payload.get("standard_number")
            )

            standard = None

            if standard_number:
                standard = (
                    db.query(Standard)
                    .filter(
                        Standard.standard_number == standard_number
                    )
                    .first()
                )

            if standard is None:
                continue

            active_version = src.db_graph.versioning.get_active_version(db, standard.id)
            compliance = check_compliance_rules(db, standard.id)
            graph = get_standard_graph(standard.standard_number)

            results.append(
                {
                    "standard_number": standard.standard_number,
                    "title": standard.title,
                    "score": item.get("score", 0.0),
                    "status": standard.status,
                    "active_version": (
                        active_version.version_number
                        if active_version
                        else None
                    ),
                    "compliance": compliance,
                    "graph": graph,
                }
            )
    finally:
        db.close()

    return {
        "query": query,
        "results": results,
        "vector_results_found": len(vector_results),
        "results_returned": len(results),
        "source": "qdrant_postgresql_neo4j",
    }


def search_standards(query: str, top_k: int = 5) -> dict:
    """Return Redis-cached search results or run a bounded lookup."""
    cache_key_hash = hashlib.sha256(
        f"{query.strip().lower()}:{top_k}".encode()
    ).hexdigest()

    cache_key = f"manak:search:{cache_key_hash}"

    cached_result = cache_get(cache_key)

    if cached_result is not None:
        return cached_result

    result = run_with_timeout(
        _search_standards_impl,
        query,
        top_k=top_k,
        timeout_seconds=2.0,
        fallback=_empty_search_result(query, top_k),
    )

    if result.get("status") != "fallback":
        cache_set(cache_key, result, ttl=60)

    return result
