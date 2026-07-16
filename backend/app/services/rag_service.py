"""RAG Service for retrieval-augmented generation."""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import FAISSVectorStore

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Single retrieval result."""
    rank: int
    text: str
    distance: float
    similarity_score: float  # 0-1, normalized
    metadata: dict


class RAGService:
    """Retrieval-Augmented Generation service."""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: Optional[FAISSVectorStore] = None,
    ):
        """
        Initialize RAG service.
        
        Args:
            embedding_service: EmbeddingService instance
            vector_store: Optional FAISSVectorStore (created if None)
        """
        self.embedding_service = embedding_service
        self.vector_store = vector_store or FAISSVectorStore(
            vector_dim=embedding_service.embedding_dim
        )
        
        logger.info("RAG service initialized")
    
    def add_documents(
        self,
        texts: list[str],
        metadata_list: list[dict],
    ) -> list[int]:
        """
        Add documents to vector store.
        
        Args:
            texts: List of document chunks
            metadata_list: List of metadata dicts (must include 'document_id', 'chunk_index', 'text')
            
        Returns:
            List of vector IDs
        """
        logger.info(f"Adding {len(texts)} documents to vector store")
        
        # Generate embeddings
        embeddings = self.embedding_service.embed_texts(texts)
        
        # Add to vector store
        vector_ids = self.vector_store.add_vectors(embeddings, metadata_list)
        
        logger.info(f"Added {len(vector_ids)} documents")
        return vector_ids
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant documents for query.
        
        Args:
            query: Query text
            k: Number of results
            score_threshold: Optional threshold for similarity (0-1)
            
        Returns:
            List of RetrievalResult objects
        """
        logger.info(f"Retrieving {k} documents for query: {query[:100]}")
        
        # Embed query
        query_embedding = self.embedding_service.embed_text(query)
        
        # Search vector store
        vector_ids, distances, metadatas = self.vector_store.search(
            query_embedding,
            k=k,
            threshold=None,  # We'll filter by normalized score
        )
        
        # Normalize distances to similarity scores (0-1)
        # For L2: similarity = 1 / (1 + distance)
        # For IP: similarity = (distance + 1) / 2 (distance is already normalized to [-1, 1])
        results = []
        for rank, (vector_id, distance, metadata) in enumerate(zip(vector_ids, distances, metadatas)):
            if self.vector_store.index_type == "l2":
                # L2 distance: lower is better
                similarity_score = 1.0 / (1.0 + distance)
            else:  # ip
                # Inner product: higher is better, range [-1, 1]
                similarity_score = (distance + 1.0) / 2.0
            
            # Filter by threshold
            if score_threshold and similarity_score < score_threshold:
                continue
            
            result = RetrievalResult(
                rank=rank,
                text=metadata.get("text", ""),
                distance=float(distance),
                similarity_score=float(similarity_score),
                metadata=metadata,
            )
            results.append(result)
        
        logger.info(f"Retrieved {len(results)} documents")
        return results
    
    def build_context(
        self,
        results: list[RetrievalResult],
        include_scores: bool = False,
    ) -> str:
        """
        Build context string from retrieval results.
        
        Args:
            results: List of RetrievalResult objects
            include_scores: Include similarity scores in output
            
        Returns:
            Context string
        """
        context_parts = []
        
        for result in results:
            source = f"[Doc: {result.metadata.get('document_id', 'unknown')}, Chunk: {result.metadata.get('chunk_index', 'unknown')}]"
            
            if include_scores:
                source += f" (similarity: {result.similarity_score:.2%})"
            
            context_parts.append(f"{source}\n{result.text}")
        
        return "\n\n".join(context_parts)
    
    def build_rag_context_and_citations(
        self,
        results: list[RetrievalResult],
    ) -> tuple[str, list[dict]]:
        """
        Build context and extract citations.
        
        Args:
            results: List of RetrievalResult objects
            
        Returns:
            (context_string, citations_list)
        """
        context = self.build_context(results, include_scores=False)
        
        citations = []
        for result in results:
            citation = {
                "document_id": result.metadata.get("document_id"),
                "chunk_index": result.metadata.get("chunk_index"),
                "page_number": result.metadata.get("page_number"),
                "similarity_score": result.similarity_score,
                "snippet": result.text[:200],  # First 200 chars as snippet
            }
            citations.append(citation)
        
        return context, citations
    
    def get_stats(self) -> dict:
        """Get RAG service statistics."""
        vector_store_stats = self.vector_store.get_stats()
        embedding_stats = self.embedding_service.get_embedding_metadata()
        
        return {
            **vector_store_stats,
            **embedding_stats,
        }
