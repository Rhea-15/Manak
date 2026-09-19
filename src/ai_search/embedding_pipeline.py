"""
Dev 3: Embedding Pipeline using bge-m3
Converts text into dense vectors for semantic search
"""


import logging
from typing import overload

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

from typing import TypedDict


class PageInput(TypedDict, total=False):
    page_number: int
    text: str

class EmbeddedChunk(TypedDict):
    page_number: int
    chunk_index: int
    text: str
    char_range: tuple[int, int]
    vector: list[float]


class StandardInput(TypedDict, total=False):
    code: str
    title: str
    definition: str


class EmbeddedStandard(TypedDict):
    code: str | None
    title: str | None
    definition: str | None
    vector: list[float]

class EmbeddingModel:
    """Wrapper around bge-m3 embedding model"""

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        """
        Initialize embedding model.

        Args:
            model_name: Hugging Face model name (default: bge-m3 multilingual)
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name

        try:
            self.model = SentenceTransformer(model_name)
            self.logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            self.logger.error(f"Error loading model {model_name}: {e}")
            raise

    @overload
    def encode(
        self, texts: str, normalize: bool = True, batch_size: int = 32
    ) -> list[float]: ...

    @overload
    def encode(
        self, texts: list[str], normalize: bool = True, batch_size: int = 32
    ) -> list[list[float]]: ...

    def encode(
        self,
        texts: str | list[str],
        normalize: bool = True,
        batch_size: int = 32,
    ) -> list[float] | list[list[float]]:
        """
        Encode text(s) to dense vectors.

        Args:
            texts: Single text or list of texts
            normalize: Whether to L2 normalize vectors (recommended for cosine similarity)
            batch_size: Batch size for encoding

        Returns:
            Single vector if texts is str, otherwise array of vectors
        """
        try:
            is_single = isinstance(texts, str)
            texts_list = [texts] if is_single else texts

            embeddings = self.model.encode(
                texts_list,
                normalize_embeddings=normalize,
                batch_size=batch_size,
            )

            if not isinstance(embeddings, np.ndarray):
                embeddings = np.array(embeddings)

            return embeddings[0].tolist() if is_single else embeddings.tolist()

        except Exception as e:
            self.logger.error(f"Error encoding texts: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """Get vector dimension"""
        return self.model.get_sentence_embedding_dimension()


class EmbeddingPipeline:
    """Orchestrate text extraction → embedding → storage"""

    def __init__(self, embedding_model_name: str = "BAAI/bge-m3"):
        self.logger = logging.getLogger(__name__)
        self.embedder = EmbeddingModel(embedding_model_name)
        self.embedding_dim = self.embedder.get_embedding_dimension()
        self.logger.info(f"Embedding dimension: {self.embedding_dim}")

    def embed_document_pages(
        self,
        pages: list[PageInput],
        chunk_size: int = 500,
    ) -> list[EmbeddedChunk]:
        """
        Embed document pages, chunking long texts.

        Args:
            pages: List of {"page_number": int, "text": str, ...}
            chunk_size: Max characters per chunk

        Returns:
            List of {"page_number": int, "chunk_index": int, "text": str, "vector": [...]}
        """
        chunked_pages = []

        for page in pages:
            text = page.get("text", "")
            page_num = page.get("page_number", 0)

            chunks = self._chunk_text(text, chunk_size)

            vectors = self.embedder.encode([c["text"] for c in chunks])

            for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                chunked_pages.append({
                    "page_number": page_num,
                    "chunk_index": i,
                    "text": chunk["text"],
                    "char_range": chunk["char_range"],
                    "vector": vector,
                })

        self.logger.info(f"Embedded {len(chunked_pages)} chunks across {len(pages)} pages")
        return chunked_pages

    def embed_standards(
        self,
        standards: list[StandardInput],
    ) -> list[EmbeddedStandard]:
        """
        Embed Indian Standard definitions.

        Args:
            standards: List of {"code": "IS 1554", "title": "...", "definition": "..."}

        Returns:
            List of {"code": str, "title": str, "vector": [...]}
        """
        texts_to_embed = []
        for std in standards:
            combined_text = f"{std.get('code', '')} {std.get('title', '')} {std.get('definition', '')}"
            texts_to_embed.append(combined_text)

        vectors = self.embedder.encode(texts_to_embed)

        result = []
        for std, vector in zip(standards, vectors):
            result.append({
                "code": std.get("code"),
                "title": std.get("title"),
                "definition": std.get("definition"),
                "vector": vector,
            })

        self.logger.info(f"Embedded {len(result)} standards")
        return result

    def embed_boq_items(
        self,
        items: list[dict[str, str]],
    ) -> list[dict[str, str | list[float]]]:
        """
        Embed Bill of Quantities items.

        Args:
            items: List of {"name": str, "specification": str, ...}

        Returns:
            List of {"name": str, "specification": str, "vector": [...]}
        """
        texts = [
            f"{item.get('name', '')} {item.get('specification', '')}"
            for item in items
        ]

        vectors = self.embedder.encode(texts)

        result = []
        for item, vector in zip(items, vectors):
            result.append({**item, "vector": vector})

        return result

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[dict]:
        """Split text into overlapping chunks with validation"""
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if overlap >= chunk_size:
            raise ValueError(f"overlap ({overlap}) must be < chunk_size ({chunk_size})")

        chunks = []
        step = chunk_size - overlap

        i = 0
        while i < len(text):
            chunk_text = text[i : i + chunk_size]
            chunks.append({
                "text": chunk_text.strip(),
                "char_range": (i, i + len(chunk_text)),
            })
            if i + chunk_size >= len(text):
                break
            i += step

        return chunks

    def similarity_search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, str | float]]:
        """
        Find semantically similar documents.

        NOTE: Not yet implemented. Actual similarity search is delegated to
        Qdrant (see qdrant_schema.QdrantSchemaManager.search). This method
        exists as a documented seam for callers that want to embed a query
        and search without touching Qdrant directly — implement it once
        that wiring is in place.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            List of {"text": str, "similarity": float}

        Raises:
            NotImplementedError: always, until Qdrant search is wired in here.
        """
        raise NotImplementedError(
            "similarity_search is not implemented; use "
            "QdrantSchemaManager.search with an embedded query vector instead."
        )