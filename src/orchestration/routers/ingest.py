"""Dev 4: Document ingestion endpoint.

Accepts a single tender/BOQ file via multipart/form-data, hands it to Dev
3's DocumentParser (via the ingestion_service adapter in
services/ingestion.py), and returns a structured extraction result. This
file owns only the HTTP boundary — validation and error mapping. See
src/ai_search/document_parser.py (Dev 3) for the parsing implementation;
it is not modified here.
"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.ai_search.config import settings

from ..schemas.common import Language
from ..schemas.ingest import IngestResponse
from ..services import ingestion_service
from ..services.ingestion import SUPPORTED_SUFFIXES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["ingest"])

# Defined as a module-level name (not inlined) so tests can monkeypatch it
# to exercise the 413 path without constructing a real 100MB payload.
_MAX_FILE_SIZE_BYTES = settings.max_upload_file_size_mb * 1024 * 1024


@router.post(
    "/ingest",
    response_model=IngestResponse,
    responses={
        400: {"description": "Missing filename, unsupported file type, or empty file"},
        413: {"description": "File exceeds the maximum allowed size"},
        422: {"description": "Missing file part or invalid form field"},
        500: {"description": "Document parsing failed"},
    },
)
def ingest(
    file: UploadFile = File(...),
    language: Language = Form(Language.en),
) -> IngestResponse:
    """Parse an uploaded tender/BOQ document and return structured extraction results.

    ``language`` is accepted now for schema/UI consistency but not yet
    used — real translation is Dev 4's Day 4 task.

    Raises:
        HTTPException: 400 for a missing/unsupported filename, an empty
            file, or a parser-reported ValueError (bad suffix/oversize);
            413 if the file exceeds the configured size limit; 500 if the
            underlying parser fails for any other reason.
    """
    del language  # noqa: F841 — reserved for Day 4 translation middleware

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Supported: {supported}",
        )

    contents = file.file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(contents) > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the maximum allowed size of "
            f"{settings.max_upload_file_size_mb} MB",
        )

    try:
        result = ingestion_service(contents, suffix, settings.max_upload_file_size_mb)
    except ValueError as exc:
        # Belt-and-suspenders: the parser re-checks size/suffix internally
        # against the temp file it writes, so this is normally unreachable
        # given the guards above, but a genuine mismatch is a client error.
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (OSError, RuntimeError, ImportError) as exc:
        logger.error("Document ingestion failed for %s: %s", file.filename, exc)
        raise HTTPException(status_code=500, detail="ingestion_failed") from exc
    except Exception as exc:  # noqa: BLE001 — last-resort guard at the HTTP boundary
        logger.error("Unexpected ingestion error for %s: %s", file.filename, exc)
        raise HTTPException(status_code=500, detail="ingestion_failed") from exc

    # Never leak the server's local temp file path to the client.
    result.pop("file_path", None)

    return IngestResponse(
        upload_id=str(uuid.uuid4()),
        filename=Path(file.filename).name,
        status="parsed",
        **result,
    )