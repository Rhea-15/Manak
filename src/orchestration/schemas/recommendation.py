from pydantic import BaseModel,Field


class RecommendationRequest(BaseModel):
    item_id: str = Field(..., min_length=1)
    original_spec: str = Field(..., min_length=1)


class RecommendationResponse(BaseModel):
    item_id: str
    original_spec: str
    ai_suggested_spec: str
    compliant: bool
    mandatory_marks: list[str] = []
    allied_standards: list[str] = []
    source: str = "rules_engine"  # never allow "llm_guess" to reach the frontend