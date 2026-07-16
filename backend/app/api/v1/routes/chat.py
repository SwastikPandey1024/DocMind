"""Chat routes for RAG-based document Q&A."""

import logging
import time
from typing import AsyncGenerator
import uuid

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
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# Placeholder services (will be injected from main.py)
_rag_service: RAGService | None = None
_llm_service: LLMService | None = None


def set_services(rag_service: RAGService, llm_service: LLMService):
    """Register RAG and LLM services (called from main.py)."""
    global _rag_service, _llm_service
    _rag_service = rag_service
    _llm_service = llm_service


def get_rag_service() -> RAGService:
    if _rag_service is None:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    return _rag_service


def get_llm_service() -> LLMService:
    if _llm_service is None:
        raise HTTPException(status_code=503, detail="LLM service not initialized")
    return _llm_service


@router.post("", response_model=ApiResponse[ChatResponse])
async def chat_with_document(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
    rag_service: RAGService = Depends(get_rag_service),
    llm_service: LLMService = Depends(get_llm_service),
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
        
        logger.info(f"Chat query on document {doc.document_id}: {request.question[:100]}")
        
        # Retrieve relevant chunks via RAG
        retrieval_results = rag_service.retrieve(
            query=request.question,
            k=5,
            score_threshold=0.3,
        )
        
        if not retrieval_results:
            logger.warning(f"No relevant chunks found for query: {request.question[:100]}")
            answer = "I could not find relevant information in the document to answer your question."
            citations = []
        else:
            # Build context and extract citations
            context, citations = rag_service.build_rag_context_and_citations(retrieval_results)
            
            # Build prompt
            system_prompt = (
                "You are a helpful assistant that answers questions based on provided documents. "
                "Be concise and accurate. If you don't know something, say so. "
                "Provide citations when referencing specific parts of the document."
            )
            
            user_prompt = f"""Based on the following document context, answer the user's question.

Document Context:
{context}

User Question: {request.question}

Answer:"""
            
            # Generate response
            answer = await llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=request.temperature,
            )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Save to chat history
        chat_record = ChatHistory(
            user_id=current_user.user_id,
            document_id=request.document_id,
            question=request.question,
            answer=answer,
            response_time_ms=response_time_ms,
        )
        db.add(chat_record)
        db.commit()
        
        return ApiResponse(
            message="Chat response generated successfully",
            data=ChatResponse(
                answer=answer,
                citations=citations if request.include_sources else [],
                response_time_ms=response_time_ms,
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
    rag_service: RAGService = Depends(get_rag_service),
    llm_service: LLMService = Depends(get_llm_service),
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
            
            # Retrieve chunks
            retrieval_results = rag_service.retrieve(
                query=request.question,
                k=5,
                score_threshold=0.3,
            )
            
            # Extract citations from first result
            citations = None
            if retrieval_results and request.include_sources:
                _, citations = rag_service.build_rag_context_and_citations(retrieval_results)
            
            # Build context
            context = rag_service.build_context(retrieval_results) if retrieval_results else ""
            
            # Build prompt
            system_prompt = (
                "You are a helpful assistant that answers questions based on provided documents. "
                "Be concise and accurate."
            )
            
            user_prompt = f"""Based on the following context, answer the user's question.

Context:
{context}

Question: {request.question}

Answer:"""
            
            # Stream generation
            collected_answer = ""
            async for chunk in llm_service.stream(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=request.temperature,
            ):
                collected_answer += chunk
                stream_chunk = ChatStreamChunk(chunk=chunk)
                yield f"data: {stream_chunk.model_dump_json()}\n\n"
            
            # Final chunk with citations
            final_chunk = ChatStreamChunk(
                chunk="",
                is_final=True,
                citations=citations,
            )
            yield f"data: {final_chunk.model_dump_json()}\n\n"
            
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
