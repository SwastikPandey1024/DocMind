"""Text chunking service with recursive splitting."""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """A single text chunk with metadata."""
    chunk_id: Optional[str] = None
    document_id: Optional[str] = None
    page_number: int = 0
    chunk_index: int = 0
    text: str = ""
    token_count: int = 0
    start_char: int = 0
    end_char: int = 0


class ChunkingService:
    """Split text into chunks with overlap and metadata."""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 128,
        separator_hierarchy: Optional[list[str]] = None,
    ):
        """
        Initialize chunking service.
        
        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            separator_hierarchy: List of separators to try in order (sentences, paragraphs, etc.)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator_hierarchy = separator_hierarchy or ["\n\n", "\n", ". ", " "]
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token count (1 token ≈ 4 chars)."""
        return len(text) // 4
    
    def split_recursive(
        self,
        text: str,
        separators: Optional[list[str]] = None,
    ) -> list[str]:
        """
        Recursively split text using separator hierarchy.
        
        Args:
            text: Text to split
            separators: Separators to try in order
            
        Returns:
            List of text chunks
        """
        if separators is None:
            separators = self.separator_hierarchy
        
        logger.debug(f"Splitting text: {len(text)} chars, {self.estimate_tokens(text)} tokens")
        
        good_splits = []
        separator = separators[-1]
        
        for i, s in enumerate(separators):
            if s == "":
                separator = s
                break
            
            if s in text:
                separator = s
                break
        
        # Split by separator
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)
        
        # Recursively merge splits if needed
        merged_splits = []
        separator_text = ""
        
        for s in splits:
            if len(s) < self.chunk_size:
                if merged_splits and len(merged_splits[-1] + separator + s) <= self.chunk_size:
                    merged_splits[-1] += separator + s
                else:
                    merged_splits.append(s)
            else:
                if merged_splits:
                    merged_text = separator.join(merged_splits)
                    if len(merged_text) > self.chunk_size:
                        # Recursively split if still too large
                        good_splits.extend(self.split_recursive(
                            merged_text,
                            separators[separators.index(separator) + 1:],
                        ))
                    else:
                        good_splits.append(merged_text)
                    merged_splits = []
                
                # Recursively split large split
                good_splits.extend(self.split_recursive(s, separators[separators.index(separator) + 1:]))
        
        if merged_splits:
            merged_text = separator.join(merged_splits)
            good_splits.append(merged_text)
        
        return [s.strip() for s in good_splits if s.strip()]
    
    def create_chunks(
        self,
        text: str,
        document_id: Optional[str] = None,
        page_number: int = 0,
        metadata: Optional[dict] = None,
    ) -> list[Chunk]:
        """
        Create chunks with overlap.
        
        Args:
            text: Text to chunk
            document_id: Document ID for metadata
            page_number: Page number for metadata
            metadata: Additional metadata
            
        Returns:
            List of Chunk objects
        """
        logger.info(f"Creating chunks: {len(text)} chars")
        
        # Split text
        splits = self.split_recursive(text)
        logger.info(f"Created {len(splits)} initial splits")
        
        # Merge and create chunks with overlap
        chunks = []
        current_chunk = ""
        chunk_index = 0
        char_position = 0
        
        for split in splits:
            if len(current_chunk) + len(split) + 1 <= self.chunk_size:
                current_chunk += split + " "
            else:
                # Save current chunk
                if current_chunk.strip():
                    chunk_text = current_chunk.strip()
                    chunk = Chunk(
                        document_id=document_id,
                        page_number=page_number,
                        chunk_index=chunk_index,
                        text=chunk_text,
                        token_count=self.estimate_tokens(chunk_text),
                        start_char=char_position,
                        end_char=char_position + len(chunk_text),
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    char_position += len(chunk_text) + 1
                
                # Start new chunk with overlap
                current_chunk = split + " "
        
        # Add final chunk
        if current_chunk.strip():
            chunk_text = current_chunk.strip()
            chunk = Chunk(
                document_id=document_id,
                page_number=page_number,
                chunk_index=chunk_index,
                text=chunk_text,
                token_count=self.estimate_tokens(chunk_text),
                start_char=char_position,
                end_char=char_position + len(chunk_text),
            )
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def chunk_document(
        self,
        text: str,
        page_texts: Optional[dict[int, str]] = None,
        document_id: Optional[str] = None,
    ) -> list[Chunk]:
        """
        Chunk entire document with page awareness.
        
        Args:
            text: Full document text
            page_texts: Optional mapping of page_number -> text
            document_id: Document ID
            
        Returns:
            List of chunks for entire document
        """
        if page_texts:
            # Chunk per-page, then combine
            all_chunks = []
            for page_num, page_text in page_texts.items():
                page_chunks = self.create_chunks(
                    page_text,
                    document_id=document_id,
                    page_number=page_num,
                )
                all_chunks.extend(page_chunks)
            return all_chunks
        else:
            # Chunk full document
            return self.create_chunks(
                text,
                document_id=document_id,
                page_number=0,
            )
