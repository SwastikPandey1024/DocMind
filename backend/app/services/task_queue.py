"""Background task management for async document processing."""

import logging
from enum import Enum
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.ocr_service import OCRService
from app.services.text_cleaning_service import TextCleaningService
from app.services.vectorstore_service import FAISSVectorStore
from app.services.document_processing_pipeline import DocumentProcessingPipeline

logger = logging.getLogger(__name__)


class ProcessingStatus(str, Enum):
    """Document processing status."""
    PENDING = "PENDING"
    EXTRACTING = "EXTRACTING"
    CLEANING = "CLEANING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


async def process_document_async(
    db: Session,
    document_id: UUID,
    file_path: str | Path,
    ocr_service: OCRService,
    cleaning_service: TextCleaningService,
    chunking_service: ChunkingService,
    embedding_service: EmbeddingService,
    vector_store: FAISSVectorStore,
) -> bool:
    """
    Process document asynchronously.
    
    Args:
        db: Database session
        document_id: Document ID
        file_path: Path to PDF file
        ocr_service: OCR service
        cleaning_service: Text cleaning service
        chunking_service: Chunking service
        embedding_service: Embedding service
        vector_store: Vector store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Update document status
        doc = db.query(Document).filter_by(document_id=document_id).first()
        if not doc:
            logger.error(f"Document not found: {document_id}")
            return False
        
        # Create pipeline
        pipeline = DocumentProcessingPipeline(
            db=db,
            ocr_service=ocr_service,
            cleaning_service=cleaning_service,
            chunking_service=chunking_service,
            embedding_service=embedding_service,
            vector_store=vector_store,
        )
        
        # Process
        results = pipeline.process_document(document_id, file_path)
        
        # Update document
        doc.status = "READY"
        doc.total_pages = results.get("pages_processed", 0)
        db.commit()
        
        logger.info(f"Document processing complete: {results}")
        return True
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        doc = db.query(Document).filter_by(document_id=document_id).first()
        if doc:
            doc.status = "FAILED"
            db.commit()
        return False
