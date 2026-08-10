<div align="center">
  <h1>🧠 DocMind</h1>
  <p><strong>AI-Powered OCR + RAG Document Chat System</strong></p>

  <p>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python">
    </a>
    <a href="https://fastapi.tiangolo.com/">
      <img src="https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white" alt="FastAPI">
    </a>
    <a href="https://react.dev/">
      <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white" alt="React">
    </a>
    <a href="https://www.typescriptlang.org/">
      <img src="https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white" alt="TypeScript">
    </a>
    <a href="https://tailwindcss.com/">
      <img src="https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white" alt="TailwindCSS">
    </a>
    <a href="https://www.docker.com/">
      <img src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white" alt="Docker">
    </a>
    <a href="https://www.postgresql.org/">
      <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
    </a>
  </p>

  <p>
    <a href="LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License">
    </a>
    <a href="CODE_OF_CONDUCT.md">
      <img src="https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg" alt="Code of Conduct">
    </a>
    <a href="https://github.com/SwastikPandey1024/DocMind/issues">
      <img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg" alt="Contributions Welcome">
    </a>
    <a href="https://github.com/SwastikPandey1024/DocMind/releases">
      <img src="https://img.shields.io/badge/release-v1.0.0-blue.svg" alt="Release">
    </a>
  </p>

  <br>

  <p align="center">
    <strong>
      <a href="#-quick-start">Quick Start</a> •
      <a href="#-features">Features</a> •
      <a href="#-screenshots">Screenshots</a> •
      <a href="#-architecture">Architecture</a> •
      <a href="#-tech-stack">Tech Stack</a> •
      <a href="#-api-documentation">API</a> •
      <a href="#-docker">Docker</a> •
      <a href="#-roadmap">Roadmap</a>
    </strong>
  </p>
</div>

---

## 🚀 Current Project Status (v1.0.0 Stable Release)

```text
DocMind (OCR + RAG Document Chat)
│
├── OCR Extraction           ✅ (PaddleOCR multi-language text extraction)
├── RAG Vector Pipeline      ✅ (Chunking, HuggingFace embeddings & FAISS indexing)
├── Hybrid LLM Support       ✅ (Local Ollama & Cloud OpenAI integrations)
├── User Authentication      ✅ (JWT Tokens, refresh rotation, Argon2 hashing)
├── PostgreSQL Storage       ✅ (User accounts, document metadata, audit logs)
├── FastAPI REST API         ✅ (Async API endpoints for documents & chat)
├── React 19 Frontend        ✅ (TypeScript + TailwindCSS modern dashboard)
├── Docker Infrastructure    ✅ (Backend, Frontend, Postgres, & Nginx config)
├── Automated Tests          ✅ (Pytest coverage for API & RAG pipelines)
├── Comprehensive Docs       ✅ (Architecture, Deployment, & Security specs)
└── Production Deployment    ✅ (Docker Compose one-command production readiness)
```

---

## 📖 Overview

**DocMind** is a production-ready AI SaaS application that combines **Optical Character Recognition (OCR)**, **Retrieval-Augmented Generation (RAG)**, and **LLM-powered chat** to enable intelligent document understanding and Q&A.

Upload PDFs, extract text using OCR, index content with semantic embeddings, and have natural conversations with your documents. DocMind supports both **local LLMs (Ollama)** and **cloud LLMs (OpenAI)**.

---

## ✨ Features

<table>
  <tr>
    <td align="center">📄</td>
    <td><strong>OCR Extraction</strong></td>
    <td>High-accuracy text extraction from scanned and digital PDFs using PaddleOCR with multi-language support</td>
  </tr>
  <tr>
    <td align="center">💬</td>
    <td><strong>AI Document Chat</strong></td>
    <td>Natural language Q&A with your documents — get answers grounded in your uploaded content</td>
  </tr>
  <tr>
    <td align="center">🔍</td>
    <td><strong>Semantic Search</strong></td>
    <td>FAISS-powered vector similarity search finds the most relevant document sections for any query</td>
  </tr>
  <tr>
    <td align="center">🧩</td>
    <td><strong>RAG Pipeline</strong></td>
    <td>End-to-end retrieval-augmented generation: chunk → embed → index → retrieve → generate</td>
  </tr>
  <tr>
    <td align="center">🔐</td>
    <td><strong>JWT Authentication</strong></td>
    <td>Secure access with JWT tokens, refresh token rotation, and Argon2 password hashing</td>
  </tr>
  <tr>
    <td align="center">🗄️</td>
    <td><strong>PostgreSQL</strong></td>
    <td>Reliable relational storage for users, documents, chat history with Alembic migrations</td>
  </tr>
  <tr>
    <td align="center">🐳</td>
    <td><strong>Docker Deployment</strong></td>
    <td>Multi-stage Docker builds, Docker Compose for dev & production, health checks everywhere</td>
  </tr>
  <tr>
    <td align="center">🌐</td>
    <td><strong>REST API</strong></td>
    <td>Fully documented RESTful API with OpenAPI/Swagger at <code>/docs</code></td>
  </tr>
