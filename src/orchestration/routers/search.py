from fastapi import APIRouter, HTTPException

from ..schemas.common import Language
from ..schemas.search import SearchRequest, SearchResponse
from ..services.search_service import search_standards
from ..services.translation import translation_service

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"description": "Query is empty or whitespace-only"},
        500: {"description": "Search service unavailable"},
    },
)
def search(payload: SearchRequest) -> SearchResponse:
    """Return IS-standard matches for a non-blank search query."""
    if not payload.query.strip():
        raise HTTPException(
            status_code=400,
            detail="query cannot be empty or whitespace",
        )

    canonical_query = payload.query

    # English bypasses translation entirely — no detection/model call at all.
    if payload.language != Language.en:
        try:
            translation_result = translation_service(payload.query)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="translation_service_unavailable",
            ) from exc
        # normalize_query() may legitimately return the original text
        # unchanged (no-op passthrough) — that's not a failure, just use it.
        canonical_query = translation_result.get("normalized") or payload.query

    try:
        result = search_standards(
            query=canonical_query,
            top_k=payload.top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="search_service_unavailable",
        ) from exc

    # SearchResponse.query echoes the ORIGINAL user-facing text, never the
    # translated/canonical one — no screenshot shows a "translated to X" UI
    # state to justify exposing it.
    result["query"] = payload.query

    return SearchResponse(**result)