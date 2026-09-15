from pydantic import BaseModel, Field
from .common import Language


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, examples=["fireproof copper wire 1.5 sq mm"])
    language: Language = Language.en
    top_k: int = Field(default=5, ge=1, le=50)


class SearchResult(BaseModel):
    is_code: str
    title: str
    score: float = Field(..., ge=0, le=1)
    status: str
    snippet: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    took_ms: int