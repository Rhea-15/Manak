"""
Dev 3: Hybrid Search with RRF (Reciprocal Rank Fusion)
Combines dense vector search with BM25 lexical search
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Single search result with ranking"""
    doc_id: int
    text: str
    vector_score: float = 0.0
    bm25_score: float = 0.0
    combined_score: float = 0.0
    rank: int = 0


class ReciprocalRankFusion:
    """RRF algorithm for combining multiple ranked lists"""

    def __init__(self, k: int = 60):
        """
        Initialize RRF.
        
        Args:
            k: Smoothing parameter (default: 60, range: 40-100)
               Prevents extreme scores and balances different ranking systems
        """
        if not (40 <= k <= 100):
            raise ValueError(f"Smoothing parameter 'k' must be between 40 and 100. Received: {k}")
            
        self.k = k
        self.logger = logging.getLogger(__name__)

    def fuse(
        self,
        vector_results: list[dict[str, float]],
        bm25_results: list[dict[str, float]],
    ) -> list[SearchResult]:
        """
        Fuse two ranked lists using RRF algorithm.
        
        RRF Formula: score = 1/(k + rank)
        - Documents in both lists get boosted
        - Documents in one list still ranked appropriately
        
        Args:
            vector_results: List of {"doc_id": int, "score": float, ...}
            bm25_results: List of {"doc_id": int, "score": float, ...}
        
        Returns:
            Fused and re-ranked results
        """
        # Build score maps from input results
        vector_scores = {r["doc_id"]: r.get("score", 0) for r in vector_results}
        bm25_scores = {r["doc_id"]: r.get("score", 0) for r in bm25_results}
        
        all_doc_ids = set(vector_scores.keys()) | set(bm25_scores.keys())
        
        # Calculate RRF scores
        rrf_scores = {}
        
        for doc_id in all_doc_ids:
            rrf_score = 0.0
            
            # Find rank in vector results (1-indexed)
            vector_rank = next(
                (i + 1 for i, r in enumerate(vector_results) if r["doc_id"] == doc_id),
                None,
            )
            if vector_rank is not None:
                rrf_score += 1.0 / (self.k + vector_rank)
            
            # Find rank in BM25 results (1-indexed)
            bm25_rank = next(
                (i + 1 for i, r in enumerate(bm25_results) if r["doc_id"] == doc_id),
                None,
            )
            if bm25_rank is not None:
                rrf_score += 1.0 / (self.k + bm25_rank)
            
            rrf_scores[doc_id] = rrf_score
        
        # Sort by RRF score (descending)
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build results
        results = []
        for rank, (doc_id, combined_score) in enumerate(sorted_docs, 1):
            result = SearchResult(
                doc_id=doc_id,
                text="",  # Placeholder, populated from actual documents
                vector_score=vector_scores.get(doc_id, 0.0),
                bm25_score=bm25_scores.get(doc_id, 0.0),
                combined_score=combined_score,
                rank=rank,
            )
            results.append(result)
        
        self.logger.debug(
            f"RRF fused {len(vector_results)} vector + {len(bm25_results)} BM25 results → {len(results)} final"
        )
        return results


class HybridSearchEngine:
    """Orchestrate hybrid vector + lexical search"""

    def __init__(self, vector_weight: float = 0.5, bm25_weight: float = 0.5):
        """
        Initialize hybrid engine.
        
        Args:
            vector_weight: Weight for vector search (0.0-1.0)
            bm25_weight: Weight for BM25 search (0.0-1.0)
        """
        if not (0 <= vector_weight <= 1 and 0 <= bm25_weight <= 1):
            raise ValueError("Weights must be between 0 and 1")
        
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.rrf = ReciprocalRankFusion()
        self.logger = logging.getLogger(__name__)

    def search_rrf(
        self,
        query: str,
        vector_results: list[dict],
        bm25_results: list[dict],
        top_k: int = 10,
    ) -> list[SearchResult]:
        """
        Perform hybrid search using RRF fusion.
        
        Args:
            query: Search query (for logging)
            vector_results: Results from dense vector search
            bm25_results: Results from BM25 search
            top_k: Number of top results to return
        
        Returns:
            Fused and ranked results
        """
        if top_k < 0:
            return []

        # Use RRF to fuse results
        fused_results = self.rrf.fuse(vector_results, bm25_results)
        
        # Return top-k
        return fused_results[:top_k]

    def search_weighted(
        self,
        query: str,
        vector_results: list[dict],
        bm25_results: list[dict],
        top_k: int = 10,
    ) -> list[SearchResult]:
        """
        Perform hybrid search using weighted combination.
        
        Alternative to RRF: normalize scores and weight them.
        
        Args:
            query: Search query
            vector_results: Results from vector search
            bm25_results: Results from BM25 search
            top_k: Number of top results
        
        Returns:
            Weighted and ranked results
        """
        if top_k < 0:
            return []

        # Helper for range-aware normalization
        def _normalize(results: list[dict]) -> dict[int, float]:
            if not results:
                return {}
            scores = [r.get("score", 0.0) for r in results]
            min_score, max_score = min(scores), max(scores)
            
            # Neutral normalization if all scores are identical
            if min_score == max_score:
                neutral = 1.0 if max_score > 0 else 0.0
                return {r["doc_id"]: neutral for r in results}
                
            return {
                r["doc_id"]: (r.get("score", 0.0) - min_score) / (max_score - min_score)
                for r in results
            }

        vector_normalized = _normalize(vector_results)
        bm25_normalized = _normalize(bm25_results)
        
        all_doc_ids = set(vector_normalized.keys()) | set(bm25_normalized.keys())
        
        # Weighted combination
        combined_scores = {}
        for doc_id in all_doc_ids:
            vector_score = vector_normalized.get(doc_id, 0.0)
            bm25_score = bm25_normalized.get(doc_id, 0.0)
            combined = (vector_score * self.vector_weight) + (bm25_score * self.bm25_weight)
            combined_scores[doc_id] = combined
        
        # Sort and build results
        sorted_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for rank, (doc_id, score) in enumerate(sorted_docs[:top_k], 1):
            results.append(SearchResult(
                doc_id=doc_id,
                text="",
                vector_score=vector_normalized.get(doc_id, 0.0),
                bm25_score=bm25_normalized.get(doc_id, 0.0),
                combined_score=score,
                rank=rank,
            ))
        
        return results

    def get_config(self) -> dict:
        """Get current hybrid search configuration"""
        return {
            "vector_weight": self.vector_weight,
            "bm25_weight": self.bm25_weight,
            "fusion_method": "rrf",  # or "weighted"
            "rrf_k": self.rrf.k,
        }