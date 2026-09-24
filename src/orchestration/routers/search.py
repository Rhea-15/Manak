from fastapi import APIRouter, HTTPException

from ..schemas.search import SearchRequest, SearchResponse
from ..services import search_service

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
    """Return IS-standard matches for a non-blank search query.

    Raises:
        HTTPException: With status 400 when the query is blank, or status 500
            when the search service raises an exception.
    """
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty or whitespace")

    try:
        result = search_service(payload.query, payload.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="search_service_unavailable") from exc

    return SearchResponse(**result)

