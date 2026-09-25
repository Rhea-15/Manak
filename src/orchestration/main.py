from fastapi import FastAPI

from src.backend import audit, compliance_api, quality_score, review, verification

from .routers import recommendation, score, search

app = FastAPI(
    title="MANAK Orchestration Layer",
    description="Dev 4 — API gateway for search, recommendation, and Tender Quality Score",
    version="0.1.0",
)

app.include_router(search.router)
app.include_router(recommendation.router)
app.include_router(score.router)
app.include_router(audit.router)
app.include_router(compliance_api.router)
app.include_router(quality_score.router)
app.include_router(review.router)
app.include_router(verification.router)


@app.get("/health")
def health() -> dict:
    """Return a simple liveness check confirming the orchestration service is running."""
    return {"status": "ok"}
