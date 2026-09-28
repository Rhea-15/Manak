"""
Dev 3: Centralized, env-driven configuration for the AI & Search module.
Nothing in ai_search/*.py should hardcode a host, port, model name, or
tuning constant again — it comes from here, which reads the environment
(and an optional local .env file) with the previous literals kept only
as the fallback default.
"""
import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; plain env vars still work


def _env_str(key: str, default: str) -> str:
    """Return the environment value, including an empty string, or the default if unset."""
    return os.getenv(key, default)


def _env_int(key: str, default: int) -> int:
    """Return an integer environment value, or the default if unset.

    Raises:
        ValueError: If the set value cannot be parsed as an integer.
    """
    val = os.getenv(key)
    return int(val) if val is not None else default


def _env_float(key: str, default: float) -> float:
    """Return a floating-point environment value, or the default if unset.

    Raises:
        ValueError: If the set value cannot be parsed as a float.
    """
    val = os.getenv(key)
    return float(val) if val is not None else default


@dataclass(frozen=True)
class AISearchSettings:
    # Qdrant
    qdrant_host: str = field(default_factory=lambda: _env_str("QDRANT_HOST", "localhost"))
    qdrant_port: int = field(default_factory=lambda: _env_int("QDRANT_PORT", 6333))
    qdrant_collection: str = field(default_factory=lambda: _env_str("QDRANT_COLLECTION", "indian_standards"))
    qdrant_api_key: str | None = field(default_factory=lambda: os.getenv("QDRANT_API_KEY") or None)

    # Embeddings
    embedding_model: str = field(default_factory=lambda: _env_str("EMBEDDING_MODEL", "BAAI/bge-m3"))
    embedding_vector_size: int = field(default_factory=lambda: _env_int("EMBEDDING_VECTOR_SIZE", 1024))
    embedding_batch_size: int = field(default_factory=lambda: _env_int("EMBEDDING_BATCH_SIZE", 32))
    chunk_size: int = field(default_factory=lambda: _env_int("CHUNK_SIZE", 500))
    chunk_overlap: int = field(default_factory=lambda: _env_int("CHUNK_OVERLAP", 100))

    # spaCy
    spacy_model: str = field(default_factory=lambda: _env_str("SPACY_MODEL", "en_core_web_sm"))

    # BM25
    bm25_k1: float = field(default_factory=lambda: _env_float("BM25_K1", 1.5))
    bm25_b: float = field(default_factory=lambda: _env_float("BM25_B", 0.75))
    bm25_index_path: str = field(default_factory=lambda: _env_str("BM25_INDEX_PATH", "data/bm25_index.json"))

    # RRF / hybrid search
    rrf_k: int = field(default_factory=lambda: _env_int("RRF_K", 60))
    hybrid_vector_weight: float = field(default_factory=lambda: _env_float("HYBRID_VECTOR_WEIGHT", 0.5))
    hybrid_bm25_weight: float = field(default_factory=lambda: _env_float("HYBRID_BM25_WEIGHT", 0.5))

    # IndicTrans2
    indictrans2_model: str = field(
        default_factory=lambda: _env_str("INDICTRANS2_MODEL", "ai4bharat/indic-trans-v2-all-gpu")
    )
    translation_max_length: int = field(default_factory=lambda: _env_int("TRANSLATION_MAX_LENGTH", 512))
    translation_num_beams: int = field(default_factory=lambda: _env_int("TRANSLATION_NUM_BEAMS", 4))

    # Ingestion
    max_upload_file_size_mb: int = field(default_factory=lambda: _env_int("MAX_UPLOAD_FILE_SIZE_MB", 100))

    def __post_init__(self) -> None:
        """Fail fast on invalid generation settings at startup.

        Without this, TRANSLATION_MAX_LENGTH<=0 or TRANSLATION_NUM_BEAMS<=0
        would only surface deep inside model.generate() — and translate()
        catches that and silently returns the original query, while
        normalize_query() still reports is_translation=True as if
        translation had succeeded. Reject invalid values immediately
        instead of letting that mask a broken config.
        """
        if self.translation_max_length <= 0:
            raise ValueError(
                "TRANSLATION_MAX_LENGTH must be a positive integer, "
                f"got {self.translation_max_length}"
            )
        if self.translation_num_beams <= 0:
            raise ValueError(
                "TRANSLATION_NUM_BEAMS must be a positive integer, "
                f"got {self.translation_num_beams}"
            )


settings = AISearchSettings()