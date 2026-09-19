from fastapi import APIRouter
from ..schemas.recommendation import RecommendationRequest, RecommendationResponse
from ..services import recommendation_service

router = APIRouter(prefix="/api/v1", tags=["recommendation"])


@router.post("/recommendation", response_model=RecommendationResponse)
def recommend(payload: RecommendationRequest) -> RecommendationResponse:
    """Return an AI-suggested compliant spec and mandatory marks for a single BOQ item."""
    result = recommendation_service(payload.item_id, payload.original_spec)
    return RecommendationResponse(**result)