"""
Dev 3: Tests for the Day 2 seed pipeline (end-to-end wiring).
"""
from unittest.mock import MagicMock, patch

import numpy as np


@patch("src.ai_search.seed_pipeline.BM25Indexer")
@patch("src.ai_search.seed_pipeline.QdrantSchemaManager")
@patch("src.ai_search.seed_pipeline.EmbeddingPipeline")
@patch("src.ai_search.seed_pipeline.SpacyNERProcessor")
def test_run_with_explicit_standards(mock_ner_cls, mock_pipeline_cls, mock_qdrant_cls, mock_bm25_cls):
    from src.ai_search.seed_pipeline import run

    mock_ner_cls.return_value.extract_technical_entities.return_value = []

    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.embed_standards.return_value = [
        {"code": "IS 1554", "title": "Fire-retardant wires", "definition": "...", "vector": [0.1] * 4}
    ]

    mock_qdrant = mock_qdrant_cls.return_value
    mock_qdrant.create_standards_collection.return_value = True
    mock_qdrant.batch_insert_vectors.return_value = 1

    mock_bm25 = mock_bm25_cls.return_value
    mock_bm25.get_stats.return_value = {"total_documents": 1}

    standards = [{"id": 1, "code": "IS 1554", "title": "Fire-retardant wires", "definition": "..."}]
    result = run(standards)

    assert result["standards_processed"] == 1
    assert result["qdrant_vectors_inserted"] == 1
    mock_qdrant.batch_insert_vectors.assert_called_once()
    mock_bm25.add_documents.assert_called_once()


def test_run_with_no_standards_returns_early():
    from src.ai_search.seed_pipeline import run

    result = run(standards=[])
    assert result == {"standards_processed": 0}