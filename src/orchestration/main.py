from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend import (
    audit,
    compliance_api,
    documents,
    graph_api,
    quality_score,
    review,
    unified_api,
    verification,
)
from src.orchestration.routers import recommendation, score, search

app = FastAPI(
    title="MANAK Orchestration & Unified API Gateway",
    description="Unified API gateway for search, recommendation, quality score, compliance, and governance",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Orchestration Endpoints
app.include_router(search.router)
app.include_router(recommendation.router)
app.include_router(score.router)

# Core Backend & Graph Endpoints
app.include_router(documents.router)
app.include_router(review.router)
app.include_router(audit.router)
app.include_router(compliance_api.router)
app.include_router(quality_score.router)
app.include_router(verification.router)
app.include_router(graph_api.router)
app.include_router(unified_api.router)


@app.get("/health")
def health() -> dict:
    """Service liveness and health status."""
    return {"status": "ok", "gateway": "manak-orchestration"}