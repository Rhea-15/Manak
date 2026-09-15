from pydantic import BaseModel, Field
from .common import Severity


class ScoreRequest(BaseModel):
    tender_id: str


class CriticalAlert(BaseModel):
    type: str
    message: str
    severity: Severity


class ScoreResponse(BaseModel):
    tender_id: str
    score: int = Field(..., ge=0, le=100)
    verdict: str
    critical_alerts: list[CriticalAlert] = []