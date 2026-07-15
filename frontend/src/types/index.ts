export interface UserProfile {
  id: string;
  name: string;
  email: string;
}

export interface DocumentSummary {
  id: string;
  title: string;
  uploadedAt: string;
  status: 'processing' | 'ready' | 'error';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}
