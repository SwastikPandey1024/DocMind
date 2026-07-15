from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies.auth import get_current_user
from app.api.v1.schemas.common import ApiResponse
from app.api.v1.schemas.documents import (
    DocumentDetailResponse,
    DocumentListItem,
    DocumentUploadResponse,
)
from app.auth.dependencies import get_db_session
from app.models.document import Document
from app.repositories.document import DocumentRepository
from app.services.document_service import DocumentService
from app.services.document_validator import DocumentValidator
from app.services.storage_service import StorageService

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_repository(db: Session = Depends(get_db_session)) -> DocumentRepository:
    return DocumentRepository(db)


def get_document_service(
    document_repository: DocumentRepository = Depends(get_document_repository),
) -> DocumentService:
    # Keep validator/service wiring in DI layer.
    validator = DocumentValidator()
    storage_service = StorageService()
    return DocumentService(
        document_repository=document_repository,
        storage_service=storage_service,
        validator=validator,
    )


@router.post("/upload", response_model=ApiResponse[DocumentUploadResponse])
def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> ApiResponse[DocumentUploadResponse]:
    doc = document_service.upload_pdf(user_id=current_user.user_id, file=file)
    return ApiResponse(
        message="Document uploaded successfully.",
        data=DocumentUploadResponse(
            document_id=doc.document_id,
            filename=doc.file_name,
            status=doc.status,
        ),
    )


@router.get("", response_model=ApiResponse[list[DocumentListItem]])
def list_documents(
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
    offset: int = 0,
    limit: int = 100,
) -> ApiResponse[list[DocumentListItem]]:
    # Rate limit placeholder (no implementation).
    docs = document_service.list_user_documents(user_id=current_user.user_id, offset=offset, limit=limit)
    return ApiResponse(
        message="Documents retrieved successfully.",
        data=[
            DocumentListItem(
                document_id=d.document_id,
                filename=d.file_name,
                pages=d.total_pages,
                status=d.status,
            )
            for d in docs
        ],
    )


@router.get("/{document_id}", response_model=ApiResponse[DocumentDetailResponse])
def get_document(
    document_id: uuid.UUID,
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> ApiResponse[DocumentDetailResponse]:
    doc = document_service.get_user_document(user_id=current_user.user_id, document_id=document_id)
    return ApiResponse(
        message="Document retrieved successfully.",
        data=DocumentDetailResponse(
            document_id=doc.document_id,
            filename=doc.file_name,
            uploaded_at=doc.created_at,
            pages=doc.total_pages,
            status=doc.status,
        ),
    )


@router.delete("/{document_id}", response_model=ApiResponse[None])
def delete_document(
    document_id: uuid.UUID,
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> ApiResponse[None]:
    # Rate limit placeholder (no implementation).
    document_service.delete_user_document(user_id=current_user.user_id, document_id=document_id)
    return ApiResponse(message="Document deleted successfully.", data=None)

