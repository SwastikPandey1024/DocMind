"""Chat service integrating RAG retrieval with LLM."""

import logging
import time
from typing import AsyncGenerator, Optional

from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.rag_memory_store import RAGMemoryStore
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)


class ChatService:
    """Chat service with RAG and LLM integration."""

    def __init__(
        self,
        rag_memory_store: RAGMemoryStore,
        llm_service: LLMService,
        embedding_service: EmbeddingService,
    ):
        self.rag_memory_store = rag_memory_store
        self.llm_service = llm_service
        self.embedding_service = embedding_service

    def _get_rag_service(self, document_id: str) -> RAGService:
        """Get RAG service for document."""
        vector_store = self.rag_memory_store.get_store(document_id)
        return RAGService(
            embedding_service=self.embedding_service,
            vector_store=vector_store,
        )

    async def chat(
        self,
        document_id: str,
        question: str,
        temperature: float = 0.7,
        include_sources: bool = True,
    ) -> dict:
        """
        Chat with document using RAG.
        
        Args:
            document_id: Document UUID
            question: User question
            temperature: LLM temperature
            include_sources: Include citations
            
        Returns:
            {
                "answer": str,
                "citations": list[dict],
                "response_time_ms": int,
                "model": str,
            }
        """
        start_time = time.time()

        try:
            logger.info(f"Chat query: doc={document_id}, question={question[:100]}")

            # Get RAG service
            rag_service = self._get_rag_service(document_id)

            # Retrieve relevant chunks
            retrieval_results = rag_service.retrieve(
                query=question,
                k=5,
                score_threshold=0.3,
            )

            if not retrieval_results:
                logger.warning(f"No relevant chunks found for query: {question[:100]}")
                return {
                    "answer": "I could not find relevant information in the document to answer your question.",
                    "citations": [],
                    "response_time_ms": int((time.time() - start_time) * 1000),
                    "model": "N/A",
                }

            # Build context and citations
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

User Question: {question}

Answer:"""

            # Generate response
            answer = await self.llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            result = {
                "answer": answer,
                "citations": citations if include_sources else [],
                "response_time_ms": response_time_ms,
                "model": self.llm_service.primary_provider.__class__.__name__,
            }

            logger.info(f"Chat response generated in {response_time_ms}ms")
            return result

        except Exception as e:
            logger.exception(f"Chat error: {e}")
            raise

    async def chat_stream(
        self,
        document_id: str,
        question: str,
        temperature: float = 0.7,
        include_sources: bool = True,
    ) -> AsyncGenerator[dict, None]:
        """
        Stream chat responses with RAG.
        
        Yields:
            {"chunk": str, "is_final": bool, "citations": list[dict] (optional)}
        """
        try:
            # Retrieve context
            rag_service = self._get_rag_service(document_id)
            retrieval_results = rag_service.retrieve(
                query=question,
                k=5,
                score_threshold=0.3,
            )

            if not retrieval_results:
                yield {
                    "chunk": "I could not find relevant information in the document to answer your question.",
                    "is_final": True,
                    "citations": [],
                }
                return

            # Build context and citations
            context, citations = rag_service.build_rag_context_and_citations(retrieval_results)

            # Build prompt
            system_prompt = (
                "You are a helpful assistant that answers questions based on provided documents. "
                "Be concise and accurate."
            )

            user_prompt = f"""Based on the following context, answer the user's question.

Context:
{context}

Question: {question}

Answer:"""

            # Stream generation
            collected = ""
            async for chunk in self.llm_service.stream(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            ):
                collected += chunk
                yield {
                    "chunk": chunk,
                    "is_final": False,
                }

            # Final chunk with citations
            yield {
                "chunk": "",
                "is_final": True,
                "citations": citations if include_sources else [],
            }

        except Exception as e:
            logger.exception(f"Stream error: {e}")
            yield {
                "chunk": f"Error: {str(e)}",
                "is_final": True,
                "citations": [],
            }