</table>

### 📋 Complete Feature List

| Category | Feature | Status |
|----------|---------|--------|
| **Auth** | JWT with access/refresh tokens | ✅ |
| **Auth** | User registration & login | ✅ |
| **Auth** | Argon2 password hashing | ✅ |
| **Auth** | Role-based access control (RBAC) | ✅ |
| **Documents** | PDF upload with validation | ✅ |
| **Documents** | Duplicate detection (SHA-256) | ✅ |
| **Documents** | Document listing & deletion | ✅ |
| **Documents** | Soft-delete for data retention | ✅ |
| **OCR** | PaddleOCR text extraction | ✅ |
| **OCR** | Multi-language support | ✅ |
| **OCR** | Automatic text cleaning | ✅ |
| **OCR** | Confidence-based filtering | ✅ |
| **RAG** | Semantic text chunking | ✅ |
| **RAG** | Embedding generation (BGE/MiniLM) | ✅ |
| **RAG** | FAISS vector indexing | ✅ |
| **RAG** | Similarity search with L2 distance | ✅ |
| **Chat** | LLM-powered Q&A with streaming | ✅ |
| **Chat** | Chat history persistence | ✅ |
| **Chat** | Source citations | ✅ |
| **LLM** | Ollama (local) integration | ✅ |
| **LLM** | OpenAI (cloud) integration | ✅ |
| **LLM** | Provider fallback mechanism | ✅ |
| **Docker** | Multi-stage builds | ✅ |
| **Docker** | Dev & production compose files | ✅ |
| **Docker** | Health checks & monitoring | ✅ |
| **Frontend** | React 19 + TypeScript + Vite | ✅ |
| **Frontend** | TailwindCSS + Radix UI | ✅ |
| **Frontend** | Dark mode support | ✅ |

---

## 📸 Screenshots

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="assets/screenshots/login.png" alt="Login Screen" width="400"/>
        <br />
        <em>Login & Registration</em>
      </td>
      <td align="center">
        <img src="assets/screenshots/dashboard.png" alt="Dashboard" width="400"/>
        <br />
        <em>User Dashboard</em>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="assets/screenshots/upload-document.png" alt="Document Upload" width="400"/>
        <br />
        <em>Document Management</em>
      </td>
      <td align="center">
        <img src="assets/screenshots/chat.png" alt="Chat Interface" width="400"/>
        <br />
        <em>AI Document Chat</em>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="assets/screenshots/processing.png" alt="AI Document Processing In Light Mode" width="400"/>
        <br />
        <em>AI Document Processing In Light Mode</em>
      </td>
      <td align="center">
        <img src="assets/screenshots/dark-mode.png" alt="Processing In Dark Mode" width="400"/>
        <br />
        <em>AI Document Processing In Dark Mode</em>
      </td>
    </tr>
    <tr>
      <td align="center" colspan="2">
        <img src="assets/screenshots/swagger.png" alt="Swagger API Documentation" width="820"/>
        <br />
        <em>Interactive API Documentation (Swagger UI)</em>
      </td>
    </tr>
  </table>
</div>

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Browser   │──────│  React SPA   │──────│  FastAPI Backend │
│   (React)   │      │  (Vite)      │      │  (Port 8000)     │
└─────────────┘      └──────────────┘      └─────────────────┘
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

### Core Processing Pipeline

```
PDF Upload → OCR Extraction → Text Cleaning → Semantic Chunking
    ↓                                                    │
Chat Response ← LLM Generation ← Context Building ← FAISS Search
```

