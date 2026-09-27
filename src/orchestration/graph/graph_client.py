from fastapi import HTTPException
from src.db_graph.graph_service import get_standard_graph
from src.orchestration.services.search_service import run_with_timeout

def safe_get_graph(standard_number: str) -> dict:
    """Safely fetch the standard graph with timeouts and error handling."""
    
    def _call_graph():
        return get_standard_graph(standard_number)

    try:
        # Use the existing timeout utility (2 seconds)
        result = run_with_timeout(_call_graph, timeout_seconds=2.0)
        
        if result is None:
            raise TimeoutError("Graph query timed out")
            
        return {"graph": result}
        
    except Exception:
        raise HTTPException(
            status_code=503, 
            detail="graph_service_unavailable"
        )