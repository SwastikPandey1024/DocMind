# DocMind Architecture & Design

## System Overview

DocMind is a distributed AI application with clear separation of concerns:

```
┌──────────────────┐
│  React Frontend  │ (Vite SPA)
│  (Port 80/3000)  │
└────────┬─────────┘
         │ HTTP/REST
         │
┌────────▼─────────────────────────────────────────────────┐
│  FastAPI Backend                                          │
│  (Port 8000)                                              │
│                                                            │
│  ├─ Authentication Service                               │
│  ├─ Document Management Service                          │
│  ├─ OCR Pipeline Service                                 │
│  ├─ Embedding Service                                    │
│  ├─ RAG Service (Retrieval-Augmented Generation)         │
│  ├─ Chat Service (with streaming)                        │
│  └─ Health/Ready Endpoints                               │
└──┬──┬──┬──┬─────────────────────────────────────┬────────┘
   │  │  │  │                                     │
   │  │  │  │                            ┌────────▼──────┐
   │  │  │  │                            │ Ollama/OpenAI │
   │  │  │  │                            │ (LLM Services)│
   │  │  │  │                            └───────────────┘
   │  │  │  │
   │  │  │  └──────────────┐
   │  │  │                 │
   │  │  │           ┌─────▼──────────┐
   │  │  │           │ FAISS Vector   │
   │  │  │           │ Store (Memory) │
   │  │  │           └────────────────┘
   │  │  │
   │  │  └──────┐
   │  │         │
   │  │    ┌────▼──────────┐
   │  │    │ Local Storage │
   │  │    │ (PDF Files,   │
   │  │    │  Vectorstore) │
   │  │    └───────────────┘
   │  │
   │  └──────────┐
   │             │
   │        ┌────▼──────────────┐
   │        │ PostgreSQL DB     │
   │        │ (Users, Docs,     │
   │        │  Chat History)    │
   │        └───────────────────┘
   │
   └─────────────────────────────────────────┐
                                              │
                                     ┌────────▼─────────┐
                                     │ PaddleOCR        │
                                     │ PyMuPDF          │
                                     │ Sentence Trans.  │
                                     │ (Python Process) │
                                     └──────────────────┘
```

---

## Backend Architecture

### 1. API Layer (`app/api/v1/`)

**Responsibility:** HTTP request handling, validation, response serialization

**Components:**
- `routes/` - Endpoint handlers
  - `auth.py` - User authentication endpoints
  - `documents.py` - Document CRUD endpoints
  - `chat.py` - Chat & RAG endpoints
  - `health.py` - Health check endpoints
  - `ready.py` - Readiness probe endpoint

- `schemas/` - Pydantic request/response models
  - `auth.py` - Login/register schemas
  - `documents.py` - Document upload/list schemas
  - `chat.py` - Chat request/response schemas
  - `common.py` - Generic response wrapper

- `dependencies/` - FastAPI dependency injection
  - `auth.py` - Current user, admin checks

### 2. Service Layer (`app/services/`)

**Responsibility:** Business logic, orchestration, domain operations

**Core Services:**

- **OCRService** (`ocr_service.py`)
  - Extracts text from PDFs using PaddleOCR
  - Returns `OCRPage` objects with bounding boxes
  - Confidence filtering (default: 0.3)

- **TextCleaningService** (`text_cleaning_service.py`)
  - Removes noise, duplicates, headers/footers
  - Normalizes unicode and whitespace
  - OCR artifact correction

- **ChunkingService** (`chunking_service.py`)
  - Recursive text splitting with separator hierarchy
  - Configurable chunk size (default: 512 chars)
  - Token estimation
  - Overlap support

- **EmbeddingService** (`embedding_service.py`)
  - SentenceTransformers-based embeddings
  - Supports multiple models (BGE, MiniLM)
  - Batch encoding for efficiency
  - Device selection (CPU/GPU)

- **FAISSVectorStore** (`vectorstore_service.py`)
  - FAISS index management
  - L2 distance or inner product similarity
  - Persistent save/load to disk
  - Metadata association

- **RAGMemoryStore** (`rag_memory_store.py`)
  - Per-document vector store management
  - In-memory caching
  - Lazy loading from disk

- **RAGService** (`rag_service.py`)
  - Retrieval logic (similarity search)
  - Context building
  - Citation extraction

- **LLMService** (`llm_service.py`)
  - Abstract provider interface
  - Ollama provider (local LLM)
  - OpenAI provider (cloud LLM)
  - Fallback mechanism

- **ChatService** (`chat_service.py`)
  - Orchestrates RAG + LLM
  - Question answering
  - Streaming response generation

- **DocumentService** (`document_service.py`)
  - Upload handling
  - Duplicate detection (SHA256 checksum)
  - File persistence

- **DocumentProcessingPipeline** (`document_processing_pipeline.py`)
  - End-to-end document processing
  - OCR → Clean → Chunk → Embed
  - Database transaction handling

