"""
Dev 3: BM25 Lexical Search Index
Provides exact keyword matching complementary to dense vectors
"""

import json
import logging

try:
    from rank_bm25 import BM25Plus
except ImportError:
    BM25Plus = None

logger = logging.getLogger(__name__)


class BM25Indexer:
    """BM25 lexical search implementation for exact keyword matching"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 indexer using BM25Plus to ensure positive IDF scores.
        
        Args:
            k1: Controls term frequency saturation (default 1.5)
            b: Controls length normalization (default 0.75)
        """
        self.logger = logging.getLogger(__name__)
        if not BM25Plus:
            self.logger.error("rank_bm25 not installed. Install with: pip install rank-bm25")
            raise RuntimeError("rank_bm25 required")
        
        self.documents: list[list[str]] = []
        self.doc_metadata: list[dict] = []
        self.bm25_model: BM25Plus = None
        self.k1 = k1
        self.b = b

    def _tokenize(self, text: str) -> list[str]:
        """
        Tokenize text for BM25.
        Converts to lowercase and splits by whitespace.
        """
        return text.lower().split()

    def add_documents(self, documents: list[dict[str, str]]) -> None:
        """
        Add documents to BM25 index.
        
        Args:
            documents: List of {"text": str, "id": int, "metadata": {...}}
        """
        self.documents = []
        self.doc_metadata = []
        
        for doc in documents:
            text = doc.get("text", "")
            tokenized = self._tokenize(text)
            
            self.documents.append(tokenized)
            self.doc_metadata.append({
                "id": doc.get("id"),
                "text_preview": text[:200],
                "metadata": doc.get("metadata", {}),
            })
        
        self.bm25_model = BM25Plus(self.documents, k1=self.k1, b=self.b)
        self.logger.info(f"Indexed {len(self.documents)} documents with BM25")

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Search documents using BM25.
        
        Args:
            query: Query text
            top_k: Number of top results to return
        
        Returns:
            List of {"doc_id": int, "score": float, "text_preview": str, "metadata": {}}
        """
        if not self.bm25_model or not self.documents:
            self.logger.error("BM25 model not initialized or empty")
            return []
        
        tokenized_query = self._tokenize(query)
        scores = self.bm25_model.get_scores(tokenized_query)
        
        # Debug: print scores with doc info
        for i, score in enumerate(scores):
            doc_id = self.doc_metadata[i]["id"]
            print(f"Doc {doc_id}: score={score}, text={self.doc_metadata[i]['text_preview']}")
        
        # Primary sort: BM25 score (descending)
        # Secondary sort: original insertion order (ascending = earlier docs first)
        sorted_indices = sorted(
            range(len(scores)),
            key=lambda i: (-scores[i], i),
        )
        
        results = []
        for idx in sorted_indices:
            score = float(scores[idx])
            # Only include results with positive relevance scores
            if score <= 0:
                continue
                
            results.append({
                "doc_id": self.doc_metadata[idx]["id"],
                "score": score,
                "text_preview": self.doc_metadata[idx]["text_preview"],
                "metadata": self.doc_metadata[idx]["metadata"],
            })
            
            if len(results) >= top_k:
                break
        
        return results

    def save_index(self, path: str) -> bool:
        """Save BM25 index tokenized documents and metadata to disk"""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({
                    "documents": self.documents,
                    "doc_metadata": self.doc_metadata,
                    "k1": self.k1,
                    "b": self.b,
                }, f, indent=2)
            self.logger.info(f"Saved BM25 index to {path}")
            return True
        except (OSError, TypeError, ValueError) as e:
            self.logger.error(f"Error saving index: {e}")
            return False

    def load_index(self, path: str) -> bool:
        """Load BM25 index and reconstruct model from disk"""
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.documents = data.get("documents", [])
            self.doc_metadata = data["doc_metadata"]
            self.k1 = data.get("k1", 1.5)
            self.b = data.get("b", 0.75)
            
            if self.documents:
                self.bm25_model = BM25Plus(self.documents, k1=self.k1, b=self.b)
            
            self.logger.info(f"Loaded BM25 index from {path}")
            return True
        except (OSError, KeyError, TypeError, ValueError) as e:
            self.logger.error(f"Error loading index: {e}")
            return False

    def get_stats(self) -> dict:
        """Get indexing statistics"""
        return {
            "total_documents": len(self.documents),
            "k1": self.k1,
            "b": self.b,
            "model_initialized": self.bm25_model is not None,
        }