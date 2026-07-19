"""Background task processing for document OCR pipeline."""

import asyncio
import logging
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.document import Document
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.ocr_service import OCRService
from app.services.text_cleaning_service import TextCleaningService
from app.services.vectorstore_service import FAISSVectorStore
from app.services.document_processing_pipeline import DocumentProcessingPipeline
from app.database.session import SessionLocal

logger = logging.getLogger(__name__)


async def process_document_background(document_id: uuid.UUID):
    """
    Process document through entire OCR → Clean → Chunk → Embed pipeline.
    Runs asynchronously in background.
    """
    db = SessionLocal()
    try:
        # Get document
        doc = db.query(Document).filter_by(document_id=document_id).first()
        if not doc:
            logger.error(f"Document not found: {document_id}")
            return

        # Update status to processing
        doc.status = "PROCESSING"
        db.commit()

        logger.info(f"Starting document processing: {document_id}")

        settings = get_settings()

        # Initialize services
        ocr_service = OCRService(languages=[settings.ocr_language])
        cleaning_service = TextCleaningService()
        chunking_service = ChunkingService(chunk_size=512, chunk_overlap=128)
        embedding_service = EmbeddingService(
            model_name=settings.embedding_model,
            device="cpu",
        )

        # Initialize vector store (will be shared for this session)
        vectorstore_path = Path(settings.vectorstore_path) / str(document_id)
        vector_store = FAISSVectorStore(
            vector_dim=embedding_service.embedding_dim,
            index_type="l2",
        )

        # Run pipeline
        pipeline = DocumentProcessingPipeline(
            db=db,
            ocr_service=ocr_service,
            cleaning_service=cleaning_service,
            chunking_service=chunking_service,
            embedding_service=embedding_service,
            vector_store=vector_store,
        )

        results = pipeline.process_document(document_id, doc.file_path)

        # Save vector store
        vectorstore_path.mkdir(parents=True, exist_ok=True)
        vector_store.save(vectorstore_path)

        # Update document with results
        doc.status = "READY"
        doc.total_pages = results.get("pages_processed", 0)
        db.commit()

        logger.info(f"Document processing complete: {results}")

    except Exception as e:
        logger.exception(f"Document processing failed: {e}")
        doc = db.query(Document).filter_by(document_id=document_id).first()
        if doc:
            doc.status = "FAILED"
            db.commit()
    finally:
        db.close()


def start_ocr_processing(document_id: uuid.UUID):
    """
    Trigger background OCR processing.
    Can be called from upload endpoint.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(process_document_background(document_id))
    except RuntimeError:
        asyncio.run(process_document_background(document_id))
