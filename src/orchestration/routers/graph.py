from fastapi import APIRouter
from src.orchestration.schemas.graph import GraphResponse
from src.orchestration.graph.graph_client import safe_get_graph

router = APIRouter(prefix="/api/v1", tags=["graph"])

@router.get("/graph/{standard_number}", response_model=GraphResponse)
def get_standard_graph_endpoint(standard_number: str) -> GraphResponse:
    """Fetch the allied/normative standard graph for a specific IS code."""
    result = safe_get_graph(standard_number)
    return GraphResponse(**result)