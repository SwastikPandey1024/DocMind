import axios, { AxiosInstance, AxiosError } from 'axios';

export interface ApiResponse<T> {
  message: string;
  data: T;
  request_id?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

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

export interface ChatRequest {
  document_id: string;
  question: string;
  temperature?: number;
  include_sources?: boolean;
}

export interface ChatCitation {
  document_id: string;
  chunk_index: number;
  page_number?: number;
  similarity_score: number;
  snippet: string;
}

export interface ChatResponse {
  answer: string;
  citations: ChatCitation[];
  response_time_ms: number;
  model: string;
}

export interface ChatHistoryItem {
  chat_id?: string;
  document_id?: string;
  question: string;
  answer: string;
  response_time_ms?: number;
  created_at?: string;
}

export class ApiClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;

  constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - add auth token
    this.client.interceptors.request.use((config) => {
      const token = this.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired - clear and redirect to login
          this.setAccessToken(null);
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );

    // Load token from storage
    const stored = localStorage.getItem('auth_tokens');
    if (stored) {
      try {
        const tokens = JSON.parse(stored);
        this.accessToken = tokens.access_token;
      } catch (e) {
        console.error('Failed to parse stored tokens');
      }
    }
  }

  // Token management
  setAccessToken(token: string | null): void {
    this.accessToken = token;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  setTokens(tokens: AuthTokens): void {
    this.accessToken = tokens.access_token;
    localStorage.setItem('auth_tokens', JSON.stringify(tokens));
  }

  clearTokens(): void {
    this.accessToken = null;
    localStorage.removeItem('auth_tokens');
  }

  // Auth endpoints
  async register(name: string, email: string, password: string): Promise<User> {
    const response = await this.client.post<ApiResponse<User>>('/api/v1/auth/register', {
      name,
      email,
      password,
    });
    return response.data.data;
  }

  async login(email: string, password: string): Promise<AuthTokens> {
    const response = await this.client.post<ApiResponse<AuthTokens>>('/api/v1/auth/login', {
      email,
      password,
    });
    const tokens = response.data.data;
    this.setTokens(tokens);
    return tokens;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<ApiResponse<User>>('/api/v1/auth/me');
    return response.data.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/api/v1/auth/logout');
    } finally {
      this.clearTokens();
    }
  }

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response = await this.client.post<ApiResponse<AuthTokens>>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
    const tokens = response.data.data;
    this.setTokens(tokens);
    return tokens;
  }

  // Document endpoints
  async uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<ApiResponse<Document>>(
      '/api/v1/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.data;
  }

  async listDocuments(offset: number = 0, limit: number = 100): Promise<Document[]> {
    const response = await this.client.get<ApiResponse<Document[]>>(
      `/api/v1/documents?offset=${offset}&limit=${limit}`
    );
    return response.data.data;
  }

  async getDocument(documentId: string): Promise<Document> {
    const response = await this.client.get<ApiResponse<Document>>(
      `/api/v1/documents/${documentId}`
    );
    return response.data.data;
  }

  async deleteDocument(documentId: string): Promise<void> {
    await this.client.delete(`/api/v1/documents/${documentId}`);
  }

  // Chat endpoints
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ApiResponse<ChatResponse>>(
      '/api/v1/chat',
      request
    );
    return response.data.data;
  }

  async *chatStream(request: ChatRequest): AsyncGenerator<string, void, unknown> {
    const response = await this.client.get('/api/v1/chat/stream', {
      params: request,
      responseType: 'stream',
    });

    const reader = response.data.getReader();
    const decoder = new TextDecoder();

    try {
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
                yield data.chunk;
              }
            } catch (e) {
              console.error('Failed to parse stream chunk', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async getChatHistory(documentId: string, offset: number = 0, limit: number = 50): Promise<ChatHistoryItem[]> {
    const response = await this.client.get<ApiResponse<{ items: ChatHistoryItem[] }>>(
      `/api/v1/chat/history/${documentId}?offset=${offset}&limit=${limit}`
    );
    return response.data.data.items;
  }

  // Health check
  async health(): Promise<{ status: string; service: string }> {
    const response = await this.client.get('/api/v1/health');
    return response.data.data;
  }
}

// Singleton instance
export const apiClient = new ApiClient();
