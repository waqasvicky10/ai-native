# Qdrant vector database client configuration
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import os
from typing import List, Dict, Any, Optional
import uuid
import numpy as np

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

class VectorDBManager:
    """Qdrant vector database manager for RAG functionality."""
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=30
        )
        self.collection_name = "textbook_content"
        self.vector_size = 1536  # OpenAI text-embedding-ada-002 dimension
        
    async def initialize_collection(self):
        """Initialize the vector collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {self.collection_name}")
            else:
                print(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            print(f"Error initializing collection: {e}")
            raise
    
    async def add_document(
        self,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Add a document to the vector database.
        
        Args:
            content: The text content
            embedding: Vector embedding of the content
            metadata: Additional metadata (chapter_id, section, etc.)
            
        Returns:
            Document ID
        """
        doc_id = str(uuid.uuid4())
        
        point = PointStruct(
            id=doc_id,
            vector=embedding,
            payload={
                "content": content,
                "metadata": metadata,
                **metadata  # Flatten metadata for easier filtering
            }
        )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        return doc_id
    
    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector embedding
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter_conditions: Optional filters (e.g., {"chapter_id": "chapter1"})
            
        Returns:
            List of similar documents with scores
        """
        search_filter = None
        if filter_conditions:
            # Build Qdrant filter
            conditions = []
            for key, value in filter_conditions.items():
                conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    )
                )
            
            if conditions:
                search_filter = models.Filter(
                    must=conditions
                )
        
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=limit,
            score_threshold=score_threshold
        )
        
        results = []
        for hit in search_result:
            results.append({
                "id": hit.id,
                "score": hit.score,
                "content": hit.payload.get("content", ""),
                "metadata": hit.payload.get("metadata", {}),
                **{k: v for k, v in hit.payload.items() if k not in ["content", "metadata"]}
            })
        
        return results
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the vector database.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[doc_id]
                )
            )
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False
    
    async def update_document(
        self,
        doc_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update an existing document.
        
        Args:
            doc_id: Document ID to update
            content: New content
            embedding: New embedding
            metadata: New metadata
            
        Returns:
            True if successful
        """
        try:
            point = PointStruct(
                id=doc_id,
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": metadata,
                    **metadata
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            return True
        except Exception as e:
            print(f"Error updating document {doc_id}: {e}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.params.vectors.size,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Check if Qdrant is healthy."""
        try:
            collections = self.client.get_collections()
            return True
        except Exception as e:
            print(f"Qdrant health check failed: {e}")
            return False

# Global vector database instance
vector_db = VectorDBManager()