from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from src.ai_search.hybrid_search import HybridSearch
from src.ai_search.translation import translate_text

app = FastAPI(
    title="MANAK AI Search",
    description="Hybrid search and embedding service"
)

# Initialize search engine
search_engine = None

@app.on_event("startup")
async def startup_event():
    global search_engine
    search_engine = HybridSearch()
    await search_engine.initialize()
    print("✓ AI Search Engine initialized")

class SearchQuery(BaseModel):
    query: str
    language: str = "en"
    top_k: int = 5

class SearchResult(BaseModel):
    is_code: str
    title: str
    score: float
    snippet: str

@app.post("/search")
async def search(req: SearchQuery):
    """Execute hybrid search (semantic + lexical)"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    # Translate if needed
    query = req.query
    if req.language != "en":
        try:
            query = translate_text(req.query, req.language, "en")
        except Exception as e:
            print(f"Translation warning: {e}")
    
    try:
        results = await search_engine.search(query, top_k=req.top_k)
        return {"results": results, "query": query, "language": req.language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "manak-ai-search"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("SEARCH_HOST", "0.0.0.0"),
        port=int(os.getenv("SEARCH_PORT", 8001))
    )