"""
Dev 3: Tests for the Day 2 seed pipeline (end-to-end wiring).
"""
import pytest
from unittest.mock import MagicMock, patch


@patch("src.ai_search.seed_pipeline.BM25Indexer")
@patch("src.ai_search.seed_pipeline.QdrantSchemaManager")
@patch("src.ai_search.seed_pipeline.EmbeddingPipeline")
@patch("src.ai_search.seed_pipeline.SpacyNERProcessor")
def test_run_with_explicit_standards(mock_ner_cls, mock_pipeline_cls, mock_qdrant_cls, mock_bm25_cls):
    from src.ai_search.seed_pipeline import run

    mock_ner_cls.return_value.extract_technical_entities.return_value = []

    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.embedding_dim = 4
    mock_pipeline.embed_standards.return_value = [
        {"code": "IS 1554", "title": "Fire-retardant wires", "definition": "...", "vector": [0.1] * 4}
    ]

    mock_qdrant = mock_qdrant_cls.return_value
    mock_qdrant.create_standards_collection.return_value = True
    mock_qdrant.batch_insert_vectors.return_value = 1

    mock_bm25 = mock_bm25_cls.return_value
    mock_bm25.get_stats.return_value = {"total_documents": 1}
    mock_bm25.save_index.return_value = True

    standards = [{"id": 1, "code": "IS 1554", "title": "Fire-retardant wires", "definition": "..."}]
    result = run(standards)

    assert result["standards_processed"] == 1
    assert result["qdrant_vectors_inserted"] == 1
    assert result["bm25_index_saved"] is True
    mock_qdrant.batch_insert_vectors.assert_called_once()
    mock_bm25.add_documents.assert_called_once()
    mock_bm25.save_index.assert_called_once()


def test_run_with_no_standards_returns_early():
    from src.ai_search.seed_pipeline import run

    result = run(standards=[])
    assert result == {"standards_processed": 0}


def test_run_rejects_standards_missing_id():
    from src.ai_search.seed_pipeline import run

    standards = [{"code": "IS 1554", "title": "Fire-retardant wires", "definition": "..."}]  # no "id"
    with pytest.raises(ValueError, match="without an 'id'"):
        run(standards)


@patch("src.ai_search.seed_pipeline.BM25Indexer")
@patch("src.ai_search.seed_pipeline.QdrantSchemaManager")
@patch("src.ai_search.seed_pipeline.EmbeddingPipeline")
@patch("src.ai_search.seed_pipeline.SpacyNERProcessor")
def test_run_raises_on_partial_qdrant_insert(mock_ner_cls, mock_pipeline_cls, mock_qdrant_cls, mock_bm25_cls):
    from src.ai_search.seed_pipeline import run

    mock_ner_cls.return_value.extract_technical_entities.return_value = []

    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.embedding_dim = 4
    mock_pipeline.embed_standards.return_value = [
        {"code": "IS 1554", "title": "t1", "definition": "d1", "vector": [0.1] * 4},
        {"code": "IS 694", "title": "t2", "definition": "d2", "vector": [0.2] * 4},
    ]

    mock_qdrant = mock_qdrant_cls.return_value
    mock_qdrant.batch_insert_vectors.return_value = 1  # only 1 of 2 inserted

    standards = [
        {"id": 1, "code": "IS 1554", "title": "t1", "definition": "d1"},
        {"id": 2, "code": "IS 694", "title": "t2", "definition": "d2"},
    ]

    with pytest.raises(RuntimeError, match="Qdrant insert incomplete"):
        run(standards)