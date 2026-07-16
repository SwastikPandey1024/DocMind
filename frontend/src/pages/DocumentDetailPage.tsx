import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { Sidebar } from '@/components/Sidebar';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export function DocumentDetailPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: document, isLoading } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => apiClient.getDocument(documentId!),
    enabled: !!documentId,
  });

  const deleteMutation = useMutation({
    mutationFn: () => apiClient.deleteDocument(documentId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      navigate('/documents');
    },
  });

  if (isLoading) {
    return (
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        <Sidebar />
        <div className="flex-1">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-600 dark:text-gray-400">Document not found</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />

      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8 flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                📄 {document.filename}
              </h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Uploaded: {document.uploaded_at ? new Date(document.uploaded_at).toLocaleString() : 'N/A'}
              </p>
            </div>
            <button
              onClick={() => navigate('/documents')}
              className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>

          {/* Stats Grid */}
          <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-3">
            <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Pages</p>
              <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                {document.pages || '-'}
              </p>
            </div>

            <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Status</p>
              <p className="mt-2">
                <span
                  className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${
                    document.status === 'READY'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                      : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                  }`}
                >
                  {document.status}
                </span>
              </p>
            </div>

            <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">File Size</p>
              <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                {document.file_size
                  ? (document.file_size / (1024 * 1024)).toFixed(2)
                  : '-'}{' '}
                MB
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="mb-8 rounded-lg bg-white p-6 shadow dark:bg-gray-800">
            <h2 className="mb-4 text-xl font-semibold text-gray-900 dark:text-white">
              Actions
            </h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <button
                onClick={() => navigate(`/documents/${documentId}/chat`)}
                className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-3 text-white hover:bg-blue-700"
              >
                <span>💬</span>
                Chat with Document
              </button>

              <button
                onClick={() => navigate(`/documents/${documentId}/history`)}
                className="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-3 text-white hover:bg-purple-700"
              >
                <span>📜</span>
                View Chat History
              </button>

              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-3 text-white hover:bg-red-700"
              >
                <span>🗑️</span>
                Delete Document
              </button>
            </div>
          </div>

          {/* Delete Confirmation */}
          {showDeleteConfirm && (
            <div className="fixed inset-0 flex items-center justify-center bg-black/50 p-4">
              <div className="rounded-lg bg-white p-6 dark:bg-gray-800 max-w-md">
                <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
                  Delete Document?
                </h3>
                <p className="mb-6 text-gray-600 dark:text-gray-400">
                  Are you sure you want to delete this document? This action cannot be undone.
                </p>
                <div className="flex gap-4">
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    className="flex-1 rounded-lg bg-gray-200 px-4 py-2 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => {
                      deleteMutation.mutate();
                      setShowDeleteConfirm(false);
                    }}
                    disabled={deleteMutation.isPending}
                    className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700 disabled:opacity-50"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Info */}
          <div className="rounded-lg bg-blue-50 p-6 dark:bg-blue-900/20">
            <h3 className="mb-2 font-semibold text-blue-900 dark:text-blue-400">ℹ️ About this document</h3>
            <ul className="space-y-1 text-sm text-blue-800 dark:text-blue-300">
              <li>• This document has been processed and is ready for AI chat</li>
              <li>• The document is encrypted and only accessible to you</li>
              <li>• Chat conversations are saved for future reference</li>
              <li>• You can delete this document anytime</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
