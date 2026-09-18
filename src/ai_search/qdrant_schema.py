"""
Dev 3: Qdrant Vector Database Schema & Client
Initializes collections and manages vector embeddings for hybrid search
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    FieldCondition,
    MatchValue,
    Filter,
)

logger = logging.getLogger(__name__)


@dataclass
class QdrantConfig:
    """Configuration for Qdrant instance"""
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "indian_standards"
    vector_size: int = 1024  # bge-m3 embedding dimension
    distance_metric: Distance = Distance.COSINE


class QdrantSchemaManager:
    """Manage Qdrant collections and schema"""

    def __init__(self, config: QdrantConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = QdrantClient(
            host=config.host,
            port=config.port,
            prefer_grpc=False,
        )
        self.logger.info(f"Connected to Qdrant at {config.host}:{config.port}")

    def create_standards_collection(self) -> bool:
        """
        Create the main standards collection with vector embeddings.
        Payload schema:
        - standard_code: str (e.g., "IS 1554")
        - standard_title: str
        - standard_type: str (normative, testing, installation, etc.)
        - year_of_publication: int
        - amendment_number: int
        - is_active: bool
        - page_content: str (for full-text search)
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            if any(col.name == self.config.collection_name for col in collections.collections):
                self.logger.warning(f"Collection '{self.config.collection_name}' already exists")
                return False

            self.client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config=VectorParams(
                    size=self.config.vector_size,
                    distance=self.config.distance_metric,
                ),
            )

            # Add payload schema (metadata about vectors)
            self.logger.info(
                f"Created collection '{self.config.collection_name}' with "
                f"{self.config.vector_size}-dim vectors"
            )
            return True

        except Exception as exc:  
            self.logger.error("Error creating collection: %s", exc)
            raise

    def create_boq_items_collection(self) -> bool:
        """Create collection for extracted BOQ items"""
        try:
            collection_name = f"{self.config.collection_name}_boq_items"
            collections = self.client.get_collections()
            
            if any(col.name == collection_name for col in collections.collections):
                self.logger.warning(f"Collection '{collection_name}' already exists")
                return False

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.config.vector_size,
                    distance=self.config.distance_metric,
                ),
            )

            self.logger.info(f"Created BOQ items collection: {collection_name}")
            return True

        except Exception as exc:  
            self.logger.error("Error creating BOQ collection: %s", exc)
            raise

    def insert_vector(
        self,
        point_id: int,
        vector: List[float],
        payload: Dict[str, Any],
        collection_name: Optional[str] = None,
    ) -> bool:
        """Insert a single vector point"""
        collection = collection_name or self.config.collection_name
        
        try:
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
            self.client.upsert(
                collection_name=collection,
                points=[point],
            )
            return True
        except Exception as exc: 
            self.logger.error("Error inserting vector: %s", exc)
            return False

    def batch_insert_vectors(
        self,
        points: List[Dict[str, Any]],
        collection_name: Optional[str] = None,
    ) -> int:
        """
        Batch insert multiple vectors
        points format: [{"id": int, "vector": List[float], "payload": Dict}, ...]
        """
        collection = collection_name or self.config.collection_name
        
        try:
            point_structs = [
                PointStruct(
                    id=p["id"],
                    vector=p["vector"],
                    payload=p["payload"],
                )
                for p in points
            ]
            self.client.upsert(
                collection_name=collection,
                points=point_structs,
            )
            self.logger.info(f"Inserted {len(points)} vectors into {collection}")
            return len(points)
        except Exception as exc:  
            self.logger.error("Error in batch insert: %s", exc)
            return 0

    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        collection_name: Optional[str] = None,
        filters: Optional[Filter] = None,
    ) -> List[Dict[str, Any]]:
        """Search by vector similarity"""
        collection = collection_name or self.config.collection_name
        
        try:
            results = self.client.search(
                collection_name=collection,
                query_vector=query_vector,
                query_filter=filters,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                }
                for hit in results
            ]
        except Exception as exc: 
            self.logger.error("Error searching vectors: %s", exc)
            return []

    def filter_by_payload(
        self,
        field: str,
        value: Any,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Filter points by payload field with pagination"""
        collection = collection_name or self.config.collection_name
        
        try:
            all_points = []
            offset = None
            
            while True:
                results = self.client.scroll(
                    collection_name=collection,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key=field,
                                match=MatchValue(value=value),
                            )
                        ]
                    ),
                    limit=100,
                    offset=offset,
                    with_payload=True,
                )
                
                points, next_offset = results
                all_points.extend([
                    {
                        "id": point.id,
                        "payload": point.payload,
                    }
                    for point in points
                ])
                
                if next_offset is None:
                    break
                offset = next_offset
            
            return all_points
        
        except Exception as exc:  
            self.logger.error("Error filtering by payload: %s", exc)
            return []

    def get_collection_info(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get collection statistics"""
        collection = collection_name or self.config.collection_name
        
        try:
            info = self.client.get_collection(collection)
            return {
                "name": info.name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": str(info.config.params.vectors.distance),
                },
            }
        except Exception as exc:  
            self.logger.error("Error getting collection info: %s", exc)
            return {}

    def delete_collection(self, collection_name: Optional[str] = None) -> bool:
        """Delete a collection (use with caution!)"""
        collection = collection_name or self.config.collection_name
        
        try:
            self.client.delete_collection(collection)
            self.logger.warning(f"Deleted collection: {collection}")
            return True
        except Exception as exc:  
            self.logger.error("Error deleting collection: %s", exc)
            return False