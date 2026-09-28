"""
Dev 3: FastAPI Application Entrypoint for AI Search Engine
Provides REST API endpoints for document ingestion, search, validation, and seeding.
"""
from dotenv import load_dotenv
load_dotenv()
import logging
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from src.ai_search.bm25_indexer import BM25Indexer
from src.ai_search.config import settings
from src.ai_search.document_parser import DocumentParser
from src.ai_search.embedding_pipeline import EmbeddingPipeline
from src.ai_search.hybrid_search import HybridSearchEngine
from src.ai_search.qdrant_schema import QdrantConfig, QdrantSchemaManager
from src.ai_search.seed_pipeline import run as run_seed_pipeline
from src.ai_search.translation import TranslationPipeline
from src.ai_search.validation import RulesEngine

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MANAK AI Search Service",
    description="Vector & Lexical Hybrid Search Engine for Indian Standards and BOQ processing",
    version="1.0.0",
)
# Add this right after app initialization in src/ai_search/main.py:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Schemas ---

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    mode: str = Field(default="rrf", pattern="^(rrf|weighted)$", description="Fusion mode: rrf or weighted")


class StandardValidationRequest(BaseModel):
    code: str = Field(..., description="Standard code, e.g., IS 1554")
    title: str = Field(..., description="Standard title")
    definition: str = Field(..., description="Standard definition text")
    year: int | None = Field(default=None, description="Year of publication")
    qco_required: bool = Field(default=False)
    qco_code: str | None = Field(default=None)
    isi_required: bool = Field(default=False)
    isi_mark: str | None = Field(default=None)


class SeedResponse(BaseModel):
    standards_processed: int
    qdrant_vectors_inserted: int | None = None
    bm25_stats: dict[str, Any] | None = None
    bm25_index_path: str | None = None
    bm25_index_saved: bool | None = None


# --- Endpoints ---

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, Any]:
    """Check service operational status and loaded configuration."""
    return {
        "status": "healthy",
        "qdrant_host": settings.qdrant_host,
        "qdrant_port": settings.qdrant_port,
        "embedding_model": settings.embedding_model,
    }


@app.post("/search", status_code=status.HTTP_200_OK)
def search(request: SearchRequest) -> dict[str, Any]:
    """
    Execute hybrid vector (Qdrant) and lexical (BM25) search with query normalization.
    """
    try:
        # 1. Normalize/Translate Query
        translator = TranslationPipeline()
        normalized_info = translator.normalize_query(request.query)
        search_query = str(normalized_info["normalized"])

        # 2. Dense Vector Search via Qdrant
        embedder = EmbeddingPipeline(embedding_model_name=settings.embedding_model)
        query_vector = embedder.embedder.encode(search_query)

        qdrant = QdrantSchemaManager(QdrantConfig())
        vector_hits = qdrant.search(
            query_vector=query_vector,
            limit=request.top_k,
            collection_name=settings.qdrant_collection,
        )

        vector_results = [
            {"doc_id": hit["id"], "score": hit["score"], "payload": hit.get("payload", {})}
            for hit in vector_hits
        ]

        # 3. Lexical Search via BM25
        bm25 = BM25Indexer()
        bm25_results = []
        if Path(settings.bm25_index_path).exists():
            if bm25.load_index(settings.bm25_index_path):
                bm25_results = bm25.search(query=search_query, top_k=request.top_k)

        # 4. Hybrid Fusion
        hybrid_engine = HybridSearchEngine(
            vector_weight=settings.hybrid_vector_weight,
            bm25_weight=settings.hybrid_bm25_weight,
        )

        if request.mode == "weighted":
            fused_results = hybrid_engine.search_weighted(
                query=search_query,
                vector_results=vector_results,
                bm25_results=bm25_results,
                top_k=request.top_k,
            )
        else:
            fused_results = hybrid_engine.search_rrf(
                query=search_query,
                vector_results=vector_results,
                bm25_results=bm25_results,
                top_k=request.top_k,
            )

        return {
            "query_info": normalized_info,
            "mode": request.mode,
            "total_results": len(fused_results),
            "results": [
                {
                    "rank": res.rank,
                    "doc_id": res.doc_id,
                    "combined_score": res.combined_score,
                    "vector_score": res.vector_score,
                    "bm25_score": res.bm25_score,
                }
                for res in fused_results
            ],
        }
    except Exception as exc:
        logger.exception("Error processing search query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search operation failed: {exc}",
        ) from exc


@app.post("/parse-document", status_code=status.HTTP_200_OK)
async def parse_document(file: UploadFile = File(...)) -> dict[str, Any]:
    """Parse document (PDF, TXT, Excel/BOQ) and extract entities."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename",
        )

    suffix = Path(file.filename).suffix.lower()
    allowed_suffixes = {".pdf", ".txt", ".xlsx", ".xls"}
    if suffix not in allowed_suffixes:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{suffix}'. Allowed: {allowed_suffixes}",
        )

    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        parser = DocumentParser()
        result = parser.parse(file_path=temp_path)
        return result.to_dict()

    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as exc:
        logger.exception("Failed to parse uploaded document")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document parsing failed: {exc}",
        ) from exc


@app.post("/validate-standard", status_code=status.HTTP_200_OK)
def validate_standard(request: StandardValidationRequest) -> dict[str, Any]:
    """Validate a standard against QCO, ISI, and formatting rules."""
    engine = RulesEngine()
    result = engine.validate_standard(request.model_dump())
    summary = engine.get_validation_summary(result)

    return {
        "summary": summary,
        "is_valid": result.is_valid,
        "score": result.score,
        "errors": [
            {
                "field": err.field,
                "error_type": err.error_type,
                "message": err.message,
                "severity": err.severity,
            }
            for err in result.errors
        ],
        "warnings": [
            {
                "field": warn.field,
                "error_type": warn.error_type,
                "message": warn.message,
                "severity": warn.severity,
            }
            for warn in result.warnings
        ],
    }


@app.post("/seed", response_model=SeedResponse, status_code=status.HTTP_200_OK)
def seed_database() -> dict[str, Any]:
    """Trigger the seed pipeline to embed standards and index into Qdrant & BM25."""
    try:
        result = run_seed_pipeline()
        return result
    except Exception as exc:
        logger.exception("Seed pipeline failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seed pipeline failed: {exc}",
        ) from exc
