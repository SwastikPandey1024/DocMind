# Project Roadmap

> *Last updated: July 2026*

DocuChat is under active development. This roadmap outlines planned features and improvements for upcoming releases. It is a living document and may change based on community feedback and project priorities.

---

## Legend

| Icon | Meaning |
|------|---------|
| ✅    | Completed |
| 🚧    | In Progress |
| 📋    | Planned |
| 💡    | Under Consideration |

---

## Version 1.0 — Current Release ✅

### Foundation
- ✅ Project scaffolding and architecture design
- ✅ FastAPI backend with modular service layer
- ✅ React frontend with TypeScript and TailwindCSS
- ✅ PostgreSQL database with Alembic migrations
- ✅ Docker Compose for development and production

### Authentication
- ✅ JWT-based authentication (access + refresh tokens)
- ✅ User registration and login
- ✅ Password hashing with Argon2
- ✅ Role-based access control (RBAC)

### Document Management
- ✅ PDF upload with validation and duplicate detection
- ✅ Document metadata storage (name, size, pages, status)
- ✅ Soft-delete for data retention
- ✅ Document listing and deletion

### OCR Pipeline
- ✅ PaddleOCR integration for text extraction
- ✅ Multi-language OCR support (English, Chinese, and more)
- ✅ Text cleaning and normalization
- ✅ OCR page metadata with confidence scores

### RAG Pipeline
- ✅ Semantic text chunking with configurable overlap
- ✅ SentenceTransformers embeddings (BGE, MiniLM models)
- ✅ FAISS vector indexing with L2 similarity
- ✅ Persistent vector store with save/load

### Chat System
- ✅ Document-aware question answering
- ✅ Streaming responses via Server-Sent Events
- ✅ Chat history persistence
- ✅ Context retrieval with source citations

### LLM Integration
- ✅ Ollama support for local LLM inference
- ✅ OpenAI GPT integration (optional fallback)
- ✅ Abstract provider interface for extensibility
- ✅ Configurable model selection

### Deployment
- ✅ Docker multi-stage builds (optimized images)
- ✅ Docker Compose for full-stack orchestration
- ✅ Production-ready Nginx configuration
- ✅ Health check endpoints
- ✅ Environment variable configuration

---

## Version 1.1 — Q3 2026 🚧

### Performance & Reliability
- 📋 Advanced RAG with multi-query reranking
- 📋 Embedding caching for faster processing
- 📋 Connection pooling optimization
- 📋 Request rate limiting

### User Experience
- 📋 Document summarization feature
- 📋 Export chat history (PDF, Markdown)
- 📋 Dark mode improvements
- 📋 Mobile-responsive design polish

### Developer Experience
- 📋 Pre-commit hooks configuration
- 📋 Expanded test coverage
- 📋 API client SDK (Python)

---

## Version 1.2 — Q4 2026 📋

### Advanced Features
- 📋 Web search integration for supplementary context
- 📋 Multi-document chat across knowledge base
- 📋 Table-aware document parsing
- 📋 Image analysis and description

### Infrastructure
- 📋 Redis caching layer for sessions and queries
- 📋 Celery task queue for background processing
- 📋 Prometheus metrics & Grafana dashboards
- 📋 Structured JSON logging

### Integration
- 📋 Webhook notifications for document processing
- 📋 API key management for external access
- 📋 S3-compatible object storage support

---

## Version 2.0 — 2027 💡

### Enterprise
- 💡 Multi-tenant architecture with full isolation
- 💡 Single Sign-On (SSO) — OAuth2, SAML, OpenID Connect
- 💡 Audit logging and compliance reporting
- 💡 Admin dashboard with usage analytics

### Scale
- 💡 Kubernetes (K8s) deployment manifests
- 💡 Distributed FAISS across multiple nodes
- 💡 Horizontal scaling with load balancing
- 💡 Blue-green deployment strategy

### Platform
- 💡 Plugin system for custom document processors
- 💡 Custom model fine-tuning interface
- 💡 Collaborative document annotation
- 💡 Real-time collaboration features

---

## Past Releases

| Version | Date       | Highlights                                  |
|---------|------------|---------------------------------------------|
| 1.0.0   | July 2026  | Initial release with core OCR, RAG, and chat |

---

## How to Contribute

See our [Contributing Guide](CONTRIBUTING.md) for details on:

- Suggesting new features via [Feature Requests](.github/ISSUE_TEMPLATE/feature_request.md)
- Reporting bugs via [Bug Reports](.github/ISSUE_TEMPLATE/bug_report.md)
- Submitting pull requests for planned features

---

## Disclaimer

This roadmap is for informational purposes only. Features and timelines may change based on community feedback, development capacity, and project priorities. We make no guarantees about the availability of specific features in any particular release.

