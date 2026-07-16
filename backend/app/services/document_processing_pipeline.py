"""Document processing pipeline (OCR -> Clean -> Chunk -> Embed)."""

import json
import logging
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.chunk import Chunk, EmbeddingMetadata
from app.models.ocr_text import OCRText
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.ocr_service import OCRService
from app.services.text_cleaning_service import TextCleaningService
from app.services.vectorstore_service import FAISSVectorStore

logger = logging.getLogger(__name__)


class DocumentProcessingPipeline:
    """End-to-end document processing: OCR -> Clean -> Chunk -> Embed."""
    
    def __init__(
        self,
        db: Session,
        ocr_service: OCRService,
        cleaning_service: TextCleaningService,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        vector_store: FAISSVectorStore,
    ):
        self.db = db
        self.ocr_service = ocr_service
        self.cleaning_service = cleaning_service
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store
    
    def process_document(
        self,
        document_id: uuid.UUID,
        file_path: str | Path,
    ) -> dict:
        """
        Process document through entire pipeline.
        
        Args:
            document_id: Document ID
            file_path: Path to PDF file
            
        Returns:
            Processing results dict
        """
        logger.info(f"Starting document processing: {document_id}")
        results = {
            "document_id": str(document_id),
            "pages_processed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
        }
        
        try:
            # STEP 1: OCR
            logger.info("Step 1: Extracting text via OCR")
            ocr_pages = self.ocr_service.extract_from_pdf(file_path)
            results["pages_processed"] = len(ocr_pages)
            logger.info(f"Extracted {len(ocr_pages)} pages")
            
            # Store OCR results
            all_chunks = []
            all_embeddings = []
            all_metadata = []
            
            for ocr_page in ocr_pages:
                # Store raw OCR
                blocks_data = [
                    {
                        "block_index": block.block_index,
                        "text": block.text,
                        "confidence": block.confidence,
                        "bbox": block.bbox,
                        "reading_order": block.reading_order,
                    }
                    for block in ocr_page.blocks
                ]
                
                ocr_text = OCRText(
                    document_id=document_id,
                    page_number=ocr_page.page_number,
                    raw_text=ocr_page.page_text,
                    block_count=len(ocr_page.blocks),
                    blocks_json=blocks_data,
                    detected_language=ocr_page.detected_language,
                )
                self.db.add(ocr_text)
                
                # STEP 2: Clean text
                logger.info(f"Step 2: Cleaning text for page {ocr_page.page_number + 1}")
                clean_text = self.cleaning_service.clean_text(ocr_page.page_text)
                ocr_text.clean_text = clean_text
                
                # STEP 3: Chunk
                logger.info(f"Step 3: Chunking page {ocr_page.page_number + 1}")
                page_chunks = self.chunking_service.create_chunks(
                    clean_text,
                    document_id=document_id,
                    page_number=ocr_page.page_number,
                )
                
                # Prepare for embeddings
                chunk_texts = [chunk.text for chunk in page_chunks]
                
                # STEP 4: Embed
                logger.info(f"Step 4: Generating embeddings for {len(chunk_texts)} chunks")
                embeddings = self.embedding_service.embed_texts(chunk_texts)
                
                # Store chunks and embeddings
                for chunk_obj, embedding in zip(page_chunks, embeddings):
                    # Get or create embedding metadata
                    embedding_key = self.embedding_service.create_embedding_key(
                        chunk_obj.text
                    )
                    
                    # Check if embedding metadata exists
                    embedding_meta = self.db.query(EmbeddingMetadata).filter_by(
                        embedding_key=embedding_key
                    ).first()
                    
                    if not embedding_meta:
                        embedding_meta = EmbeddingMetadata(
                            embedding_key=embedding_key,
                            model_name=self.embedding_service.model_key,
                            dimension=self.embedding_service.embedding_dim,
                        )
                        self.db.add(embedding_meta)
                    
                    # Create chunk
                    chunk = Chunk(
                        document_id=document_id,
                        chunk_index=chunk_obj.chunk_index,
                        page_number=chunk_obj.page_number,
                        chunk_text=chunk_obj.text,
                        embedding_key=embedding_key,
                        token_count=chunk_obj.token_count,
                        start_char=chunk_obj.start_char,
                        end_char=chunk_obj.end_char,
                    )
                    self.db.add(chunk)
                    
                    # Add to vector store
                    metadata = {
                        "document_id": str(document_id),
                        "chunk_index": chunk_obj.chunk_index,
                        "page_number": chunk_obj.page_number,
                        "text": chunk_obj.text,
                        "embedding_key": embedding_key,
                    }
                    all_embeddings.append(embedding)
                    all_metadata.append(metadata)
                    all_chunks.append(chunk)
            
            # Commit to database
            self.db.commit()
            
            # Add to vector store (after commit to ensure IDs are assigned)
            if all_embeddings:
                import numpy as np
                embeddings_array = np.array(all_embeddings)
                self.vector_store.add_vectors(embeddings_array, all_metadata)
                results["embeddings_generated"] = len(all_embeddings)
            
            results["chunks_created"] = len(all_chunks)
            
            logger.info(f"Document processing complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            self.db.rollback()
            raise
