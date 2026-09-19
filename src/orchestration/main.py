from fastapi import FastAPI

from .routers import recommendation, score, search

app = FastAPI(
    title="MANAK Orchestration Layer",
    description="Dev 4 — API gateway for search, recommendation, and Tender Quality Score",
    version="0.1.0",
)

app.include_router(search.router)
app.include_router(recommendation.router)
app.include_router(score.router)


@app.get("/health")
def health() -> dict:
    """Return a simple liveness check confirming the orchestration service is running."""
    return {"status": "ok"}
