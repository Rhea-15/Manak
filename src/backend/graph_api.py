from fastapi import APIRouter

from src.db_graph.graph_service import get_standard_graph


router = APIRouter(
    prefix="/graph",
    tags=["Neo4j Graph"]
)


@router.get("/standard/{standard_number}")
def get_graph_for_standard(standard_number: str):
    return get_standard_graph(standard_number)