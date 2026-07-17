"""Chat routes with lazy AI service initialization."""

import logging
import time
import uuid
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
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
from app.core.config import get_settings
from app.models.chat import ChatHistory
from app.models.document import Document
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService, OllamaProvider
from app.services.rag_memory_store import RAGMemoryStore
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


async def get_chat_service(request: Request) -> ChatService:
    """Get or initialize chat service lazily."""
    if not request.app.state.services_initialized:
        try:
            logger.info("Lazy-initializing AI services...")

            # Initialize embedding service
            embedding_service = EmbeddingService(
                model_name=settings.embedding_model,
                device="cpu",
            )
            logger.info(f"✓ Embedding service ready: {settings.embedding_model}")

            # Initialize RAG memory store
            rag_memory_store = RAGMemoryStore(embedding_service)
            logger.info("✓ RAG memory store ready")

            # Initialize LLM service
            llm_provider = OllamaProvider(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
            )
            llm_service = LLMService(primary_provider=llm_provider)
            logger.info(f"✓ LLM service ready: {settings.ollama_model}")

            # Initialize chat service
            chat_service = ChatService(
                rag_memory_store=rag_memory_store,
                llm_service=llm_service,
                embedding_service=embedding_service,
            )
            logger.info("✓ Chat service ready")

            # Store in app state
            request.app.state.embedding_service = embedding_service
            request.app.state.rag_memory_store = rag_memory_store
            request.app.state.llm_service = llm_service
            request.app.state.chat_service = chat_service
            request.app.state.services_initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize AI services: {e}")
            raise HTTPException(
                status_code=503,
                detail="AI services not available. Please try again later.",
            )

    return request.app.state.chat_service


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

        logger.info(f"Chat query: {request.question[:100]}")

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

        return ApiResponse(
            message="Chat response generated successfully",
            data=ChatResponse(
                answer=response_data["answer"],
                citations=response_data["citations"],
                response_time_ms=response_time_ms,
                model=response_data["model"],
            ),
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


def set_services(*args, **kwargs):
    """Deprecated: Services are now lazy-initialized."""
    pass
