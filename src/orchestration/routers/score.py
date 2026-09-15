from fastapi import APIRouter
from ..schemas.score import ScoreRequest, ScoreResponse
from ..services import score_service

router = APIRouter(prefix="/api/v1", tags=["score"])


@router.post("/score", response_model=ScoreResponse)
def score(payload: ScoreRequest) -> ScoreResponse:
    result = score_service(payload.tender_id)
    return ScoreResponse(**result)