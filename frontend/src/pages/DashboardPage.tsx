import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { Sidebar } from '@/components/Sidebar';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState({ documents: 0, chats: 0 });

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => apiClient.listDocuments(0, 100),
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    setStats({ documents: documents.length, chats: 0 });
  }, [documents]);

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Welcome back, {user?.name}! 👋
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Manage your documents and chat with AI
            </p>
          </div>

          {/* Stats Grid */}
          <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Documents</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                    {stats.documents}
                  </p>
                </div>
                <div className="text-4xl">📄</div>
              </div>
            </div>

            <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Chat Sessions</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                    {stats.chats}
                  </p>
                </div>
                <div className="text-4xl">💬</div>
              </div>
            </div>

            <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Member Since</p>
                  <p className="mt-2 text-lg font-bold text-gray-900 dark:text-white">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
                <div className="text-4xl">🗓️</div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mb-8">
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">Quick Actions</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <button
                onClick={() => navigate('/documents/upload')}
                className="flex items-center justify-center rounded-lg bg-blue-600 px-6 py-4 text-white hover:bg-blue-700"
              >
                <span className="text-2xl mr-2">📤</span>
                <div className="text-left">
                  <p className="font-semibold">Upload Document</p>
                  <p className="text-sm opacity-90">Add a new PDF</p>
                </div>
              </button>

              <button
                onClick={() => navigate('/documents')}
                className="flex items-center justify-center rounded-lg bg-green-600 px-6 py-4 text-white hover:bg-green-700"
              >
                <span className="text-2xl mr-2">📚</span>
                <div className="text-left">
                  <p className="font-semibold">View Documents</p>
                  <p className="text-sm opacity-90">Browse all documents</p>
                </div>
              </button>
            </div>
          </div>

          {/* Recent Documents */}
          <div>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">Recent Documents</h2>
            {isLoading ? (
              <LoadingSpinner />
            ) : documents.length === 0 ? (
              <div className="rounded-lg bg-white p-8 text-center dark:bg-gray-800">
                <p className="text-gray-600 dark:text-gray-400">No documents yet</p>
                <button
                  onClick={() => navigate('/documents/upload')}
                  className="mt-4 inline-block text-blue-600 hover:text-blue-700 dark:text-blue-400"
                >
                  Upload your first document →
                </button>
              </div>
            ) : (
              <div className="overflow-hidden rounded-lg bg-white shadow dark:bg-gray-800">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700 dark:text-gray-300">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700 dark:text-gray-300">
                        Pages
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700 dark:text-gray-300">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700 dark:text-gray-300">
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {documents.slice(0, 5).map((doc) => (
                      <tr key={doc.document_id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                          {doc.filename}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                          {doc.pages || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span
                            className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                              doc.status === 'READY'
                                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                            }`}
                          >
                            {doc.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <button
                            onClick={() => navigate(`/documents/${doc.document_id}`)}
                            className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
