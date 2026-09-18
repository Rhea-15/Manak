"""
Dev 3: Tests for embedding pipeline
"""

from unittest.mock import MagicMock, patch

import numpy as np

from src.ai_search.embedding_pipeline import (
    EmbeddingModel,
    EmbeddingPipeline,
)


class TestEmbeddingModel:
    """Test embedding model"""

    @patch("src.ai_search.embedding_pipeline.SentenceTransformer")
    def test_model_initialization(self, mock_st):
        """Test model loading"""
        mock_model = MagicMock()
        mock_st.return_value = mock_model
        
        embedder = EmbeddingModel("BAAI/bge-m3")
        
        assert embedder.model_name == "BAAI/bge-m3"
        mock_st.assert_called_once()

    @patch("src.ai_search.embedding_pipeline.SentenceTransformer")
    def test_encode_single_text(self, mock_st):
        """Test encoding a single text"""
        mock_model = MagicMock()
        mock_st.return_value = mock_model
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_model.get_sentence_embedding_dimension.return_value = 1024
        
        embedder = EmbeddingModel()
        vector = embedder.encode("Test text")
        
        assert isinstance(vector, list)
        assert len(vector) == 3

    @patch("src.ai_search.embedding_pipeline.SentenceTransformer")
    def test_encode_multiple_texts(self, mock_st):
        """Test encoding multiple texts"""
        mock_model = MagicMock()
        mock_st.return_value = mock_model
        mock_model.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ])
        mock_model.get_sentence_embedding_dimension.return_value = 1024
        
        embedder = EmbeddingModel()
        vectors = embedder.encode(["Text 1", "Text 2"])
        
        assert isinstance(vectors, list)
        assert len(vectors) == 2


class TestEmbeddingPipeline:
    """Test embedding pipeline orchestration"""

    @patch("src.ai_search.embedding_pipeline.SentenceTransformer")
    def test_embed_document_pages(self, mock_st):
        """Test embedding document pages with chunking"""
        mock_model = MagicMock()
        mock_st.return_value = mock_model
        mock_model.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ])
        mock_model.get_sentence_embedding_dimension.return_value = 1024
        
        pipeline = EmbeddingPipeline()
        
        pages = [
            {
                "page_number": 1,
                "text": "A" * 1000,  # Long text to trigger chunking
            }
        ]
        
        result = pipeline.embed_document_pages(pages, chunk_size=500)
        
        assert len(result) >= 1
        assert "vector" in result[0]
        assert "page_number" in result[0]

    @patch("src.ai_search.embedding_pipeline.SentenceTransformer")
    def test_chunk_text(self, mock_st):
        """Test text chunking utility"""
        pipeline = EmbeddingPipeline()
        
        long_text = "Word " * 200  # ~1000 characters
        chunks = pipeline._chunk_text(long_text, chunk_size=200)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert "text" in chunk
            assert "char_range" in chunk