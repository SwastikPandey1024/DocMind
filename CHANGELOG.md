# Changelog

All notable changes to DocuChat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-20

### Added

#### Authentication & User Management
- JWT-based authentication with access (15 min) and refresh (7 days) tokens
- User registration with email, name, and password
- Secure password hashing using Argon2
- Role-based access control (RBAC) with user/admin roles
- Token refresh endpoint for seamless re-authentication

#### Document Management
- PDF upload with file type and size validation
- SHA-256 checksum deduplication to prevent duplicate uploads
- Document status tracking (uploading → processing → ready → failed)
- Document metadata: file name, size, MIME type, page count
- Soft-delete support for data retention and recovery
- List, view, and delete operations for user documents

#### OCR Pipeline
- PaddleOCR integration for high-accuracy text extraction
- Multi-language OCR support (English, Chinese, and extendable)
- Per-page text extraction with bounding boxes and confidence scores
- Automatic text cleaning and normalization
- OCR artifact correction and noise removal
- Image preprocessing for improved OCR quality

#### RAG (Retrieval-Augmented Generation) Pipeline
- Semantic text chunking with recursive splitting strategy
- Configurable chunk size (default: 512 characters) with overlap support
- Token estimation for LLM context window management
- SentenceTransformers embeddings (BGE-small, BGE-base, BGE-large, MiniLM)
- Batch embedding generation for performance optimization
- FAISS vector indexing with L2 distance similarity search
- Persistent vector store with save/load from disk
- Per-document vector store management with lazy loading

#### Chat System
- Document-aware question answering with RAG context
- Streaming responses via Server-Sent Events (SSE)
- Chat history persistence with user and document association
- Source citation with relevant chunk references
- Configurable temperature for LLM response generation
- Support for both streaming and non-streaming chat modes

#### LLM Integration
- Abstract provider interface for model-agnostic design
- Ollama provider for local LLM inference
- OpenAI provider for cloud-based GPT models
- Automatic fallback between providers
- Configurable model selection per request

#### API & Infrastructure
- FastAPI RESTful API with automatic OpenAPI/Swagger documentation
- Health check (`/health`) and readiness (`/ready`) endpoints
- CORS middleware for cross-origin requests
- Global exception handler with consistent error responses
- Structured request logging for audit trails
- PostgreSQL database with SQLAlchemy ORM
- Alembic migrations for schema versioning
- Async/await architecture for high concurrency
- Comprehensive input validation with Pydantic schemas

#### Frontend
- React 19 SPA with TypeScript and Vite
- TailwindCSS utility-first styling
- Login, registration, and dashboard pages
- Document upload and management interface
- Chat interface with streaming responses
- Responsive design with mobile support
- Authentication state management with React Context
- React Query for server state management
- Radix UI primitives for accessible components

#### Docker & Deployment
- Multi-stage Docker builds for backend (3-stage: build → wheels → runtime)
- Multi-stage Docker builds for frontend (build → nginx)
- Docker Compose for development with hot-reload
- Docker Compose for production with resource limits
- Nginx reverse proxy with SPA routing and API proxying
- Health checks for all services
- Non-root user execution for container security
- Volume management for persistent data

#### Documentation
- Architecture documentation with system diagrams
- Deployment guide with Docker, K8s, and backup instructions
- API documentation with endpoint examples
- Database schema documentation with ERD
- Product Requirements Document (PRD)
- Software Requirements Specification (SRS)
- Business Requirements Document (BRD)
- Architecture Decision Records (ADRs)

### Security
- JWT authentication with configurable token expiration
- Argon2 password hashing (industry standard)
- SQL injection protection via SQLAlchemy ORM
- XSS protection via React's automatic escaping
- Input validation on all API endpoints
- File type and size validation for uploads
- Checksum verification for document integrity
- Soft-delete for audit trail compliance
- CORS origin restriction configuration

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Fixed
- N/A (initial release)

### Removed
- N/A (initial release)

---

## [0.2.0] - 2026-07-10

### Added
- Authentication flow implementation
- OCR pipeline integration
- RAG indexing and chat experience
- Docker deployment improvements

---

## [0.1.0] - 2026-07-01

### Added
- Initial project scaffolding
- Backend and frontend folder structure
- Documentation set for BRD, PRD, SRS, and architecture
- Database schema and migration scaffold
- API route structure for authentication, documents, OCR, embeddings, and chat

---

## Template

This project follows [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

---

[1.0.0]: https://github.com/SwastikPandey1024/DocuChat/releases/tag/v1.0.0
[0.2.0]: https://github.com/SwastikPandey1024/DocuChat/releases/tag/v0.2.0
[0.1.0]: https://github.com/SwastikPandey1024/DocuChat/releases/tag/v0.1.0

