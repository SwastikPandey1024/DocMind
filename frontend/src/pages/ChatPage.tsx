import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiClient, ChatCitation } from '@/services/api';
import { Sidebar } from '@/components/Sidebar';
import { LoadingSpinner } from '@/components/LoadingSpinner';

interface Message {
  id: string;
  question: string;
  answer: string;
  citations: ChatCitation[];
  isLoading?: boolean;
  timestamp: Date;
}

export function ChatPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: document, isLoading: docLoading } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => apiClient.getDocument(documentId!),
    enabled: !!documentId,
  });

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !document || document.status !== 'READY') return;

    const question = input;
    setInput('');
    setIsStreaming(true);

    const messageId = Date.now().toString();
    setMessages((prev) => [
      ...prev,
      {
        id: messageId,
        question,
        answer: '',
        citations: [],
        isLoading: true,
        timestamp: new Date(),
      },
    ]);

    try {
      let fullAnswer = '';
      let finalCitations: ChatCitation[] = [];

      // Try streaming first
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/api/v1/chat/stream`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${localStorage.getItem('auth_tokens') ? JSON.parse(localStorage.getItem('auth_tokens')!).access_token : ''}`,
            },
            body: JSON.stringify({
              document_id: documentId,
              question,
              temperature: 0.7,
              include_sources: true,
            }),
          }
        );

        if (!response.ok) throw new Error('Stream failed');

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No reader');

        const decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n').filter((line) => line.trim());

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.chunk) {
                  fullAnswer += data.chunk;
                }
                if (data.is_final && data.citations) {
                  finalCitations = data.citations;
                }
              } catch (e) {
                console.error('Parse error:', e);
              }
            }
          }

          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === messageId
                ? {
                    ...msg,
                    answer: fullAnswer,
                    citations: finalCitations,
                  }
                : msg
            )
          );
        }
      } catch (streamError) {
        // Fallback to regular chat
        console.log('Streaming failed, using regular chat');
        const response = await apiClient.chat({
          document_id: documentId!,
          question,
          temperature: 0.7,
          include_sources: true,
        });

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === messageId
              ? {
                  ...msg,
                  answer: response.answer,
                  citations: response.citations,
                  isLoading: false,
                }
              : msg
          )
        );
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId
            ? {
                ...msg,
                answer: 'Failed to get response. Please try again.',
                isLoading: false,
              }
            : msg
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (docLoading) {
    return (
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        <Sidebar />
        <div className="flex-1">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />

      <div className="flex flex-1 flex-col">
        {/* Header */}
        <div className="border-b border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            📄 {document?.filename}
          </h1>
          <div className="mt-2 flex items-center gap-2">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Status: 
            </p>
            <span
              className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                document?.status === 'READY'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                  : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
              }`}
            >
              {document?.status}
            </span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <div className="mb-4 text-5xl">💬</div>
                <p className="text-gray-600 dark:text-gray-400">
                  {document?.status !== 'READY'
                    ? 'Document is being processed. Please wait...'
                    : 'Start asking questions about the document'}
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg) => (
                <div key={msg.id} className="space-y-4">
                  {/* Question */}
                  <div className="flex justify-end">
                    <div className="max-w-md rounded-lg bg-blue-600 px-4 py-3 text-white">
                      {msg.question}
                    </div>
                  </div>

                  {/* Answer */}
                  <div className="flex justify-start">
                    <div className="max-w-2xl space-y-3 rounded-lg bg-white p-4 dark:bg-gray-800">
                      {msg.isLoading ? (
                        <div className="flex items-center gap-2">
                          <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600"></div>
                          <span className="text-gray-600 dark:text-gray-400">Thinking...</span>
                        </div>
                      ) : (
                        <>
                          <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
                            {msg.answer}
                          </p>

                          {/* Citations */}
                          {msg.citations && msg.citations.length > 0 && (
                            <div className="border-t border-gray-200 pt-3 dark:border-gray-700">
                              <p className="mb-2 text-xs font-semibold text-gray-600 dark:text-gray-400">
                                📚 SOURCES
                              </p>
                              <div className="space-y-2">
                                {msg.citations.map((citation, idx) => (
                                  <div
                                    key={idx}
                                    className="rounded bg-gray-50 p-2 text-xs text-gray-700 dark:bg-gray-700 dark:text-gray-300"
                                  >
                                    <p className="font-medium">
                                      Page {citation.page_number || 'N/A'} • Confidence:{' '}
                                      {(citation.similarity_score * 100).toFixed(0)}%
                                    </p>
                                    <p className="mt-1 line-clamp-2 italic">
                                      "{citation.snippet}..."
                                    </p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          {document?.status !== 'READY' && (
            <div className="mb-4 rounded-lg bg-yellow-50 p-3 text-sm text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300">
              ⏳ Document is being processed. Chat will be available when ready.
            </div>
          )}
          <form onSubmit={handleSendMessage} className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                document?.status !== 'READY'
                  ? 'Document is processing...'
                  : 'Ask a question about the document...'
              }
              disabled={isStreaming || document?.status !== 'READY'}
              className="flex-1 rounded-lg border border-gray-300 px-4 py-3 dark:border-gray-600 dark:bg-gray-700 dark:text-white disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isStreaming || !input.trim() || document?.status !== 'READY'}
              className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isStreaming ? '📤' : '→'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
