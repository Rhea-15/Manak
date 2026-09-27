"""
Orchestration-layer wrapper around Dev 3's TranslationPipeline.

Ownership boundary: this file owns ONLY the singleton lifecycle and the
thin call-through used by routers/search.py. All translation/model logic
lives in src/ai_search/translation.py (Dev 3) and is never modified here.
"""
from src.ai_search.translation import TranslationPipeline
# Instantiated once at module import (= app startup), matching the eager
# model-load discipline IndicTrans2Translator.__init__ requires. Never
# construct TranslationPipeline() per-request.
_pipeline = TranslationPipeline()


def translation_service(query: str) -> dict:
    """
    Pass-through to Dev 3's normalize_query():
        {"original": str, "normalized": str, "language": str, "is_translation": bool}

    Translation's own anticipated failure modes (missing deps, model
    unavailable, detection failure) are already swallowed inside
    translate()/detect_language() and surface here as a clean pass-through
    result, not an exception. Only a genuinely unexpected exception should
    reach the caller — routers/search.py is responsible for catching it.
    """
    return _pipeline.normalize_query(query)