from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import recommendation, score, search

app = FastAPI(
    title="MANAK Orchestration Layer",
    description="Dev 4 — API gateway for search, recommendation, and Tender Quality Score",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # confirm exact port with Dev 5
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(recommendation.router)
app.include_router(score.router)


@app.get("/health")
def health() -> dict:
    """Return a simple liveness check for the orchestration service."""
    return {"status": "ok"}