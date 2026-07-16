"""FAISS Vector Store Service."""

import json
import logging
import pickle
from pathlib import Path
from typing import Optional

import faiss
import numpy as np

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """FAISS-based vector database for document embeddings."""
    
    def __init__(self, vector_dim: int = 384, index_type: str = "l2"):
        """
        Initialize FAISS vector store.
        
        Args:
            vector_dim: Embedding dimension
            index_type: Index type ("l2" for L2 distance, "ip" for inner product)
        """
        self.vector_dim = vector_dim
        self.index_type = index_type
        self.metadata = {}  # vector_id -> metadata mapping
        
        # Create index
        if index_type == "l2":
            self.index = faiss.IndexFlatL2(vector_dim)
        elif index_type == "ip":
            self.index = faiss.IndexFlatIP(vector_dim)
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        logger.info(f"FAISS index created: dim={vector_dim}, type={index_type}")
    
    def add_vectors(
        self,
        vectors: np.ndarray,
        metadata_list: Optional[list[dict]] = None,
    ) -> list[int]:
        """
        Add vectors to index.
        
        Args:
            vectors: Array of vectors (N, vector_dim)
            metadata_list: Optional list of metadata dicts for each vector
            
        Returns:
            List of vector IDs
        """
        if vectors.shape[1] != self.vector_dim:
            raise ValueError(f"Vector dimension mismatch: expected {self.vector_dim}, got {vectors.shape[1]}")
        
        # Ensure float32
        vectors = vectors.astype(np.float32)
        
        # Get starting ID
        start_id = self.index.ntotal
        
        # Add to index
        self.index.add(vectors)
        
        # Store metadata
        if metadata_list:
            for i, metadata in enumerate(metadata_list):
                vector_id = start_id + i
                self.metadata[vector_id] = metadata
        
        logger.info(f"Added {vectors.shape[0]} vectors to index (total: {self.index.ntotal})")
        return list(range(start_id, start_id + len(vectors)))
    
    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5,
        threshold: Optional[float] = None,
    ) -> tuple[list[int], list[float], list[dict]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector
            k: Number of results to return
            threshold: Optional distance threshold
            
        Returns:
            (vector_ids, distances, metadatas)
        """
        if query_vector.shape[0] != self.vector_dim:
            raise ValueError(f"Query dimension mismatch: expected {self.vector_dim}, got {query_vector.shape[0]}")
        
        # Ensure float32 and reshape
        query_vector = query_vector.astype(np.float32).reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_vector, k)
        
        distances = distances[0].tolist()
        indices = indices[0].tolist()
        
        # Filter by threshold
        if threshold is not None:
            mask = np.array(distances) < threshold
            distances = [d for d, m in zip(distances, mask) if m]
            indices = [i for i, m in zip(indices, mask) if m]
        
        # Get metadata
        metadatas = [self.metadata.get(int(i), {}) for i in indices]
        
        logger.info(f"Search returned {len(indices)} results")
        return indices, distances, metadatas
    
    def save(self, path: str | Path) -> None:
        """
        Save index and metadata to disk.
        
        Args:
            path: Directory to save to
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = path / "index.faiss"
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        metadata_path = path / "metadata.json"
        # Convert int keys to strings for JSON
        metadata_to_save = {str(k): v for k, v in self.metadata.items()}
        with open(metadata_path, "w") as f:
            json.dump(metadata_to_save, f)
        
        logger.info(f"FAISS index saved to {path}")
    
    @classmethod
    def load(cls, path: str | Path) -> "FAISSVectorStore":
        """
        Load index and metadata from disk.
        
        Args:
            path: Directory to load from
            
        Returns:
            FAISSVectorStore instance
        """
        path = Path(path)
        
        # Load FAISS index
        index_path = path / "index.faiss"
        index = faiss.read_index(str(index_path))
        
        # Load metadata
        metadata_path = path / "metadata.json"
        with open(metadata_path, "r") as f:
            metadata_raw = json.load(f)
        # Convert string keys back to ints
        metadata = {int(k): v for k, v in metadata_raw.items()}
        
        # Create instance
        vector_store = cls(vector_dim=index.d)
        vector_store.index = index
        vector_store.metadata = metadata
        
        logger.info(f"FAISS index loaded from {path}")
        return vector_store
    
    def get_stats(self) -> dict:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.vector_dim,
            "index_type": self.index_type,
            "metadata_count": len(self.metadata),
        }
