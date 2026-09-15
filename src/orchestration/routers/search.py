from fastapi import APIRouter
from ..schemas.search import SearchRequest, SearchResponse
from ..services import search_service

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(payload: SearchRequest) -> SearchResponse:
    result = search_service(payload.query, payload.top_k)
    return SearchResponse(**result)