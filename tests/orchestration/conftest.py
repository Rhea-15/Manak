import sys
from unittest.mock import patch, MagicMock

# Block other devs' dependencies from crashing test collection
sys.modules["minio"] = MagicMock()
sys.modules["neo4j"] = MagicMock()

import types

def _install_translation_stub_if_needed() -> None:
    try:
        import src.ai_search.translation  # noqa: F401
        return
    except ImportError:
        pass

    stub = types.ModuleType("src.ai_search.translation")

    class TranslationPipeline:
        def __init__(self, *args, **kwargs):
            pass
            
        def normalize_query(self, query):
            return {"original": query, "normalized": query, "language": "eng_Latn", "is_translation": False}

    stub.TranslationPipeline = TranslationPipeline
    sys.modules["src.ai_search.translation"] = stub

_install_translation_stub_if_needed()

def _install_document_parser_stub_if_needed() -> None:
    try:
        import src.ai_search.document_parser  # noqa: F401

        return  # real dependencies are installed — use the real module
    except ImportError:
        pass

    stub = types.ModuleType("src.ai_search.document_parser")

    class DocumentParser:  # minimal stand-in
        """Placeholder only. Every test in test_ingest.py monkeypatches
        this class before use — if this implementation ever actually
        runs, a test is missing its monkeypatch."""

        def __init__(self, *args, **kwargs):
            pass

        def parse(self, file_path, max_file_size_mb=100):
            raise NotImplementedError(
                "document_parser stub invoked directly — the calling "
                "test forgot to monkeypatch DocumentParser."
            )

    stub.DocumentParser = DocumentParser
    sys.modules["src.ai_search.document_parser"] = stub


def _install_embedding_pipeline_stub_if_needed() -> None:
    """Same technique as the document_parser stub above, for the same
    reason: embedding_pipeline.py imports sentence_transformers (and
    therefore torch) at module top level, so importing
    src.orchestration.main — which every orchestration test file does —
    otherwise hard-requires the full ML stack just to collect, even for
    tests that have nothing to do with embeddings.
    """
    try:
        import src.ai_search.embedding_pipeline  # noqa: F401

        return  # real dependencies are installed — use the real module
    except ImportError:
        pass

    stub = types.ModuleType("src.ai_search.embedding_pipeline")

    class EmbeddingModel:  # minimal stand-in
        """Placeholder only. Any test exercising real search behavior
        must monkeypatch this class before use — if this implementation
        ever actually runs, a test is missing its monkeypatch."""

        def __init__(self, *args, **kwargs):
            pass

        def encode(self, *args, **kwargs):
            raise NotImplementedError(
                "embedding_pipeline stub invoked directly — the calling "
                "test forgot to monkeypatch EmbeddingModel."
            )

    stub.EmbeddingModel = EmbeddingModel
    sys.modules["src.ai_search.embedding_pipeline"] = stub


_install_document_parser_stub_if_needed()
_install_embedding_pipeline_stub_if_needed()