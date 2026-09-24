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
    Returns [] with a warning if the DB isn't reachable yet, so this
    script can still be smoke-tested standalone before Dev 1/2 finish
    their pieces.
    """
    try:
        from src.backend.database import SessionLocal
        from src.db_graph.models import Standard
    except ImportError as exc:
        logger.warning("Backend DB modules not importable (%s); returning []", exc)
        return []

    db = SessionLocal()
    try:
        rows = db.query(Standard).all()
    finally:
        db.close()

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

    # 1. spaCy NER over title+definition -> technical entities for the payload
    ner = SpacyNERProcessor(model_name=settings.spacy_model)
    entities_by_code = {
        std["code"]: ner.extract_technical_entities(
            f"{std.get('title', '')} {std.get('definition', '')}"
        )
        for std in standards
    }

    # 2. bge-m3 embeddings
    pipeline = EmbeddingPipeline(embedding_model_name=settings.embedding_model)
    embedded = pipeline.embed_standards(standards)

    # 3. Index into Qdrant
    qdrant = QdrantSchemaManager(QdrantConfig())
    qdrant.create_standards_collection()  # returns False (no-op) if it already exists

    points = [
        {
            "id": std.get("id", i),
            "vector": emb["vector"],
            "payload": {
                "standard_code": emb["code"],
                "standard_title": emb["title"],
                "definition": emb["definition"],
                "entity_count": len(entities_by_code.get(emb["code"], [])),
            },
        }
        for i, (std, emb) in enumerate(zip(standards, embedded))
    ]
    inserted = qdrant.batch_insert_vectors(points)

    # 4. Index into BM25 for lexical search
    bm25 = BM25Indexer(k1=settings.bm25_k1, b=settings.bm25_b)
    bm25.add_documents(
        [
            {
                "id": std.get("id", i),
                "text": f"{std.get('code', '')} {std.get('title', '')} {std.get('definition', '')}",
                "metadata": {"standard_code": std.get("code")},
            }
            for i, std in enumerate(standards)
        ]
    )

    logger.info(
        "Seed pipeline complete: %s standards embedded, %s vectors indexed in Qdrant, BM25 index built.",
        len(standards), inserted,
    )
    return {
        "standards_processed": len(standards),
        "qdrant_vectors_inserted": inserted,
        "bm25_stats": bm25.get_stats(),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(run())