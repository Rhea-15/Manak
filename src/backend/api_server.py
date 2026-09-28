from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Import all route modules
from src.orchestration.routers import search, recommendation, score

app = FastAPI(
    title="MANAK API",
    description="Indian Standards Compliance Engine",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(recommendation.router, prefix="/api/v1", tags=["recommendation"])
app.include_router(score.router, prefix="/api/v1", tags=["score"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "manak-backend"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000))
    )