- **OCRPipeline** (`ocr_pipeline.py`)
  - Asynchronous background processing
  - Status tracking (PROCESSING → READY/FAILED)

### 3. Data Layer

**Models** (`app/models/`)
- `User` - User accounts & authentication
- `Document` - Document metadata & status
- `OCRText` - Raw OCR extraction
- `Chunk` - Text chunks with embeddings
- `EmbeddingMetadata` - Embedding model metadata
- `ChatHistory` - Chat Q&A records

**Repositories** (`app/repositories/`)
- Generic CRUD via `BaseRepository`
- Specialized queries in domain repositories
- Soft-delete pattern

**Database** (`app/database/`)
- SQLAlchemy engine & session management
- Alembic migrations
- Base model with mixins (Timestamps, SoftDelete, UUIDs)

### 4. Authentication (`app/auth/`)

**JWT Flow:**
1. User registers/logs in → password hashed with Argon2
2. Backend generates access token (15 min) + refresh token (7 days)
3. Frontend stores tokens in localStorage
4. Requests include `Authorization: Bearer <token>`
5. Backend validates signature and expiration

**Implementation:**
- `service.py` - Signup, login, token refresh
- `jwt.py` - Token creation and verification
- `dependencies.py` - Current user extraction
- `router.py` - Auth endpoints

### 5. Middleware (`app/middleware/`)

- **CORS** - Cross-origin resource sharing
- **Exception Handling** - Global error responses
- **Request Logging** - Audit trails

---

## Frontend Architecture

### 1. React Component Hierarchy

```
App
├── AuthProvider
│   └── Router
│       ├── LoginPage (public)
│       ├── RegisterPage (public)
│       └── ProtectedRoute
│           ├── DashboardPage
│           ├── DocumentsPage
│           ├── UploadPage
│           ├── DocumentDetailPage
│           ├── ChatPage
│           ├── HistoryPage
│           └── SettingsPage
```

### 2. Key Contexts & Hooks

**AuthContext**
- User state
- Login/logout/register functions
- Token management
- Loading/error states

**Custom Hooks**
- `useAuth()` - Access auth context
- `useQuery()` - Data fetching (React Query)
- `useDocuments()` - Document list queries
- `useChat()` - Chat API integration

### 3. API Client (`services/api.ts`)

```typescript
- axios configured instance
- JWT token handling
- Request/response interceptors
- Error handling
- Methods: login, register, logout, getCurrentUser
- Document methods: upload, list, get, delete
- Chat methods: chat, stream, history
```

### 4. Routing

- React Router v7 for navigation
- Protected routes with auth check
- Redirects for unauthenticated users
- Deep linking support

### 5. Styling

- **Tailwind CSS** for utility-first styling
- **Radix UI** for accessible components
- **Dark mode** support via class toggle

---

## Processing Pipelines

### OCR → Chat Pipeline

```
1. Upload PDF
   ↓
2. Validate file (size, type, checksum)
   ↓
3. Store file on disk
   ↓
4. Create Document record (status=PROCESSING)
   ↓
5. [ASYNC] Extract text with OCR
   ├─ Per-page OCR
   ├─ Block extraction with confidence
   ├─ Store raw OCR data
   ↓
6. Clean text
   ├─ Remove noise
   ├─ Fix OCR artifacts
   ├─ Remove duplicates
   ↓
7. Chunk text
   ├─ Recursive splitting
   ├─ Overlap handling
   ├─ Token estimation
   ↓
8. Generate embeddings
   ├─ Batch encode chunks
   ├─ Create EmbeddingMetadata records
   ↓
9. Index vectors
   ├─ Add to FAISS index
   ├─ Associate metadata
   ├─ Save to disk
   ↓
10. Update Document (status=READY)

---

Chat Query Pipeline

1. User asks question
   ↓
2. Verify document ownership
   ↓
3. Embed question with same model
   ↓
4. Search FAISS index (k=5)
   ↓
5. Build context from results
   ↓
6. Create system + user prompt
   ↓
7. Call LLM (Ollama/OpenAI)
   ├─ If streaming: SSE response
   └─ If regular: wait for full response
   ↓
8. Save to ChatHistory
   ↓
9. Return with citations
```

---

## Data Models

### Core Relations

```
User (1) ──→ (N) Document
User (1) ──→ (N) ChatHistory
Document (1) ──→ (N) OCRText
Document (1) ──→ (N) Chunk
Document (1) ──→ (N) ChatHistory
Chunk (N) ──→ (1) EmbeddingMetadata
```

### Key Fields

**Document**
- `document_id` (UUID, PK)
- `user_id` (FK)
- `file_name`, `file_path`
- `status` (UPLOADING, PROCESSING, READY, FAILED)
- `checksum_sha256` (duplicate detection)
- `total_pages`, `mime_type`, `file_size`

