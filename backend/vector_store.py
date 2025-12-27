"""
Vector store interface using Qdrant for RAG.
Supports both local and cloud Qdrant instances.
"""

import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, SearchParams, VectorParams
from sentence_transformers import SentenceTransformer


@dataclass
class SearchResult:
    """Represents a search result from the vector store."""

    content: str
    source: str
    score: float
    chunk_id: str
    metadata: Dict[str, Any]


class VectorStore:
    """
    Vector store interface for document retrieval.
    Uses Qdrant for efficient vector search.
    """

    def __init__(
        self,
        collection_name: str = "aigenbook_chunks",
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
    ):
        self.collection_name = collection_name

        # Initialize Qdrant client
        if qdrant_url:
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
            )
        else:
            # In-memory mode for development/testing
            self.client = QdrantClient(":memory:")

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(
            embedding_model,
            device=device,
        )
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # Ensure collection exists
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the collection exists with proper configuration."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            print(f"Created collection: {self.collection_name}")

    def add_documents(
        self,
        documents: List[Any],
        collection_name: Optional[str] = None,
        batch_size: int = 100,
    ):
        """
        Add documents to the vector store.

        Args:
            documents: List of TextChunk objects
            collection_name: Override collection name
            batch_size: Batch size for indexing
        """
        coll_name = collection_name or self.collection_name

        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]

            # Generate embeddings
            texts = [doc.content for doc in batch]
            embeddings = self.embedding_model.encode(texts).tolist()

            # Create points
            points = []
            for j, (doc, embedding) in enumerate(zip(batch, embeddings)):
                point_id = str(uuid.uuid4())

                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "content": doc.content,
                        "source": doc.source,
                        "chunk_id": doc.chunk_id,
                        "section_title": doc.section_title,
                        "start_char": doc.start_char,
                        "end_char": doc.end_char,
                    },
                )
                points.append(point)

            # Upload to Qdrant
            self.client.upsert(
                collection_name=coll_name,
                points=points,
            )

        print(f"Added {len(documents)} documents to {coll_name}")

    def search(
        self,
        query: str,
        k: int = 5,
        collection_name: Optional[str] = None,
        score_threshold: Optional[float] = None,
    ) -> List[SearchResult]:
        """
        Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return
            collection_name: Override collection name
            score_threshold: Minimum similarity score

        Returns:
            List of SearchResult objects
        """
        coll_name = collection_name or self.collection_name

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]

        # Search
        search_params = SearchParams(hnsw_ef=128, exact=False)

        results = self.client.search(
            collection_name=coll_name,
            query_vector=query_embedding,
            limit=k,
            score_threshold=score_threshold,
            query_params=search_params,
        )

        # Convert to SearchResult objects
        search_results = []
        for hit in results:
            result = SearchResult(
                content=hit.payload.get("content", ""),
                source=hit.payload.get("source", ""),
                score=hit.score,
                chunk_id=hit.payload.get("chunk_id", ""),
                metadata={
                    "section_title": hit.payload.get("section_title", ""),
                    "start_char": hit.payload.get("start_char", 0),
                    "end_char": hit.payload.get("end_char", 0),
                },
            )
            search_results.append(result)

        return search_results

    def search_by_source(
        self,
        query: str,
        source: str,
        k: int = 5,
    ) -> List[SearchResult]:
        """
        Search within a specific source document.

        Args:
            query: Search query
            source: Source document path
            k: Number of results

        Returns:
            List of SearchResult objects
        """
        coll_name = self.collection_name

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]

        # Search with filter
        results = self.client.search(
            collection_name=coll_name,
            query_vector=query_embedding,
            limit=k,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=source),
                    )
                ]
            ),
        )

        return [
            SearchResult(
                content=hit.payload.get("content", ""),
                source=hit.payload.get("source", ""),
                score=hit.score,
                chunk_id=hit.payload.get("chunk_id", ""),
                metadata={},
            )
            for hit in results
        ]

    def delete_by_source(self, source: str) -> int:
        """
        Delete all documents from a specific source.

        Args:
            source: Source document path

        Returns:
            Number of deleted points
        """
        result = self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=source),
                    )
                ]
            ),
        )

        return result.operation_idx if hasattr(result, "operation_idx") else 0

    def get_collection_stats(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about the collection."""
        coll_name = collection_name or self.collection_name

        try:
            info = self.client.get_collection(coll_name)
            return {
                "collection_name": coll_name,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "status": str(info.status),
            }
        except Exception as e:
            return {"error": str(e)}

    def count_documents(self, collection_name: Optional[str] = None) -> int:
        """Get total number of documents."""
        coll_name = collection_name or self.collection_name

        try:
            info = self.client.get_collection(coll_name)
            return info.points_count or 0
        except Exception:
            return 0

    def close(self):
        """Close the vector store connection."""
        if hasattr(self.client, "close"):
            self.client.close()
