from unittest.mock import patch
from fastapi.testclient import TestClient
from src.orchestration.main import app

client = TestClient(app)

@patch("src.orchestration.graph.graph_client.get_standard_graph")
def test_graph_endpoint_success(mock_get_graph):
    """Endpoint returns 200 and matches expected schema on success."""
    mock_get_graph.return_value = {
        "found": True,
        "standard_number": "IS 694",
        "title": "PVC cables",
        "linked_standards": [
            {"standard_number": "IS 8130", "title": "Conductors", "relationship": "TESTED_BY"}
        ]
    }
    
    response = client.get("/api/v1/graph/IS 694")
    assert response.status_code == 200
    
    data = response.json()["graph"]
    assert data["found"] is True
    assert data["standard_number"] == "IS 694"
    assert len(data["linked_standards"]) == 1

@patch("src.orchestration.graph.graph_client.get_standard_graph")
def test_graph_endpoint_neo4j_unavailable(mock_get_graph):
    """Endpoint returns 503 cleanly if the graph service fails or times out."""
    mock_get_graph.side_effect = Exception("Neo4j connection refused")
    
    response = client.get("/api/v1/graph/IS 694")
    assert response.status_code == 503
    assert response.json()["detail"] == "graph_service_unavailable"