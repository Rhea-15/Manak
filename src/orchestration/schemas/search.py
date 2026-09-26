from pydantic import BaseModel, Field

from .common import Language


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, examples=["fireproof copper wire 1.5 sq mm"])
    language: Language = Language.en
    top_k: int = Field(default=5, ge=1, le=50)


class SearchResult(BaseModel):
    standard_number: str
    title: str
    score: float = Field(..., ge=0, le=1)
    status: str
    active_version: str | None = None
    compliance: dict = Field(default_factory=dict)
    graph: dict = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    vector_results_found: int = 0
    results_returned: int = 0
    source: str
    status: str | None = None
    top_k: int | None = None