### Component Overview

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | React 19, TypeScript, Vite, TailwindCSS | Web UI for document upload, chat, history |
| **Backend** | FastAPI, Python 3.12, SQLAlchemy | REST API, business logic, orchestration |
| **Database** | PostgreSQL 16 | Users, documents, metadata, chat history |
| **OCR** | PaddleOCR, PyMuPDF | Text extraction from scanned/digital PDFs |
| **Embeddings** | SentenceTransformers | Semantic text representation |
| **Vector Store** | FAISS | Similarity search indexing |
| **LLM** | Ollama (local) / OpenAI (cloud) | Context-aware response generation |

---

## 🛠️ Tech Stack

### Backend
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-1.14-blue)
![PaddleOCR](https://img.shields.io/badge/PaddleOCR-2.10-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?logo=openai&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local-000?logo=ollama&logoColor=white)

### Frontend
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)
![TanStack Query](https://img.shields.io/badge/TanStack%20Query-5-FF4154?logo=reactquery&logoColor=white)
![React Router](https://img.shields.io/badge/React%20Router-7-CA4245?logo=reactrouter&logoColor=white)

### DevOps
![Docker](https://img.shields.io/badge/Docker-24-2496ED?logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-3.8-2496ED?logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-alpine-009639?logo=nginx&logoColor=white)

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended path)
- **OR** Python 3.12+, Node.js 20+, PostgreSQL 16

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/SwastikPandey1024/DocMind.git
cd DocMind

# Build and start all services
docker compose up -d

# Wait for services to become healthy (30-60 seconds)
docker compose ps

# Access the application
open http://localhost          # Frontend
open http://localhost:8000/docs # API Documentation
```

### Option 2: Local Development

**1. Start PostgreSQL:**
```bash
docker run -d \
  -e POSTGRES_DB=docmind \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16-alpine
```

**2. Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**3. Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🐳 Docker

### Development

```bash
docker compose up -d
```

### Production

```bash
docker compose -f docker-compose.production.yml up -d
```

### Useful Commands

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Rebuild specific service
docker compose build --no-cache backend

# Stop everything
docker compose down

# Remove volumes (WARNING: deletes data)
docker compose down -v
```

### Services

| Service    | Port  | Description                     |
|------------|-------|---------------------------------|
| Frontend   | 80    | React SPA via Nginx             |
| Backend    | 8000  | FastAPI REST API                |
| PostgreSQL | 5432  | Relational database             |
| Ollama     | 11434 | Local LLM inference (optional)  |

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)

```env
APP_NAME=DocMind
APP_VERSION=1.0.0
APP_ENV=development

DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/docmind

JWT_SECRET=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

OPENAI_API_KEY=sk-...              # Optional: for OpenAI models
OLLAMA_HOST=http://ollama:11434    # Local LLM endpoint
OLLAMA_MODEL=llama3.2

EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
OCR_LANGUAGE=en
MAX_UPLOAD_SIZE_MB=50
LOG_LEVEL=INFO
```

### Frontend (`frontend/.env`)

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📚 API Documentation

Interactive API documentation is available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc).

### Authentication Endpoints

```bash
# Register a new user
POST /api/v1/auth/register
# Body: { "name": "John Doe", "email": "john@example.com", "password": "SecurePass123" }

# Login
POST /api/v1/auth/login
# Body: { "email": "john@example.com", "password": "SecurePass123" }
# Response: { "access_token": "...", "refresh_token": "...", "token_type": "bearer" }

# Refresh token
POST /api/v1/auth/refresh
# Body: { "refresh_token": "..." }

# Get current user
GET /api/v1/auth/me
# Header: Authorization: Bearer <access_token>
```

### Document Endpoints

```bash
# Upload document
POST /api/v1/documents/upload
# Header: Authorization: Bearer <token>
# Body: multipart/form-data (file: PDF)

# List user documents
GET /api/v1/documents
# Header: Authorization: Bearer <token>

# Get document details
GET /api/v1/documents/{document_id}
# Header: Authorization: Bearer <token>

# Delete document
DELETE /api/v1/documents/{document_id}
# Header: Authorization: Bearer <token>
```

### Chat Endpoints

```bash
# Chat with document
POST /api/v1/chat
# Header: Authorization: Bearer <token>
# Body: { "document_id": "uuid", "question": "What is this document about?" }

# Stream chat response (SSE)
POST /api/v1/chat/stream
# Header: Authorization: Bearer <token>
# Body: { "document_id": "uuid", "question": "..." }

# Get chat history
GET /api/v1/chat/history/{document_id}
# Header: Authorization: Bearer <token>
```

### Health Endpoints

