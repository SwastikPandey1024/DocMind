# DocMind - AI-Powered Document Chat System

An enterprise-grade document intelligence platform that enables users to upload PDFs, extract structured text using OCR, and interact with documents through a conversational interface powered by Retrieval-Augmented Generation (RAG).

## Features

### 🔐 Authentication
- User registration and login
- JWT-based token authentication
- Password strength validation (Argon2)
- Token refresh mechanism
- Protected API routes

### 📄 Document Management
- PDF upload with validation
- Automatic duplicate detection via checksums
- Soft delete support
- Document metadata tracking
- File size and MIME type validation
- Maximum 50MB file upload

### 🤖 OCR & Text Processing
- PyMuPDF for PDF rendering
- PaddleOCR for text extraction
- Layout detection and reading order
- Confidence filtering (>30%)
- Unicode normalization
- Header/footer removal
- Noise filtering and deduplication

### 📊 Text Chunking & Embeddings
- Recursive text splitter with overlap
- Token-aware chunking (~512 tokens per chunk)
- SentenceTransformers (BGE Small/Base/Large)
- Batch embedding generation
- FAISS vector database
- Similarity scoring and search

### 💬 RAG & Chat
- Retrieval-Augmented Generation pipeline
- Top-K similarity search (default: 5 chunks)
- Citation extraction and grounding
- Streaming chat responses
- Chat history persistence
- Support for OpenAI + Ollama backends

### 🎨 Frontend
- React 19 with TypeScript
- TanStack React Query for state management
- Axios with interceptors for API calls
- Dark mode support
- Responsive design (mobile, tablet, desktop)
- Protected routes with auth context
- Error boundaries for graceful error handling

## Architecture

### Backend Stack
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migration**: Alembic
- **Authentication**: JWT (HS256)
- **Password Hashing**: Argon2
- **OCR**: PyMuPDF + PaddleOCR
- **Embeddings**: SentenceTransformers
- **Vector Store**: FAISS
- **LLM**: OpenAI API + Ollama local models

### Frontend Stack
- **Framework**: React 19 with TypeScript
- **Build**: Vite
- **Styling**: Tailwind CSS + dark mode
- **State**: React Context + TanStack Query
- **HTTP**: Axios with interceptors
- **Routing**: React Router v7

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 16 Alpine
- **LLM Provider**: Ollama
- **Reverse Proxy**: Nginx
- **Orchestration**: Docker Compose (single-host)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.12+ (for local development)
- 50GB free disk space (for models)

### Using Docker Compose

```bash
# Clone repository
git clone https://github.com/yourusername/docmind.git
cd docmind

# Create .env from example
cp .env.example .env

# Start all services
docker-compose up -d

# Wait for all services to be healthy (2-3 minutes)
docker-compose ps

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/docmind
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## API Documentation

### Authentication Endpoints

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "message": "User registered successfully",
  "data": {
    "user_id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer"
  }
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>

Response: 200 OK
{
  "message": "User retrieved",
  "data": {
    "user_id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Document Endpoints

#### Upload Document
```http
POST /api/v1/documents/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file=<binary_pdf>

Response: 200 OK
{
  "message": "Document uploaded successfully",
  "data": {
    "document_id": "uuid",
    "filename": "example.pdf",
    "status": "READY",
    "pages": null
  }
}
```

#### List Documents
```http
GET /api/v1/documents?offset=0&limit=100
Authorization: Bearer <access_token>

