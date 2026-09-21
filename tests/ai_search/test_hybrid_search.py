"""
Dev 3: Tests for Hybrid Search and RRF
"""

import pytest
from src.ai_search.hybrid_search import (
    ReciprocalRankFusion,
    HybridSearchEngine,
    SearchResult,
)


class TestReciprocalRankFusion:
    """Test RRF algorithm"""

    def test_initialization(self):
        """Test RRF initialization"""
        rrf = ReciprocalRankFusion(k=60)
        assert rrf.k == 60

    def test_custom_k(self):
        """Test RRF with custom k parameter"""
        rrf = ReciprocalRankFusion(k=100)
        assert rrf.k == 100

    def test_rrf_fusion(self):
        """Test RRF fusion of two ranked lists"""
        rrf = ReciprocalRankFusion(k=60)
        
        vector_results = [
            {"doc_id": 1, "score": 0.95},
            {"doc_id": 2, "score": 0.87},
            {"doc_id": 3, "score": 0.75},
        ]
        
        bm25_results = [
            {"doc_id": 3, "score": 0.92},
            {"doc_id": 1, "score": 0.88},
            {"doc_id": 4, "score": 0.78},
        ]
        
        fused = rrf.fuse(vector_results, bm25_results)
        
        assert len(fused) == 4  # All unique doc_ids
        assert all(isinstance(r, SearchResult) for r in fused)
        assert fused[0].rank == 1
        assert fused[-1].rank == 4
        
        # Doc 1 appears in both, should rank high
        doc_1 = next(r for r in fused if r.doc_id == 1)
        doc_4 = next(r for r in fused if r.doc_id == 4)
        assert doc_1.combined_score > doc_4.combined_score

    def test_rrf_single_list(self):
        """Test RRF with one empty list"""
        rrf = ReciprocalRankFusion()
        
        results = rrf.fuse(
            [{"doc_id": 1, "score": 0.9}],
            []
        )
        
        assert len(results) == 1
        assert results[0].doc_id == 1

    def test_rrf_ranking_order(self):
        """Test that RRF maintains proper ranking order"""
        rrf = ReciprocalRankFusion(k=60)
        
        vector_results = [
            {"doc_id": i, "score": 1.0 - i * 0.1}
            for i in range(5)
        ]
        
        bm25_results = [
            {"doc_id": i, "score": 1.0 - i * 0.1}
            for i in range(5)
        ]
        
        fused = rrf.fuse(vector_results, bm25_results)
        
        # Verify ranking is in order
        for i, result in enumerate(fused):
            assert result.rank == i + 1
            if i > 0:
                assert fused[i-1].combined_score >= result.combined_score


class TestHybridSearchEngine:
    """Test hybrid search orchestration"""

    def test_initialization(self):
        """Test engine initialization"""
        engine = HybridSearchEngine(vector_weight=0.6, bm25_weight=0.4)
        
        assert engine.vector_weight == 0.6
        assert engine.bm25_weight == 0.4

    def test_invalid_weights(self):
        """Test that invalid weights raise error"""
        with pytest.raises(ValueError):
            HybridSearchEngine(vector_weight=1.5, bm25_weight=0.4)
        
        with pytest.raises(ValueError):
            HybridSearchEngine(vector_weight=0.6, bm25_weight=-0.1)

    def test_search_rrf(self):
        """Test hybrid search with RRF"""
        engine = HybridSearchEngine()
        
        vector_results = [
            {"doc_id": 1, "score": 0.95},
            {"doc_id": 2, "score": 0.80},
        ]
        
        bm25_results = [
            {"doc_id": 2, "score": 0.90},
            {"doc_id": 1, "score": 0.75},
        ]
        
        results = engine.search_rrf("query", vector_results, bm25_results, top_k=2)
        
        assert len(results) <= 2
        assert all(isinstance(r, SearchResult) for r in results)

    def test_search_weighted(self):
        """Test hybrid search with weighted combination"""
        engine = HybridSearchEngine(vector_weight=0.7, bm25_weight=0.3)
        
        vector_results = [{"doc_id": 1, "score": 1.0}]
        bm25_results = [{"doc_id": 2, "score": 1.0}]
        
        results = engine.search_weighted("query", vector_results, bm25_results, top_k=2)
        
        assert len(results) == 2
        doc_ids = {r.doc_id for r in results}
        assert doc_ids == {1, 2}

    def test_get_config(self):
        """Test getting engine configuration"""
        engine = HybridSearchEngine(vector_weight=0.6, bm25_weight=0.4)
        config = engine.get_config()
        
        assert config["vector_weight"] == 0.6
        assert config["bm25_weight"] == 0.4
        assert config["fusion_method"] == "rrf"

    def test_search_result_scores(self):
        """Test that search results track individual scores"""
        engine = HybridSearchEngine()
        
        vector_results = [
            {"doc_id": 1, "score": 0.95},
        ]
        
        bm25_results = [
            {"doc_id": 1, "score": 0.85},
        ]
        
        results = engine.search_rrf("query", vector_results, bm25_results, top_k=1)
        
        assert results[0].vector_score == 0.95
        assert results[0].bm25_score == 0.85
        assert results[0].combined_score > 0

    def test_empty_results(self):
        """Test hybrid search with empty inputs"""
        engine = HybridSearchEngine()
        
        results = engine.search_rrf("query", [], [], top_k=10)
        
        assert len(results) == 0