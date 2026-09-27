from unittest.mock import MagicMock, patch
from src.db_graph.graph_service import get_standard_graph

@patch("src.db_graph.graph_service.cache_get")
@patch("src.db_graph.graph_service.cache_set")
@patch("src.db_graph.graph_service.driver")
def test_get_standard_graph_found(mock_driver, mock_cache_set, mock_cache_get):
    """Test successful graph retrieval with linked standards."""
    mock_cache_get.return_value = None  # Force DB query
    
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    
    mock_result = MagicMock()
    mock_result.single.return_value = {
        "standard_number": "IS 456",
        "title": "Plain and Reinforced Concrete",
        "linked_standards": [
            {"standard_number": "IS 383", "title": "Coarse and Fine Aggregates", "relationship": "REFERENCES"}
        ]
    }
    mock_session.run.return_value = mock_result
    
    result = get_standard_graph("IS 456")
    
    assert result["found"] is True
    assert result["standard_number"] == "IS 456"
    assert len(result["linked_standards"]) == 1
    assert result["linked_standards"][0]["relationship"] == "REFERENCES"
    mock_cache_set.assert_called_once()

@patch("src.db_graph.graph_service.cache_get")
@patch("src.db_graph.graph_service.driver")
def test_get_standard_graph_not_found(mock_driver, mock_cache_get):
    """Test graph retrieval when standard doesn't exist."""
    mock_cache_get.return_value = None
    
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    
    mock_result = MagicMock()
    mock_result.single.return_value = None  # No record found
    mock_session.run.return_value = mock_result
    
    result = get_standard_graph("INVALID")
    
    assert result["found"] is False
    assert result["standard_number"] == "INVALID"
    assert result["linked_standards"] == []