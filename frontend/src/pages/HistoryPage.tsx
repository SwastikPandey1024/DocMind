import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { Sidebar } from '@/components/Sidebar';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export function HistoryPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const [page, setPage] = useState(0);
  const limit = 20;

  const { data: document } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => apiClient.getDocument(documentId!),
    enabled: !!documentId,
  });

  const { data: history = [], isLoading } = useQuery({
    queryKey: ['chatHistory', documentId, page],
    queryFn: () => apiClient.getChatHistory(documentId!, page * limit, limit),
    enabled: !!documentId,
  });

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />

      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Chat History</h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              📄 {document?.filename}
            </p>
          </div>

          {isLoading ? (
            <LoadingSpinner />
          ) : history.length === 0 ? (
            <div className="rounded-lg bg-white p-12 text-center dark:bg-gray-800">
              <p className="text-gray-600 dark:text-gray-400">No chat history yet</p>
            </div>
          ) : (
            <div className="space-y-4">
              {history.map((item, idx) => (
                <div key={idx} className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
                  <div className="mb-3 flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-semibold text-blue-600 dark:text-blue-400">Q: {item.question}</p>
                    </div>
                    {item.created_at && (
                      <p className="ml-4 whitespace-nowrap text-xs text-gray-500 dark:text-gray-400">
                        {new Date(item.created_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                  <p className="text-gray-700 dark:text-gray-300">A: {item.answer}</p>
                  {item.response_time_ms && (
                    <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      Response time: {item.response_time_ms}ms
                    </p>
                  )}
                </div>
              ))}

              {/* Pagination */}
              <div className="flex gap-4 pt-4">
                <button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  className="rounded-lg bg-gray-200 px-4 py-2 text-gray-800 hover:bg-gray-300 disabled:opacity-50 dark:bg-gray-700 dark:text-white"
                >
                  Previous
                </button>
                <span className="flex items-center text-gray-600 dark:text-gray-400">
                  Page {page + 1}
                </span>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={history.length < limit}
                  className="rounded-lg bg-gray-200 px-4 py-2 text-gray-800 hover:bg-gray-300 disabled:opacity-50 dark:bg-gray-700 dark:text-white"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
