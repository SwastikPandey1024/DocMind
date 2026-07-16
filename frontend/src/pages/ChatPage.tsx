import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
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

  const chatMutation = useMutation({
    mutationFn: async (question: string) => {
      const response = await apiClient.chat({
        document_id: documentId!,
        question,
        temperature: 0.7,
        include_sources: true,
      });
      return response;
    },
  });

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const question = input;
    setInput('');

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
      const response = await chatMutation.mutateAsync(question);
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
    } catch (error) {
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
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Chat with this document using AI
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <div className="mb-4 text-5xl">💬</div>
                <p className="text-gray-600 dark:text-gray-400">
                  Start asking questions about the document
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
                          {msg.citations.length > 0 && (
                            <div className="border-t border-gray-200 pt-3 dark:border-gray-700">
                              <p className="mb-2 text-xs font-semibold text-gray-600 dark:text-gray-400">
                                SOURCES
                              </p>
                              <div className="space-y-2">
                                {msg.citations.map((citation, idx) => (
                                  <div
                                    key={idx}
                                    className="rounded bg-gray-50 p-2 text-xs text-gray-700 dark:bg-gray-700 dark:text-gray-300"
                                  >
                                    <p className="font-medium">
                                      Page {citation.page_number} • Confidence:{' '}
                                      {(citation.similarity_score * 100).toFixed(0)}%
                                    </p>
                                    <p className="mt-1 line-clamp-2 italic">{citation.snippet}...</p>
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
          <form onSubmit={handleSendMessage} className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about the document..."
              disabled={chatMutation.isPending}
              className="flex-1 rounded-lg border border-gray-300 px-4 py-3 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            />
            <button
              type="submit"
              disabled={chatMutation.isPending || !input.trim()}
              className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {chatMutation.isPending ? '...' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
