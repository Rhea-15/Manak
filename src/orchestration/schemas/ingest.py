"""Dev 4: Response schema for the document ingestion endpoint.

Mirrors the shape returned by Dev 3's ``DocumentExtractionResult.to_dict()``
(see ``src/ai_search/document_parser.py``), plus the orchestration-layer
fields (``upload_id``, ``filename``, ``status``, ``took_ms``) added by
``services/ingestion.py`` and ``routers/ingest.py``. This file does not
depend on ``document_parser.py`` directly — it only re-declares the shape
as a Pydantic model so the response is schema-validated and documented in
``/docs``.
"""

from typing import Any

from pydantic import BaseModel, Field


class ExtractedEntitySchema(BaseModel):
    text: str
    entity_type: str
    confidence: float = Field(..., ge=0, le=1)
    page: int
    bbox: tuple[float, float, float, float] | None = None


class ExtractedPageSummary(BaseModel):
    page_number: int
    raw_text: str
    entity_count: int = Field(..., ge=0)
    table_count: int = Field(..., ge=0)
    entities: list[ExtractedEntitySchema] = Field(default_factory=list)


class IngestResponse(BaseModel):
    upload_id: str
    filename: str
    document_type: str
    status: str = "parsed"
    total_pages: int = Field(..., ge=0)
    language_detected: str
    pages: list[ExtractedPageSummary]
    metadata: dict[str, Any]
    took_ms: int = Field(..., ge=0)