"""Document service with OCR pipeline integration."""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass

from fastapi import HTTPException, status
from fastapi.datastructures import UploadFile

from app.models.document import Document
from app.repositories.document import DocumentRepository
from app.services.document_validator import DocumentValidator
from app.services.storage_service import StorageService
from app.services.ocr_pipeline import start_ocr_processing

logger = logging.getLogger("docmind")


@dataclass(frozen=True)
class UploadMeta:
    mime_type: str
    size_bytes: int
    checksum_sha256: str


class DocumentService:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        storage_service: StorageService,
        validator: DocumentValidator,
    ) -> None:
        self.document_repository = document_repository
        self.storage_service = storage_service
        self.validator = validator

    def upload_pdf(self, *, user_id: uuid.UUID, file: UploadFile) -> Document:
        """Upload PDF and trigger OCR pipeline."""

        if file.content_type is None and not file.filename:
            raise HTTPException(status_code=422, detail="Invalid upload.")

        try:
            file_bytes = file.file.read()
            size_bytes = len(file_bytes)
            if size_bytes == 0:
                raise ValueError("Uploaded file is empty.")

            # Validate
            meta = self.validator.validate_pdf(
                filename=file.filename or "upload.pdf",
                content_type=file.content_type,
                size_bytes=size_bytes,
            )

            checksum_sha256 = hashlib.sha256(file_bytes).hexdigest()
            meta_all = UploadMeta(
                mime_type=meta.mime_type,
                size_bytes=meta.size_bytes,
                checksum_sha256=checksum_sha256,
            )

            # Duplicate detection
            print("=" * 60)
            print("USER :", user_id)
            print("CHECKSUM :", meta_all.checksum_sha256)
            existing = self.document_repository.get_by_user_and_checksum(
                  user_id=user_id,
                  checksum=meta_all.checksum_sha256,
            )
            print("EXISTING :", existing)
            print("=" * 60)

            if existing is not None:
                logger.info(
                    "document.upload.duplicate",
                    extra={"user_id": str(user_id), "document_id": str(existing.document_id)},
                )
                return existing

            document_id = uuid.uuid4()

            # Save file
            from io import BytesIO

            dest_path, _mime_type = self.storage_service.save_upload(
                fileobj=BytesIO(file_bytes),
                user_id=user_id,
                document_id=document_id,
                original_filename=file.filename or f"{document_id}.pdf",
                mime_type=meta_all.mime_type,
            )

            # Create document record with PROCESSING status
            doc = self.document_repository.create(
                obj_in={
                    "document_id": document_id,
                    "user_id": user_id,
                    "file_name": file.filename or f"{document_id}.pdf",
                    "file_path": str(dest_path),
                    "status": "PROCESSING",  # Will be updated by OCR pipeline
                    "total_pages": None,
                    "mime_type": meta_all.mime_type,
                    "file_size": meta_all.size_bytes,
                    "checksum_sha256": meta_all.checksum_sha256,
                }
            )

            logger.info(
                "document.upload.success",
                extra={"user_id": str(user_id), "document_id": str(doc.document_id)},
            )

            # Trigger OCR processing in background
            try:
                start_ocr_processing(document_id)
                logger.info(f"OCR processing started: {document_id}")
            except Exception as e:
                logger.error(f"Failed to start OCR processing: {e}")
                # Continue anyway - user can retry

            return doc

        except ValueError as exc:
            logger.warning(
                "document.upload.failure.validation",
                extra={"user_id": str(user_id), "error": str(exc)},
            )
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception(
                "document.upload.failure",
                extra={"user_id": str(user_id)},
            )
            raise HTTPException(status_code=500, detail="Failed to upload document.") from exc

    def list_user_documents(self, *, user_id: uuid.UUID, offset: int = 0, limit: int = 100) -> list[Document]:
        """List user's documents."""
        return self.document_repository.list_by_user(user_id=user_id, offset=offset, limit=limit)

    def get_user_document(self, *, user_id: uuid.UUID, document_id: uuid.UUID) -> Document:
        """Get single document."""
        doc = self.document_repository.get_by_user_and_id(user_id=user_id, document_id=document_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found.")
        return doc

    def delete_user_document(self, *, user_id: uuid.UUID, document_id: uuid.UUID) -> None:
        """Delete document (soft delete)."""
        doc = self.get_user_document(user_id=user_id, document_id=document_id)
        self.document_repository.delete(db_obj=doc)
        logger.info(
            "document.delete.soft",
            extra={"user_id": str(user_id), "document_id": str(doc.document_id)},
        )
