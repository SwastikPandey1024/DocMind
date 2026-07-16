"""Embedding service using SentenceTransformers (BGE)."""

import hashlib
import logging
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings using SentenceTransformers."""
    
    # Recommended models
    MODELS = {
        "bge-small": "BAAI/bge-small-en-v1.5",
        "bge-base": "BAAI/bge-base-en-v1.5",
        "bge-large": "BAAI/bge-large-en-v1.5",
        "all-minilm": "sentence-transformers/all-MiniLM-L6-v2",
    }
    
    def __init__(
        self,
        model_name: str = "bge-small",
        device: str = "cpu",
        batch_size: int = 32,
    ):
        """
        Initialize embedding service.
        
        Args:
            model_name: Model key or full HuggingFace model name
            device: Device to use ("cpu" or "cuda")
            batch_size: Batch size for embedding
        """
        # Resolve model name
        if model_name in self.MODELS:
            self.model_name_full = self.MODELS[model_name]
            self.model_key = model_name
        else:
            self.model_name_full = model_name
            self.model_key = model_name
        
        logger.info(f"Loading embedding model: {self.model_name_full}")
        self.model = SentenceTransformer(self.model_name_full, device=device)
        self.device = device
        self.batch_size = batch_size
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"Model loaded: dimension={self.embedding_dim}, device={device}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)
    
    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """
        Embed multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Array of embeddings
        """
        logger.info(f"Embedding {len(texts)} texts")
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embeddings.astype(np.float32)
    
    def get_embedding_metadata(self) -> dict:
        """Get embedding model metadata."""
        return {
            "model": self.model_key,
            "model_full_name": self.model_name_full,
            "dimension": self.embedding_dim,
            "device": self.device,
        }
    
    def create_embedding_key(self, text: str, model_name: Optional[str] = None) -> str:
        """
        Create deterministic embedding key (for caching/deduplication).
        
        Args:
            text: Text to create key for
            model_name: Model name (defaults to current model)
            
        Returns:
            Embedding key hash
        """
        model = model_name or self.model_key
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"{model}_{text_hash}"
