import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { Sidebar } from '@/components/Sidebar';

export function UploadPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadedDocumentId, setUploadedDocumentId] = useState<string | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string>('');

  const uploadMutation = useMutation({
    mutationFn: (fileToUpload: File) => apiClient.uploadDocument(fileToUpload),
    onSuccess: (doc) => {
      setUploadedDocumentId(doc.document_id);
      setProcessingStatus('Document uploaded. Processing OCR...');
      setFile(null);

      // Poll for processing status
      const interval = setInterval(async () => {
        try {
          const updated = await apiClient.getDocument(doc.document_id);
          if (updated.status === 'READY') {
            setProcessingStatus('Processing complete! Redirecting to chat...');
            clearInterval(interval);
            setTimeout(() => {
              navigate(`/documents/${doc.document_id}/chat`);
            }, 1000);
          } else if (updated.status === 'FAILED') {
            setProcessingStatus('Processing failed. Please try again.');
            clearInterval(interval);
          } else {
            setProcessingStatus(`Processing... (${updated.status})`);
          }
        } catch (e) {
          console.error('Error checking status:', e);
        }
      }, 2000);

      return () => clearInterval(interval);
    },
  });

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      const droppedFile = droppedFiles[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />

      <div className="flex-1 overflow-auto">
        <div className="flex h-full items-center justify-center p-8">
          <div className="w-full max-w-2xl">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Upload Document</h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Upload a PDF to start chatting with AI
              </p>
            </div>

            <div className="rounded-lg bg-white p-8 shadow dark:bg-gray-800">
              {processingStatus ? (
                // Processing status
                <div className="text-center">
                  <div className="mb-4 inline-block">
                    <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600"></div>
                  </div>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    Processing Document
                  </p>
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    {processingStatus}
                  </p>
                  <div className="mt-6 space-y-2 text-left text-sm text-gray-600 dark:text-gray-400">
                    <p>📄 Extracting text via OCR</p>
                    <p>🧹 Cleaning and normalizing text</p>
                    <p>✂️ Splitting into chunks</p>
                    <p>🧠 Generating embeddings</p>
                    <p>📚 Building search index</p>
                  </div>
                </div>
              ) : (
                <>
                  {/* Upload Area */}
                  <div
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    className={`rounded-lg border-2 border-dashed p-12 text-center transition-colors ${
                      dragActive
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                  >
                    <div className="mb-4 text-5xl">📄</div>
                    <p className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
                      {file ? file.name : 'Drag and drop your PDF here'}
                    </p>
                    <p className="mb-6 text-sm text-gray-600 dark:text-gray-400">
                      or click to browse
                    </p>

                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf"
                      onChange={handleFileSelect}
                      className="hidden"
                    />

                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="mb-4 rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
                    >
                      Select File
                    </button>

                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Maximum file size: 50 MB
                    </p>
                  </div>

                  {/* File Info */}
                  {file && (
                    <div className="mt-6 rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {file.name}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {(file.size / (1024 * 1024)).toFixed(2)} MB
                          </p>
                        </div>
                        <button
                          onClick={() => setFile(null)}
                          className="text-sm text-red-600 hover:text-red-700 dark:text-red-400"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Upload Button */}
                  <button
                    onClick={handleUpload}
                    disabled={!file || uploadMutation.isPending}
                    className="mt-6 w-full rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {uploadMutation.isPending ? 'Uploading...' : 'Upload Document'}
                  </button>

                  {/* Error */}
                  {uploadMutation.isError && (
                    <div className="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-400">
                      Upload failed. Please try again.
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Info */}
            <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="rounded-lg bg-white p-4 dark:bg-gray-800">
                <p className="font-semibold text-gray-900 dark:text-white">✓ Automatic Processing</p>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  Your PDF will be automatically processed with OCR and ready for chat
                </p>
              </div>
              <div className="rounded-lg bg-white p-4 dark:bg-gray-800">
                <p className="font-semibold text-gray-900 dark:text-white">✓ Private & Secure</p>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  Your documents are encrypted and only accessible to you
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
