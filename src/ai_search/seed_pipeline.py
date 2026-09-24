"""
Dev 3 — Day 2: Seed pipeline.
Pulls the standards Dev 2 seeded into PostgreSQL, runs spaCy NER for
technical entities, generates bge-m3 embeddings, and indexes everything
into Qdrant + BM25 so Feature 2/3 (search & recommendation) have real
data to query instead of mocks.

Run: python -m src.ai_search.seed_pipeline
"""
import logging

from src.ai_search.bm25_indexer import BM25Indexer
from src.ai_search.config import settings
from src.ai_search.document_parser import SpacyNERProcessor
from src.ai_search.embedding_pipeline import EmbeddingPipeline
from src.ai_search.qdrant_schema import QdrantConfig, QdrantSchemaManager

logger = logging.getLogger(__name__)


def _fetch_seeded_standards() -> list[dict]:
    """
    Read Dev 2's `standards` table and adapt field names to what
    EmbeddingPipeline.embed_standards expects (code/title/definition).

    Only a missing DB integration is treated as "nothing to do yet" (so this
    script can still be smoke-tested standalone before Dev 1/2's pieces are
    wired in). A failure while actually querying the database — bad
    connection, missing table, etc. — is a real error and is left to
    propagate rather than being reported as an empty, successful run.
    """
    try:
        from src.backend.database import SessionLocal
        from src.db_graph.models import Standard
    except ImportError as exc:
        logger.warning(
            "Backend DB modules not importable (%s); returning [] — "
            "pass `standards` explicitly or wire up src.backend.database "
            "and src.db_graph.models to seed from Postgres.",
            exc,
        )
        return []

    db = SessionLocal()
    try:
        rows = db.query(Standard).all()
    finally:
        db.close()

    missing_ids = [row.standard_number for row in rows if row.id is None]
    if missing_ids:
        raise ValueError(
            f"Standards missing a primary key id, cannot be indexed safely: {missing_ids}"
        )

    return [
        {
            "id": row.id,
            "code": row.standard_number,
            "title": row.title,
            "definition": row.description or "",
        }
        for row in rows
    ]


def run(standards: list[dict] | None = None) -> dict:
    """Extract entities, embed, and index a batch of standards end-to-end."""
    standards = standards if standards is not None else _fetch_seeded_standards()
    if not standards:
        logger.warning("No standards to seed — nothing to do.")
        return {"standards_processed": 0}

    missing_ids = [std.get("code", "<no code>") for std in standards if std.get("id") is None]
    if missing_ids:
        raise ValueError(
            f"Standards without an 'id' cannot be safely indexed (would collide "
            f"on fallback positional IDs): {missing_ids}"
        )

    # 1. spaCy NER over title+definition -> technical entities for the payload
    ner = SpacyNERProcessor(model_name=settings.spacy_model)
    entities_by_id = {
        std["id"]: ner.extract_technical_entities(
            f"{std.get('title', '')} {std.get('definition', '')}"
        )
        for std in standards
    }

    # 2. bge-m3 embeddings
    pipeline = EmbeddingPipeline(embedding_model_name=settings.embedding_model)
    embedded = pipeline.embed_standards(standards)

    # 3. Index into Qdrant — collection is created with the *actual* model
    #    dimension (pipeline.embedding_dim), not just the configured default,
    #    so a model/config drift can't silently produce a dimension mismatch.
    qdrant = QdrantSchemaManager(QdrantConfig(vector_size=pipeline.embedding_dim))
    qdrant.create_standards_collection()  # returns False (no-op) if it already exists

    points = [
        {
            "id": std["id"],
            "vector": emb["vector"],
            "payload": {
                "standard_code": emb["code"],
                "standard_title": emb["title"],
                "definition": emb["definition"],
                "entity_count": len(entities_by_id.get(std["id"], [])),
            },
        }
        for std, emb in zip(standards, embedded)
    ]
    inserted = qdrant.batch_insert_vectors(points)
    if inserted != len(points):
        raise RuntimeError(
            f"Qdrant insert incomplete: {inserted}/{len(points)} vectors indexed — "
            "check the collection's vector size matches the embedding model, and "
            "that Qdrant is reachable."
        )

    # 4. Index into BM25 for lexical search, using the *same* IDs as Qdrant so
    #    a downstream hybrid search can fuse results by doc_id. The index is
    #    persisted to disk (not just held in this process) so a separate
    #    search process can BM25Indexer().load_index(settings.bm25_index_path).
    bm25 = BM25Indexer(k1=settings.bm25_k1, b=settings.bm25_b)
    bm25.add_documents(
        [
            {
                "id": std["id"],
                "text": f"{std.get('code', '')} {std.get('title', '')} {std.get('definition', '')}",
                "metadata": {"standard_code": std.get("code")},
            }
            for std in standards
        ]
    )
    bm25_saved = bm25.save_index(settings.bm25_index_path)
    if not bm25_saved:
        logger.error(
            "BM25 index built (%s docs) but could not be saved to %s — "
            "downstream search will not see this run's data until it's persisted.",
            len(standards), settings.bm25_index_path,
        )

    logger.info(
        "Seed pipeline complete: %s standards embedded, %s vectors indexed in "
        "Qdrant, BM25 index built and saved=%s (%s).",
        len(standards), inserted, bm25_saved, settings.bm25_index_path,
    )
    return {
        "standards_processed": len(standards),
        "qdrant_vectors_inserted": inserted,
        "bm25_stats": bm25.get_stats(),
        "bm25_index_path": settings.bm25_index_path,
        "bm25_index_saved": bm25_saved,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(run())