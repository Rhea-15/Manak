from fastapi import APIRouter

from ..schemas.search import SearchRequest
from ..services.search_service import search_standards

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.post("/search")
def search(payload: SearchRequest) -> dict:
    return search_standards(
        query=payload.query,
        top_k=payload.top_k,
    )
