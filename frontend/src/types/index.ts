export interface User {
  user_id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Document {
  document_id: string;
  filename: string;
  pages: number;
  status: string;
  uploaded_at?: string;
  file_size?: number;
}

export interface ChatCitation {
  document_id: string;
  chunk_index: number;
  page_number?: number;
  similarity_score: number;
  snippet: string;
}

export interface ChatMessage {
  id: string;
  question: string;
  answer: string;
  citations: ChatCitation[];
  timestamp: Date;
  isLoading?: boolean;
}

export interface ApiResponse<T> {
  message: string;
  data: T;
  request_id?: string;
}
