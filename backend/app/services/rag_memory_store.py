"""RAG Memory Store - manages document-specific vector stores and retrieval."""

import json
import logging
from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import FAISSVectorStore

logger = logging.getLogger(__name__)


class RAGMemoryStore:
    """
    Manages FAISS vector stores per document.
    Loads from disk if exists, creates new if not.
    """

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.settings = get_settings()
        self._stores: dict[str, FAISSVectorStore] = {}  # Cache in memory

    def get_store(self, document_id: str) -> FAISSVectorStore:
        """
        Get or load vector store for document.
        
        Args:
            document_id: Document UUID
            
        Returns:
            FAISSVectorStore instance
        """
        # Check memory cache
        if document_id in self._stores:
            return self._stores[document_id]

        # Try to load from disk
        vectorstore_path = Path(self.settings.vectorstore_path) / document_id
        if vectorstore_path.exists():
            try:
                logger.info(f"Loading vector store from disk: {document_id}")
                store = FAISSVectorStore.load(vectorstore_path)
                self._stores[document_id] = store
                return store
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")
                # Continue to create new one

        # Create new store
        logger.info(f"Creating new vector store: {document_id}")
        store = FAISSVectorStore(
            vector_dim=self.embedding_service.embedding_dim,
            index_type="l2",
        )
        self._stores[document_id] = store
        return store

    def save_store(self, document_id: str, store: FAISSVectorStore) -> None:
        """Save vector store to disk."""
        vectorstore_path = Path(self.settings.vectorstore_path) / document_id
        vectorstore_path.mkdir(parents=True, exist_ok=True)
        store.save(vectorstore_path)
        logger.info(f"Vector store saved: {document_id}")

    def add_document_to_store(
        self,
        document_id: str,
        texts: list[str],
        metadata_list: list[dict],
    ) -> None:
        """Add document chunks to vector store."""
        store = self.get_store(document_id)

        # Generate embeddings
        embeddings = self.embedding_service.embed_texts(texts)

        # Add to store
        store.add_vectors(embeddings, metadata_list)

        # Persist
        self.save_store(document_id, store)

        logger.info(f"Added {len(texts)} vectors to store: {document_id}")

    def search_document(
        self,
        document_id: str,
        query: str,
        k: int = 5,
    ) -> tuple[list[str], list[float], list[dict]]:
        """
        Search document's vector store.
        
        Args:
            document_id: Document UUID
            query: Search query
            k: Number of results
            
        Returns:
            (vector_ids, distances, metadatas)
        """
        store = self.get_store(document_id)

        # Embed query
        query_embedding = self.embedding_service.embed_text(query)

        # Search
        vector_ids, distances, metadatas = store.search(query_embedding, k=k)

        return vector_ids, distances, metadatas

    def clear_memory(self, document_id: Optional[str] = None) -> None:
        """Clear in-memory cache."""
        if document_id:
            if document_id in self._stores:
                del self._stores[document_id]
        else:
            self._stores.clear()