Response: 200 OK
{
  "message": "Documents retrieved successfully",
  "data": [
    {
      "document_id": "uuid",
      "filename": "example.pdf",
      "pages": 10,
      "status": "READY",
      "uploaded_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Document
```http
GET /api/v1/documents/{document_id}
Authorization: Bearer <access_token>

Response: 200 OK
{
  "message": "Document retrieved successfully",
  "data": {
    "document_id": "uuid",
    "filename": "example.pdf",
    "pages": 10,
    "status": "READY",
    "uploaded_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Delete Document
```http
DELETE /api/v1/documents/{document_id}
Authorization: Bearer <access_token>

Response: 200 OK
{
  "message": "Document deleted successfully",
  "data": null
}
```

### Chat Endpoints

#### Chat (Single Response)
```http
POST /api/v1/chat
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "document_id": "uuid",
  "question": "What is this document about?",
  "temperature": 0.7,
  "include_sources": true
}

Response: 200 OK
{
  "message": "Chat response generated successfully",
  "data": {
    "answer": "This document discusses...",
    "citations": [
      {
        "document_id": "uuid",
        "chunk_index": 0,
        "page_number": 1,
        "similarity_score": 0.95,
        "snippet": "..."
      }
    ],
    "response_time_ms": 2500,
    "model": "gpt-3.5-turbo"
  }
}
```

#### Chat Streaming
```http
POST /api/v1/chat/stream
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "document_id": "uuid",
  "question": "Summarize this document",
  "temperature": 0.7,
  "include_sources": true
}

Response: 200 OK (Server-Sent Events)
data: {"chunk": "This ", "is_final": false}
data: {"chunk": "document ", "is_final": false}
data: {"chunk": "discusses...", "is_final": true, "citations": [...]}
```

#### Chat History
```http
GET /api/v1/chat/history/{document_id}?offset=0&limit=50
Authorization: Bearer <access_token>

Response: 200 OK
{
  "message": "Chat history retrieved successfully",
  "data": {
    "items": [
      {
        "chat_id": "uuid",
        "document_id": "uuid",
        "question": "What is this document about?",
        "answer": "This document discusses...",
        "response_time_ms": 2500,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1
  }
}
```

## Configuration

### Environment Variables

#### Backend (.env)
```env
# Application
APP_NAME=DocMind
APP_VERSION=0.1.0
APP_ENV=development
DEBUG=false

# Database
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/docmind
POSTGRES_DB=docmind
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# JWT
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Storage
UPLOAD_DIR=/app/storage/uploads
STORAGE_PATH=/app/storage
VECTORSTORE_PATH=/app/storage/vectorstore
MAX_UPLOAD_SIZE_MB=50

# Logging
LOG_LEVEL=INFO

# AI/ML - Embeddings
EMBEDDING_MODEL=bge-small

# AI/ML - OCR
OCR_LANGUAGE=en

# AI/ML - LLM
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
OPENAI_API_KEY=

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

## Database Schema

### Users Table
- `user_id` (UUID PK)
- `name` (String)
- `email` (String, unique)
- `password_hash` (String)
- `role` (String, default: 'user')
- `is_active` (Boolean)
- `is_deleted` (Boolean, default: false)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `deleted_at` (DateTime)

### Documents Table
- `document_id` (UUID PK)
- `user_id` (UUID FK)
- `file_name` (String)
- `file_path` (String)
- `status` (String, enum: UPLOADING, READY, FAILED)
- `total_pages` (Integer)
- `mime_type` (String)
- `file_size` (Integer)
- `checksum_sha256` (String, unique per user)
- `is_deleted` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `deleted_at` (DateTime)

### OCR Text Table
- `text_id` (UUID PK)
- `document_id` (UUID FK)
- `page_number` (Integer)
- `raw_text` (Text)
- `clean_text` (Text)
- `block_count` (Integer)
- `blocks_json` (JSON)
- `detected_language` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Chunks Table
- `chunk_id` (UUID PK)
- `document_id` (UUID FK)
- `chunk_index` (Integer)
- `page_number` (Integer)
- `chunk_text` (Text)
- `embedding_key` (String FK)
- `token_count` (Integer)
- `start_char` (Integer)
- `end_char` (Integer)
- `is_deleted` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `deleted_at` (DateTime)

### Embedding Metadata Table
- `embedding_key` (String PK)
- `model_name` (String)
- `dimension` (Integer)
- `is_deleted` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `deleted_at` (DateTime)

### Chat History Table
- `chat_id` (UUID PK)
- `user_id` (UUID FK)
- `document_id` (UUID FK, nullable)
- `question` (Text)
- `answer` (Text)
- `response_time_ms` (Integer)
- `is_deleted` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `deleted_at` (DateTime)

## Security Considerations

### Implemented
- ✅ JWT-based authentication
- ✅ Argon2 password hashing
- ✅ HTTPS enforced in production
- ✅ CORS configured for specific origins
- ✅ SQL injection prevention via ORM
- ✅ XSS protection via CSP headers
- ✅ Rate limiting ready (middleware framework)
- ✅ Request validation (Pydantic)

### Recommended for Production
- Implement rate limiting
- Add API key management
- Enable HTTPS/TLS
- Configure CORS for specific domains
- Implement audit logging
- Add database encryption
- Enable database backups
- Implement DDoS protection
- Add security headers (HSTS, X-Frame-Options, etc.)

## Testing

### Backend
```bash
cd backend
pytest tests/ -v --cov=app

# Run specific test
pytest tests/test_auth.py -v
```

### Frontend
```bash
cd frontend
npm run test

# Run with coverage
npm run test:coverage
```

## Deployment

### Using Docker Compose (Development/Single-Host)
```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f backend
```

### Using Kubernetes (Production)
```bash
# Create ConfigMaps and Secrets
kubectl create configmap docmind-config --from-file=.env
kubectl create secret generic docmind-secrets --from-literal=jwt-secret=...

# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get svc
```

### CI/CD Pipeline (GitHub Actions)
See `.github/workflows/` for automated testing, building, and deployment.

## Performance Optimization

### Backend
- SQLAlchemy query optimization with proper indexing
- Redis caching for frequently accessed data
- Lazy loading for relationships
- Batch processing for embeddings
- Connection pooling for database

### Frontend
- Code splitting via Vite
- Lazy loading routes
- React Query caching with stale-time
- Image optimization
- CSS minification

## Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check PostgreSQL container
docker-compose logs postgres

# Verify connection
docker-compose exec postgres psql -U postgres -d docmind -c "SELECT 1"

# Reinitialize database
docker-compose down postgres
docker-compose up -d postgres
```

#### Backend Not Responding
```bash
# Check logs
docker-compose logs backend

# Verify migrations
docker-compose exec backend alembic upgrade head

# Restart service
docker-compose restart backend
```

#### Frontend Build Issues
```bash
# Clear cache
rm -rf frontend/node_modules frontend/.vite
npm install --prefix frontend

# Rebuild
npm run build --prefix frontend
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions:
- GitHub Issues: https://github.com/yourusername/docmind/issues
- Email: support@docmind.ai
- Documentation: https://docs.docmind.ai

## Roadmap

### v1.1 (Q2 2025)
- [ ] Web clipper extension
- [ ] Batch document processing
- [ ] Advanced search filters
- [ ] Export chat sessions
- [ ] Custom model fine-tuning

### v1.2 (Q3 2025)
- [ ] Multi-language support
- [ ] Document collaboration
- [ ] Image extraction from PDFs
- [ ] Table data extraction
- [ ] API webhooks

### v2.0 (Q4 2025)
- [ ] Enterprise SSO integration
- [ ] Advanced analytics dashboard
- [ ] Custom deployment options
- [ ] CLI tool
- [ ] SDK for third-party integration

---

**DocMind v1.0** - Powered by AI, built with ❤️
