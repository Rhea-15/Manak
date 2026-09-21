"""
Dev 3: Tests for BM25 Lexical Indexing
"""

import pytest
import tempfile
from pathlib import Path
from src.ai_search.bm25_indexer import BM25Indexer


class TestBM25Indexer:
    """Test BM25 lexical search"""

    def test_initialization(self):
        """Test BM25 indexer initialization"""
        indexer = BM25Indexer()
        assert indexer.k1 == 1.5
        assert indexer.b == 0.75
        assert indexer.bm25_model is None

    def test_custom_parameters(self):
        """Test custom BM25 parameters"""
        indexer = BM25Indexer(k1=2.0, b=0.5)
        assert indexer.k1 == 2.0
        assert indexer.b == 0.5

    def test_add_documents(self):
        """Test adding documents to index"""
        indexer = BM25Indexer()
        
        documents = [
            {
                "id": 1,
                "text": "IS 1554 fire-retardant copper wire electrical specification",
                "metadata": {"code": "IS 1554"}
            },
            {
                "id": 2,
                "text": "IS 694 electrical installation code safety requirements",
                "metadata": {"code": "IS 694"}
            },
            {
                "id": 3,
                "text": "IS 8542 cable sheathing materials testing procedure",
                "metadata": {"code": "IS 8542"}
            },
        ]
        
        indexer.add_documents(documents)
        
        assert len(indexer.documents) == 3
        assert indexer.bm25_model is not None
        stats = indexer.get_stats()
        assert stats["total_documents"] == 3

    def test_search_exact_match(self):
        """Test searching for exact matches"""
        indexer = BM25Indexer()
        
        documents = [
            {
                "id": 1,
                "text": "IS 1554 fire-retardant copper wire",
                "metadata": {"code": "IS 1554"}
            },
            {
                "id": 2,
                "text": "IS 694 electrical installation code",
                "metadata": {"code": "IS 694"}
            },
        ]
        
        indexer.add_documents(documents)
        results = indexer.search("IS 1554", top_k=10)
        
        assert len(results) > 0
        assert results[0]["doc_id"] == 1
        assert results[0]["score"] > 0

    def test_search_keyword_match(self):
        """Test searching by keywords"""
        indexer = BM25Indexer()
        
        documents = [
            {
                "id": 1,
                "text": "fire-retardant copper wire electrical specification",
                "metadata": {}
            },
            {
                "id": 2,
                "text": "copper pipe installation materials",
                "metadata": {}
            },
            {
                "id": 3,
                "text": "ceramic tile flooring options",
                "metadata": {}
            },
        ]
        
        indexer.add_documents(documents)
        results = indexer.search("copper", top_k=10)
        
        assert len(results) >= 2  # Should find docs 1 and 2
        doc_ids = [r["doc_id"] for r in results]
        assert 1 in doc_ids
        assert 2 in doc_ids

    def test_search_multiple_keywords(self):
        """Test searching with multiple keywords"""
        indexer = BM25Indexer()
        
        documents = [
            {
                "id": 1,
                "text": "fire-retardant copper wire electrical safety code",
                "metadata": {}
            },
            {
                "id": 2,
                "text": "fire safety building construction materials",
                "metadata": {}
            },
            {
                "id": 3,
                "text": "electrical wiring installation procedures",
                "metadata": {}
            },
        ]
        
        indexer.add_documents(documents)
        results = indexer.search("fire electrical", top_k=10)
        
        # Both docs contain relevant terms; BM25 ranks by relevance score
        assert len(results) >= 2
        doc_ids = [r["doc_id"] for r in results]
        assert 1 in doc_ids
        assert 2 in doc_ids
        # Just verify results are sorted by score
        if len(results) > 1:
            assert results[0]["score"] >= results[1]["score"]

    def test_search_no_results(self):
        """Test search with no matching results"""
        indexer = BM25Indexer()
        
        documents = [
            {
                "id": 1,
                "text": "copper wire electrical",
                "metadata": {}
            },
        ]
        
        indexer.add_documents(documents)
        results = indexer.search("nonexistent xyz abc", top_k=10)
        
        assert len(results) == 0

    def test_save_and_load_index(self):
        """Test saving and loading index"""
        indexer = BM25Indexer(k1=2.0, b=0.5)
        
        documents = [
            {"id": 1, "text": "IS 1554 copper wire", "metadata": {}},
            {"id": 2, "text": "IS 694 electrical code", "metadata": {}},
        ]
        
        indexer.add_documents(documents)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "bm25_index.json"
            
            # Save
            success = indexer.save_index(str(index_path))
            assert success
            assert index_path.exists()
            
            # Load
            indexer2 = BM25Indexer()
            success = indexer2.load_index(str(index_path))
            assert success
            assert indexer2.k1 == 2.0
            assert indexer2.b == 0.5
            assert len(indexer2.doc_metadata) == 2

    def test_get_stats(self):
        """Test getting indexing statistics"""
        indexer = BM25Indexer()
        
        documents = [
            {"id": i, "text": f"Document {i}", "metadata": {}}
            for i in range(5)
        ]
        
        indexer.add_documents(documents)
        stats = indexer.get_stats()
        
        assert stats["total_documents"] == 5
        assert stats["k1"] == 1.5
        assert stats["b"] == 0.75
        assert stats["model_initialized"] is True

    def test_search_top_k_limit(self):
        """Test that search respects top_k limit"""
        indexer = BM25Indexer()
        
        documents = [
            {"id": i, "text": f"copper document {i}", "metadata": {}}
            for i in range(10)
        ]
        
        indexer.add_documents(documents)
        results = indexer.search("copper", top_k=3)
        
        assert len(results) <= 3