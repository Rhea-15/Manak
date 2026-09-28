from fastapi import APIRouter, HTTPException

from ..schemas.search import SearchRequest, SearchResponse
from ..services.search_service import search_standards

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
<<<<<<< HEAD
    """Validate a search request, call the search service, and return matched IS standards.

    Returns 400 if the query is empty or whitespace-only, 422 on schema
    validation failure, and 500 if the underlying search service fails.
    """
=======
    """Return IS-standard matches for a non-blank search query."""
>>>>>>> 240e0e8a30bc687b7b154b536634473b3a5f11e6
    if not payload.query.strip():
        raise HTTPException(
            status_code=400,
            detail="query cannot be empty or whitespace",
        )

    try:
        result = search_standards(
            query=payload.query,
            top_k=payload.top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="search_service_unavailable",
        ) from exc

    return SearchResponse(**result)