**Chunk**
- `chunk_id` (UUID, PK)
- `document_id` (FK)
- `chunk_index` (page-relative position)
- `page_number`
- `chunk_text` (raw text)
- `embedding_key` (FK to EmbeddingMetadata)
- `token_count`, `start_char`, `end_char`

**ChatHistory**
- `chat_id` (UUID, PK)
- `user_id`, `document_id` (FKs)
- `question`, `answer` (stored verbatim)
- `response_time_ms`

---

## Deployment Topology

### Docker Compose Setup

**Services:**
1. **PostgreSQL** - Database (postgres:16-alpine)
2. **Backend** - FastAPI app (python:3.12-slim)
3. **Frontend** - React app (nginx:alpine)
4. **Ollama** - Local LLM (ollama/ollama:latest)

**Volumes:**
- `postgres_data` - Database persistence
- `ollama_data` - LLM model cache
- `./storage/uploads` - PDF uploads
- `./storage/vectorstore` - FAISS indices

**Networks:**
- `docmind` (bridge) - Internal communication

### Port Mappings

| Service | Port | Purpose |
|---------|------|---------|
| Nginx (Frontend) | 80 | Web UI |
| FastAPI (Backend) | 8000 | REST API |
| PostgreSQL | 5432 | Database |
| Ollama | 11434 | LLM inference |

---

## Performance Considerations

### Optimization Strategies

**Frontend:**
- Code splitting via Vite
- React Query caching
- Virtual scrolling for large lists
- Image optimization

**Backend:**
- Connection pooling (SQLAlchemy)
- FAISS CPU optimization
- Batch embeddings
- Async I/O
- Request compression

**Database:**
- Indexes on frequently queried columns
- Soft-delete queries filter `is_deleted`
- Connection pooling
- Read replicas (optional)

### Scaling Options

**Vertical:**
- Increase CPU/RAM for embeddings
- GPU acceleration for FAISS

**Horizontal:**
- Multiple backend instances (load balanced)
- Read replicas for PostgreSQL
- Distributed FAISS indices per document shard

**Caching:**
- Redis for session management
- FAISS in-memory store
- Embedding cache

---

## Security Considerations

### Authentication & Authorization

- JWT tokens with RS256 or HS256
- Argon2 password hashing
- Refresh token rotation
- Rate limiting (future)

### Data Protection

- Soft-delete audit trail
- Checksum verification
- File type validation
- Upload size limits
- SQL injection prevention (ORM)

### Network Security

- HTTPS/TLS in production
- CORS configured
- Secure cookies (HttpOnly, SameSite)
- CSRF protection (future)

---

## Error Handling

### HTTP Status Codes

| Code | Scenario |
|------|----------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request (validation) |
| 401 | Unauthorized (no auth token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found |
| 409 | Conflict (duplicate checksum) |
| 422 | Unprocessable (validation error) |
| 500 | Server error |
| 503 | Service unavailable (LLM down) |

### Error Response Format

```json
{
  "detail": "User not found",
  "status_code": 404,
  "error_code": "USER_NOT_FOUND"
}
```

---

## Monitoring & Logging

### Health Checks

- `GET /api/v1/health` - Full health check
- `GET /api/v1/ready` - Readiness probe
- Database connection test
- External service availability

### Logging

- Structured logging (JSON)
- Request/response logging
- Performance metrics
- Error tracking
- Audit trails

### Metrics (Future)

- Request latency
- Document processing time
- LLM response latency
- Vector search latency
- Database query times

---

## Extensibility

### Adding New LLM Providers

```python
# Extend LLMProvider
class AnthropicProvider(LLMProvider):
    async def generate(self, prompt, **kwargs):
        # Implementation
        pass
    
    async def stream(self, prompt, **kwargs):
        # Implementation
        pass

# Register in LLMService
llm_service = LLMService(
    primary_provider=AnthropicProvider(...),
    fallback_provider=OllamaProvider(...)
)
```

### Adding New Document Types

- Extend `DocumentValidator` for file type checks
- Create parser in `ocr_service` (e.g., ImageService)
- Update `document_processing_pipeline` to route correctly

### Adding New Embedding Models

- Register in `EmbeddingService.MODELS`
- Download model during initialization
- Cache embeddings with new model name

---

## Future Architecture Improvements

1. **Message Queue** (Celery/RabbitMQ)
   - Offload background tasks
   - Retry logic

2. **Caching Layer** (Redis)
   - Session store
   - Query cache
   - Rate limiting

3. **Search Engine** (Elasticsearch)
   - Full-text search
   - Advanced filtering

4. **Message Broker** (WebSockets)
   - Real-time notifications
   - Live collaboration

5. **Analytics** (Prometheus/Grafana)
   - Metrics collection
   - Performance monitoring

6. **Feature Flags** (LaunchDarkly)
   - A/B testing
   - Gradual rollouts

---

**For operational details, see DEPLOYMENT.md**
**For API reference, see /docs endpoint**
