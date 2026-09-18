"""
Dev 3: Tests for Qdrant schema management
"""

from unittest.mock import MagicMock, patch

from src.ai_search.qdrant_schema import (
    QdrantConfig,
    QdrantSchemaManager,
)


class TestQdrantConfig:
    """Test Qdrant configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = QdrantConfig()
        
        assert config.host == "localhost"
        assert config.port == 6333
        assert config.collection_name == "indian_standards"
        assert config.vector_size == 1024

    def test_custom_config(self):
        """Test custom configuration"""
        config = QdrantConfig(
            host="qdrant.example.com",
            port=6334,
            collection_name="custom_collection",
        )
        
        assert config.host == "qdrant.example.com"
        assert config.port == 6334
        assert config.collection_name == "custom_collection"


class TestQdrantSchemaManager:
    """Test schema manager (with mocking)"""

    @patch("src.ai_search.qdrant_schema.QdrantClient")
    def test_initialization(self, mock_qdrant):
        """Test manager initialization"""
        config = QdrantConfig()
        manager = QdrantSchemaManager(config)
        
        assert manager.config == config
        assert manager.client is not None

    @patch("src.ai_search.qdrant_schema.QdrantClient")
    def test_insert_vector(self, mock_qdrant):
        """Test vector insertion"""
        config = QdrantConfig()
        manager = QdrantSchemaManager(config)
        
        # Mock the upsert method
        manager.client.upsert = MagicMock(return_value=True)
        
        result = manager.insert_vector(
            point_id=1,
            vector=[0.1, 0.2, 0.3],
            payload={"standard_code": "IS 1554"},
        )
        
        assert result is True
        manager.client.upsert.assert_called_once()

    @patch("src.ai_search.qdrant_schema.QdrantClient")
    def test_batch_insert_vectors(self, mock_qdrant):
        """Test batch vector insertion"""
        config = QdrantConfig()
        manager = QdrantSchemaManager(config)
        
        manager.client.upsert = MagicMock(return_value=True)
        
        points = [
            {
                "id": 1,
                "vector": [0.1, 0.2, 0.3],
                "payload": {"code": "IS 1554"},
            },
            {
                "id": 2,
                "vector": [0.4, 0.5, 0.6],
                "payload": {"code": "IS 694"},
            },
        ]
        
        count = manager.batch_insert_vectors(points)
        
        assert count == 2
        manager.client.upsert.assert_called_once()