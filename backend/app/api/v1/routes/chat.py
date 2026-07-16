"""Chat routes for RAG-based document Q&A."""

import logging
import time
import uuid
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1.dependencies.auth import get_current_user
from app.api.v1.schemas.chat import (
    ChatHistoryResponse,
    ChatHistoryItem,
    ChatRequest,
    ChatResponse,
    ChatStreamChunk,
)
from app.api.v1.schemas.common import ApiResponse
from app.auth.dependencies import get_db_session
from app.models.chat import ChatHistory
from app.models.document import Document
from app.services.chat_service import ChatService
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.rag_memory_store import RAGMemoryStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Placeholder services (will be injected from main.py)
_rag_memory_store: Optional[RAGMemoryStore] = None
_llm_service: Optional[LLMService] = None
_embedding_service: Optional[EmbeddingService] = None
_chat_service: Optional[ChatService] = None


def set_services(
    rag_memory_store: RAGMemoryStore,
    llm_service: LLMService,
    embedding_service: EmbeddingService,
    chat_service: ChatService,
):
    """Register services (called from main.py)."""
    global _rag_memory_store, _llm_service, _embedding_service, _chat_service
    _rag_memory_store = rag_memory_store
    _llm_service = llm_service
    _embedding_service = embedding_service
    _chat_service = chat_service


def get_chat_service() -> ChatService:
    if _chat_service is None:
        raise HTTPException(status_code=503, detail="Chat service not initialized")
    return _chat_service


@router.post("", response_model=ApiResponse[ChatResponse])
async def chat_with_document(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
    chat_service: ChatService = Depends(get_chat_service),
) -> ApiResponse[ChatResponse]:
    """Chat with a document using RAG."""
    start_time = time.time()

    try:
        # Verify document ownership
        doc = db.query(Document).filter_by(
            document_id=request.document_id,
            user_id=current_user.user_id,
        ).first()

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.status != "READY":
            raise HTTPException(
                status_code=400,
                detail=f"Document is still processing. Status: {doc.status}",
            )

        logger.info(f"Chat query on document {doc.document_id}: {request.question[:100]}")

        # Get response from chat service
        response_data = await chat_service.chat(
            document_id=str(request.document_id),
            question=request.question,
            temperature=request.temperature,
            include_sources=request.include_sources,
        )

        response_time_ms = int((time.time() - start_time) * 1000)

        # Save to chat history
        chat_record = ChatHistory(
            user_id=current_user.user_id,
            document_id=request.document_id,
            question=request.question,
            answer=response_data["answer"],
            response_time_ms=response_time_ms,
        )
        db.add(chat_record)
        db.commit()

        # Build response
        chat_response = ChatResponse(
            answer=response_data["answer"],
            citations=response_data["citations"],
            response_time_ms=response_time_ms,
            model=response_data["model"],
        )

        return ApiResponse(
            message="Chat response generated successfully",
            data=chat_response,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate chat response")


@router.post("/stream", response_class=StreamingResponse)
async def chat_stream(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
    chat_service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """Stream chat responses."""

    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            # Verify document ownership
            doc = db.query(Document).filter_by(
                document_id=request.document_id,
                user_id=current_user.user_id,
            ).first()

            if not doc:
                error = ChatStreamChunk(chunk="Error: Document not found", is_final=True)
                yield f"data: {error.model_dump_json()}\n\n"
                return

            if doc.status != "READY":
                error = ChatStreamChunk(
                    chunk=f"Document is still processing. Status: {doc.status}",
                    is_final=True,
                )
                yield f"data: {error.model_dump_json()}\n\n"
                return

            collected_answer = ""
            collected_citations = []

            # Stream chat
            async for chunk_data in chat_service.chat_stream(
                document_id=str(request.document_id),
                question=request.question,
                temperature=request.temperature,
                include_sources=request.include_sources,
            ):
                if chunk_data.get("is_final"):
                    collected_citations = chunk_data.get("citations", [])
                else:
                    collected_answer += chunk_data.get("chunk", "")

                chunk = ChatStreamChunk(
                    chunk=chunk_data.get("chunk", ""),
                    is_final=chunk_data.get("is_final", False),
                    citations=chunk_data.get("citations"),
                )
                yield f"data: {chunk.model_dump_json()}\n\n"

            # Save to history
            chat_record = ChatHistory(
                user_id=current_user.user_id,
                document_id=request.document_id,
                question=request.question,
                answer=collected_answer,
            )
            db.add(chat_record)
            db.commit()

        except Exception as e:
            logger.exception(f"Stream error: {e}")
            error = ChatStreamChunk(chunk=f"Error: {str(e)}", is_final=True)
            yield f"data: {error.model_dump_json()}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@router.get("/history/{document_id}", response_model=ApiResponse[ChatHistoryResponse])
def get_chat_history(
    document_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
    offset: int = 0,
    limit: int = 50,
) -> ApiResponse[ChatHistoryResponse]:
    """Get chat history for a document."""

    # Verify document ownership
    doc = db.query(Document).filter_by(
        document_id=document_id,
        user_id=current_user.user_id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get history
    query = db.query(ChatHistory).filter_by(
        user_id=current_user.user_id,
        document_id=document_id,
    ).order_by(ChatHistory.created_at.desc())

    total = query.count()
    items = query.offset(offset).limit(limit).all()

    history_items = [
        ChatHistoryItem(
            chat_id=item.chat_id,
            document_id=item.document_id,
            question=item.question,
            answer=item.answer,
            response_time_ms=item.response_time_ms,
            created_at=item.created_at.isoformat() if item.created_at else None,
        )
        for item in items
    ]

    return ApiResponse(
        message="Chat history retrieved successfully",
        data=ChatHistoryResponse(items=history_items, total=total),
    )
