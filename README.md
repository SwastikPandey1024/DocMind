# DocMind - AI-Powered OCR & RAG Document Chat

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.139-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/react-19-blue.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)](https://www.docker.com/)

DocMind is a production-ready AI SaaS application that combines **Optical Character Recognition (OCR)**, **Retrieval-Augmented Generation (RAG)**, and **LLM-powered chat** to enable intelligent document understanding and Q&A.

**Key Capabilities:**
- 📄 Extract text from PDFs using **PaddleOCR** with multi-language support
- 🧹 Automatic text cleaning and noise removal
- 📚 Semantic chunking with configurable overlap
- 🔍 Vector similarity search with **FAISS**
- 💬 LLM-powered Q&A with streaming responses
- 🔐 JWT authentication with role-based access
- ⚡ Async/await architecture for high concurrency
- 🐳 Docker & Docker Compose for production deployment
- 📊 Comprehensive audit logging

---

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Browser   │──────│  React SPA   │──────│  FastAPI    │
│   (React)   │      │  (Vite)      │      │  Backend    │
└─────────────┘      └──────────────┘      └─────────────┘
                                                    │
                              ┌─────────────────────┼─────────────────────┐
                              │                     │                     │
                        ┌──────────┐         ┌─────────────┐      ┌──────────────┐
                        │PostgreSQL│         │ FAISS Vector│      │Ollama/OpenAI │
                        │Database  │         │ Store       │      │LLM Services  │
                        └──────────┘         └─────────────┘      └──────────────┘
                              │
                        ┌──────────────┐
                        │OCR Pipeline  │
                        │(PaddleOCR)   │
                        └──────────────┘
```

### Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Frontend** | Web UI for document upload, chat, history | React 19, TypeScript, Tailwind, Vite |
| **Backend** | REST API & WebSocket server | FastAPI, Uvicorn, Python 3.12 |
| **Database** | User, document, chat history storage | PostgreSQL 16 |
| **OCR Pipeline** | PDF text extraction & cleaning | PaddleOCR, PyMuPDF |
| **Embeddings** | Semantic text representation | SentenceTransformers (BGE) |
| **Vector Store** | Similarity search index | FAISS |
| **LLM Services** | Response generation | Ollama (local) / OpenAI (cloud) |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR: Python 3.12+, Node.js 20+, PostgreSQL 16

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/SwastikPandey1024/DocMind.git
cd DocMind

# Build & start services
docker compose up -d

# Wait for services to be healthy (30-60s)
docker compose ps

# Access application
- Frontend: http://localhost
- API Docs: http://localhost:8000/docs
- API: http://localhost:8000
```

### Option 2: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**PostgreSQL:**
```bash
# Using Docker
docker run -d \
  -e POSTGRES_DB=docmind \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16-alpine
```

---

## API Documentation

### Authentication

All protected endpoints require JWT Bearer token in `Authorization` header.

```bash
# Register
POST /api/v1/auth/register
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}

# Login
POST /api/v1/auth/login
{
  "email": "john@example.com",
  "password": "SecurePassword123"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Document Operations

```bash
# Upload PDF
POST /api/v1/documents/upload
Headers: Authorization: Bearer <token>
Body: multipart/form-data (file)

# List documents
GET /api/v1/documents
Headers: Authorization: Bearer <token>

# Get document details
GET /api/v1/documents/{document_id}
Headers: Authorization: Bearer <token>

# Delete document
DELETE /api/v1/documents/{document_id}
Headers: Authorization: Bearer <token>
```

### Chat & RAG

```bash
# Chat with document
POST /api/v1/chat
Headers: Authorization: Bearer <token>
{
  "document_id": "uuid",
  "question": "What is the main topic?",
  "temperature": 0.7,
  "include_sources": true
}

# Stream chat response
POST /api/v1/chat/stream
(Server-Sent Events)

# Get chat history
GET /api/v1/chat/history/{document_id}
Headers: Authorization: Bearer <token>
```

### Health & Monitoring

```bash
# Health check (no auth required)
GET /api/v1/health

# Readiness check
GET /api/v1/ready
```

Full OpenAPI documentation available at: `http://localhost:8000/docs`

---

## Project Structure

```
DocMind/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── routes/          # API endpoints
│   │   │   ├── schemas/         # Pydantic models
│   │   │   └── dependencies/    # FastAPI dependencies
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── repositories/        # Data access layer
│   │   ├── services/            # Business logic
│   │   │   ├── ocr_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── rag_service.py
│   │   │   └── vectorstore_service.py
│   │   ├── auth/                # Authentication
│   │   ├── middleware/          # CORS, logging, exceptions
│   │   ├── core/                # Config, constants, logging
│   │   └── database/            # DB engine, session, base
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Unit & integration tests
│   ├── requirements.txt
│   └── startup.sh
├── frontend/
│   ├── src/
│   │   ├── app/                 # App entry point
│   │   ├── components/          # React components
│   │   ├── pages/               # Route pages
│   │   ├── contexts/            # React contexts
│   │   ├── hooks/               # Custom hooks
│   │   ├── services/            # API client
│   │   ├── types/               # TypeScript types
│   │   └── utils/               # Utilities
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml           # Production compose
├── Dockerfile.backend
├── Dockerfile.frontend
├── nginx.conf
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## Configuration

### Environment Variables

**Backend (.env or docker-compose environment):**

```env
# Application
APP_NAME=DocMind
APP_VERSION=0.1.0
APP_ENV=production              # development, testing, production
DEBUG=false

# Database
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/docmind

# Authentication
JWT_SECRET=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Storage
UPLOAD_DIR=/app/storage/uploads
MAX_UPLOAD_SIZE_MB=50
STORAGE_PATH=/app/storage
VECTORSTORE_PATH=/app/storage/vectorstore

# LLM Services
OPENAI_API_KEY=sk-...              # Optional: for OpenAI models
OLLAMA_HOST=http://ollama:11434    # Local LLM
OLLAMA_MODEL=llama2

# Embeddings & OCR
EMBEDDING_MODEL=bge-small          # bge-small|bge-base|bge-large|all-minilm
OCR_LANGUAGE=en                    # en, zh, etc.

# Logging
LOG_LEVEL=INFO
```

**Frontend (.env):**

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Features

### ✨ Implemented

- [x] JWT authentication with access/refresh tokens
- [x] User registration and login
- [x] PDF upload with validation
- [x] PaddleOCR text extraction (multi-language)
- [x] Automatic text cleaning
- [x] Semantic text chunking
- [x] Embeddings generation (SentenceTransformers)
- [x] FAISS vector indexing
- [x] Document similarity search
- [x] Chat with streaming responses
- [x] Chat history persistence
- [x] Ollama local LLM support
- [x] OpenAI GPT integration (fallback)
- [x] Role-based access control (RBAC)
- [x] Soft-delete for data retention
- [x] Comprehensive error handling
- [x] Request logging & audit trails
- [x] Health/readiness endpoints
- [x] Docker production setup
- [x] PostgreSQL with migrations

### 🚀 Future Enhancements

- [ ] Advanced RAG with reranking
- [ ] Web search integration
- [ ] Multi-language translation
- [ ] Document summarization
- [ ] Custom model fine-tuning
- [ ] Rate limiting & quotas
- [ ] Admin dashboard
- [ ] Export to multiple formats
- [ ] Webhook integrations
- [ ] API key management

---

## Development

### Running Tests

```bash
cd backend
pytest tests/
pytest --cov=app tests/      # With coverage
```

### Code Quality

```bash
# Linting
cd backend
pylint app/
black --check app/
mypy app/

cd ../frontend
npm run lint
npm run type-check
```

### Database Migrations

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1
```

---

## Deployment

### Production Checklist

- [ ] Set strong `JWT_SECRET` (min 32 chars)
- [ ] Configure `DATABASE_URL` for production PostgreSQL
- [ ] Set `APP_ENV=production`
- [ ] Disable `DEBUG=false`
- [ ] Configure `OPENAI_API_KEY` for production LLM
- [ ] Set up HTTPS/TLS
- [ ] Configure reverse proxy (Nginx)
- [ ] Setup database backups
- [ ] Monitor logs and metrics
- [ ] Configure resource limits

### Docker Deployment

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop services
docker compose down
```

### Kubernetes (Future)

KubernetesYAML manifests available in `k8s/` directory (coming soon).

---

## Performance

### Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| Text extraction (10-page PDF) | ~5-10s | PaddleOCR |
| Embedding generation (1000 chunks) | ~2-3s | SentenceTransformers |
| Vector search (k=5) | <100ms | FAISS on CPU |
| Chat response (streaming) | ~1-5s | Ollama/OpenAI |

### Optimization Tips

- Use GPU for embeddings: `DEVICE=cuda` (requires CUDA)
- Increase `EMBEDDING_BATCH_SIZE` for throughput
- Use `bge-base` or `bge-large` for better quality
- Cache embeddings with `EmbeddingMetadata`
- Enable FAISS GPU with `faiss-gpu` package

---

## Troubleshooting

### Backend won't start: "libGL.so.1 not found"

**Solution:** Dockerfile now uses `opencv-python-headless` instead of `opencv-python`.

```bash
# Rebuild
docker compose build --no-cache backend
docker compose up
```

### Vector store not persisting

Ensure `/app/storage/vectorstore` volume is mounted and writable.

```bash
docker compose exec backend ls -la /app/storage/
```

### Chat responses empty or timeout

Check Ollama/LLM service health:

```bash
# If using Ollama
docker compose logs ollama
curl http://localhost:11434/api/tags
```

### Database migrations fail

```bash
# Check migration status
docker compose exec backend alembic current

# View migration history
docker compose exec backend alembic history

# Manual rollback
docker compose exec backend alembic downgrade base
docker compose exec backend alembic upgrade head
```

---

## Security

### Authentication & Authorization

- JWT tokens with 15-minute expiration
- Refresh tokens with 7-day expiration
- Password hashing with Argon2
- Role-based access control (RBAC)
- Secure password validation

### Data Protection

- Soft-delete for audit trail
- Checksum verification for uploads
- CORS configured for frontend domain
- SQL injection protection via ORM
- XSS protection in React

### Best Practices

1. Always use HTTPS in production
2. Rotate JWT secrets periodically
3. Enable database backups
4. Monitor for suspicious activity
5. Keep dependencies updated
6. Implement rate limiting
7. Use strong passwords

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Support

- 📖 [Full Documentation](ARCHITECTURE.md)
- 🐛 [Issue Tracker](https://github.com/SwastikPandey1024/DocMind/issues)
- 💬 [Discussions](https://github.com/SwastikPandey1024/DocMind/discussions)

---

## Author

**Swastik Pandey**
- GitHub: [@SwastikPandey1024](https://github.com/SwastikPandey1024)
- LinkedIn: [swastik-pandey-a02719297](https://www.linkedin.com/in/swastik-pandey-a02719297)

---

**Built with ❤️ for intelligent document understanding**