```bash
# Health check (no auth required)
GET /api/v1/health

# Readiness probe
GET /api/v1/ready
```

---

## 📁 Project Structure

```
DocMind/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes, schemas, dependencies
│   │   │   ├── routes/      # auth, chat, documents, health
│   │   │   └── schemas/     # Pydantic request/response models
│   │   ├── auth/            # JWT, password hashing, dependencies
│   │   ├── core/            # Configuration, constants, logging
│   │   ├── database/        # Engine, session, base models
│   │   ├── middleware/      # CORS, exception handling, logging
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── repositories/    # Data access layer
│   │   ├── schemas/         # Shared Pydantic schemas
│   │   └── services/        # Business logic services
│   │       ├── ocr/         # OCR pipeline services
│   │       ├── llm/         # LLM provider abstractions
│   │       ├── rag/         # RAG orchestration
│   │       └── vectorstore/ # FAISS management
│   ├── alembic/             # Database migrations
│   ├── tests/               # Test suite
│   ├── requirements.txt     # Python dependencies
│   └── startup.sh           # Docker entrypoint
├── frontend/
│   ├── src/
│   │   ├── app/             # App bootstrap
│   │   ├── components/      # UI components (Radix, layout)
│   │   ├── contexts/        # React contexts (auth)
│   │   ├── features/        # Feature modules
│   │   ├── pages/           # Route pages
│   │   ├── routes/          # Router configuration
│   │   ├── services/        # API client (axios)
│   │   ├── styles/          # Global styles (Tailwind)
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml       # Development orchestration
├── docker-compose.production.yml
├── Dockerfile.backend        # Multi-stage backend build
├── Dockerfile.frontend       # Multi-stage frontend build
├── nginx.conf                # Reverse proxy configuration
├── docs/                     # Project documentation
│   ├── API.md, Architecture.md, Database.md
│   ├── PRD.md, SRS.md, BRD.md
│   └── DECISIONS.md, Testing.md, Deployment.md
├── assets/screenshots/       # Application screenshots
├── .github/                  # CI/CD, issue templates
│   ├── workflows/ci.yml
│   └── ISSUE_TEMPLATE/
├── ARCHITECTURE.md           # Detailed architecture docs
├── CHANGELOG.md              # Release history
├── CONTRIBUTING.md           # Contribution guide
├── ROADMAP.md                # Development roadmap
├── SECURITY.md               # Security policy
├── CODE_OF_CONDUCT.md        # Community guidelines
├── LICENSE                   # MIT license
└── README.md                 # This file
```

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| ⏱️ Setup Time | ~5 minutes (Docker) |
| 📝 Language | Python 3.12, TypeScript 5.7 |
| 📦 Dependencies | 25+ Python packages, 15+ npm packages |
| 🐳 Docker Images | 3 services + optional Ollama |
| 🗄️ Database | PostgreSQL 16 with 6 tables |
| 📄 Documentation | 15+ markdown files |

---

## 🗺️ Roadmap

### Version 1.0 (Current) ✅
Core OCR, RAG, chat, authentication, Docker deployment

### Version 1.1 (Upcoming) 🚧
Advanced RAG reranking, document summarization, test coverage, pre-commit hooks

### Version 1.2 (Planned) 📋
Web search, multi-document chat, Redis caching, Celery workers, metrics

### Version 2.0 (Future) 💡
Multi-tenant, SSO, Kubernetes, admin dashboard, plugins

See [ROADMAP.md](ROADMAP.md) for full details.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) for details.

**Quick steps:**
1. Fork the repository
2. Create a feature branch (`feature/amazing-feature`)
3. Commit your changes (`feat: add amazing feature`)
4. Push to your branch
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the incredible Python web framework
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for OCR capabilities
- [FAISS](https://github.com/facebookresearch/faiss) by Meta for vector search
- [SentenceTransformers](https://www.sbert.net/) for embedding models
- [Ollama](https://ollama.ai/) for local LLM inference
- All open-source contributors whose libraries made this possible

---

## 👤 Author

**Swastik Pandey**

- GitHub: [@SwastikPandey1024](https://github.com/SwastikPandey1024)
- LinkedIn: [swastik-pandey-a02719297](https://www.linkedin.com/in/swastik-pandey-a02719297)

---

<div align="center">
  <strong>Built with ❤️ for intelligent document understanding</strong>
  <br />
  <sub>If you find this project useful, consider giving it a ⭐!</sub>
</div>

