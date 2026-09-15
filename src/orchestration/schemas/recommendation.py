from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    item_id: str
    original_spec: str


class RecommendationResponse(BaseModel):
    item_id: str
    original_spec: str
    ai_suggested_spec: str
    compliant: bool
    mandatory_marks: list[str] = []
    allied_standards: list[str] = []
    source: str = "rules_engine"  # never allow "llm_guess" to reach the frontend