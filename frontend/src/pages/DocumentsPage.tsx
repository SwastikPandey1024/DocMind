import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { Sidebar } from '@/components/Sidebar';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export function DocumentsPage() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => apiClient.listDocuments(0, 1000),
    staleTime: 5 * 60 * 1000,
  });

  const filtered = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />

      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Documents</h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Manage and organize your PDFs</p>
            </div>
            <button
              onClick={() => navigate('/documents/upload')}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700"
            >
              <span>+</span>
              Upload Document
            </button>
          </div>

          {/* Search */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            />
          </div>

          {/* Documents Grid */}
          {isLoading ? (
            <LoadingSpinner />
          ) : filtered.length === 0 ? (
            <div className="rounded-lg bg-white p-12 text-center dark:bg-gray-800">
              <p className="text-lg text-gray-600 dark:text-gray-400">
                {searchTerm ? 'No documents found matching your search' : 'No documents yet'}
              </p>
              {!searchTerm && (
                <button
                  onClick={() => navigate('/documents/upload')}
                  className="mt-4 inline-block text-blue-600 hover:text-blue-700 dark:text-blue-400"
                >
                  Upload your first document →
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {filtered.map((doc) => (
                <div
                  key={doc.document_id}
                  onClick={() => navigate(`/documents/${doc.document_id}`)}
                  className="cursor-pointer rounded-lg bg-white p-6 shadow transition-all hover:shadow-lg dark:bg-gray-800"
                >
                  <div className="mb-4 flex items-start justify-between">
                    <div className="text-4xl">📄</div>
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                        doc.status === 'READY'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                      }`}
                    >
                      {doc.status}
                    </span>
                  </div>
                  <h3 className="mb-2 font-semibold text-gray-900 dark:text-white line-clamp-2">
                    {doc.filename}
                  </h3>
                  <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                    <p>Pages: {doc.pages || '-'}</p>
                    {doc.uploaded_at && (
                      <p>Uploaded: {new Date(doc.uploaded_at).toLocaleDateString()}</p>
                    )}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/documents/${doc.document_id}/chat`);
                    }}
                    className="mt-4 w-full rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-600 hover:bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400"
                  >
                    Chat with Document
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
