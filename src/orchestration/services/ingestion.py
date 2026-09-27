"""Dev 4: Orchestration adapter around Dev 3's DocumentParser.

This module owns the temp-file lifecycle and maps Dev 3's
``DocumentExtractionResult`` into a plain dict the ingest router can
validate against ``IngestResponse``. It implements none of the parsing
logic itself — see ``src/ai_search/document_parser.py`` (Dev 3-owned) for
that. Do not modify ``document_parser.py`` from this module.
"""

import logging
import tempfile
import time
from pathlib import Path

from src.ai_search.document_parser import DocumentParser

logger = logging.getLogger(__name__)

# Extensions Dev 3's DocumentParser.parse() actually has a code path for
# today. Keep this in sync with document_parser.py's suffix branches —
# it is intentionally not a superset of what the UI advertises (see
# Day 3 playbook Section 4/6 re: the DocumentType.IMAGE gap).
SUPPORTED_SUFFIXES = frozenset({".pdf", ".xlsx", ".xls", ".txt"})

# Constructed lazily so importing this module (and therefore the whole
# orchestration app, via routers -> services -> ingestion) never pays the
# spaCy-model-load cost unless an ingest request actually happens.
_parser: DocumentParser | None = None


def _get_parser() -> DocumentParser:
    """Return a process-wide DocumentParser, constructing it on first use."""
    global _parser
    if _parser is None:
        _parser = DocumentParser()
    return _parser


def ingest_document(file_bytes: bytes, suffix: str, max_file_size_mb: int) -> dict:
    """Save uploaded bytes to a temp file, parse them, and return a plain dict.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        suffix: A lowercase extension from ``SUPPORTED_SUFFIXES`` (e.g.
            ``".pdf"``). Callers must validate this before calling — this
            function does not re-check the allowlist.
        max_file_size_mb: Forwarded to ``DocumentParser.parse()`` as the
            hard size ceiling.

    Returns:
        A dict combining Dev 3's ``DocumentExtractionResult.to_dict()``
        output with a ``took_ms`` timing field. Includes a ``file_path``
        key pointing at the (already-deleted) temp path — callers must
        strip this before returning it externally.

    Raises:
        ValueError: File exceeds max_file_size_mb or has an unsupported suffix.
        OSError: The temp file could not be written or read.
        RuntimeError: OCR was needed but PaddleOCR is unavailable.
        ImportError: An Excel parsing dependency is unavailable.
    """
    start = time.perf_counter()
    tmp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = Path(tmp.name)

        result = _get_parser().parse(str(tmp_path), max_file_size_mb=max_file_size_mb)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)

    payload = result.to_dict()
    payload["took_ms"] = int((time.perf_counter() - start) * 1000)
    return payload