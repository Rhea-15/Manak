"""
Dev 3 — Day 9 addendum: regression guard against hardcoded tuning constants.

config.py's own docstring states nothing in ai_search/*.py should hardcode a
host, port, model name, or tuning constant — it should come from
AISearchSettings. These tests assert every constructor/default actually reads
from `settings` instead of a baked-in literal.
"""
import json

from src.ai_search.bm25_indexer import BM25Indexer
from src.ai_search.config import AISearchSettings, settings
from src.ai_search.embedding_pipeline import EmbeddingModel
from src.ai_search.hybrid_search import HybridSearchEngine, ReciprocalRankFusion
from src.ai_search.translation import IndicTrans2Translator


class TestConfigIsSingleSourceOfTruth:
    def test_rrf_default_k_matches_settings(self):
        assert ReciprocalRankFusion().k == settings.rrf_k

    def test_hybrid_engine_default_weights_match_settings(self):
        engine = HybridSearchEngine()
        assert engine.vector_weight == settings.hybrid_vector_weight
        assert engine.bm25_weight == settings.hybrid_bm25_weight

    def test_hybrid_engine_internal_rrf_uses_configured_k(self):
        engine = HybridSearchEngine()
        assert engine.rrf.k == settings.rrf_k

    def test_bm25_default_params_match_settings(self):
        indexer = BM25Indexer()
        assert indexer.k1 == settings.bm25_k1
        assert indexer.b == settings.bm25_b

    def test_bm25_load_index_fallback_matches_settings(self, tmp_path):
        """A legacy index file with no k1/b keys should fall back to the
        configured defaults, not literals baked into load_index()."""
        index_path = tmp_path / "legacy_index.json"
        index_path.write_text(json.dumps({
            "documents": [["copper", "wire"]],
            "doc_metadata": [{"id": 1, "text_preview": "copper wire", "metadata": {}}],
        }))

        indexer = BM25Indexer()
        assert indexer.load_index(str(index_path))
        assert indexer.k1 == settings.bm25_k1
        assert indexer.b == settings.bm25_b

    def test_translator_default_model_matches_settings(self):
        translator = IndicTrans2Translator()
        assert translator.model_name == settings.indictrans2_model

    def test_embedding_model_default_matches_settings(self):
        # Checked via function defaults, not instantiation — instantiating
        # would download/load a real SentenceTransformer model.
        assert EmbeddingModel.__init__.__defaults__ == (settings.embedding_model,)

    def test_embedding_encode_default_batch_size_matches_settings(self):
        assert EmbeddingModel.encode.__defaults__[-1] == settings.embedding_batch_size

    def test_translation_generation_params_are_configurable(self):
        fresh = AISearchSettings()
        assert hasattr(fresh, "translation_max_length")
        assert hasattr(fresh, "translation_num_beams")