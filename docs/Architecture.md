# System Architecture

## Project
DocuChat AI - Intelligent OCR Document Chat System

## Version
| Version | Date | Author |
|----------|------|--------|
| 1.0 | July 2026 | Swastik Pandey |

## 1. Architecture Overview
DocuChat AI follows a modular, service-oriented architecture to separate responsibilities across presentation, business logic, AI processing, data storage, and external services. This design enables scalability, maintainability, and future extensibility.

## 2. High-Level Architecture
```text
                    User
                     │
                     ▼
             React Frontend
                     │
          HTTPS / REST API
                     │
                     ▼
              FastAPI Backend
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
 Authentication  PostgreSQL  OCR Service
                               │
                               ▼
                         Text Cleaning
                               │
                               ▼
                           Chunking
                               │
                               ▼
                    HuggingFace Embeddings
                               │
                               ▼
                          FAISS Index
                               │
                               ▼
                          Retriever
                               │
                               ▼
                     Prompt Construction
                               │
                               ▼
                     Ollama / OpenAI LLM
                               │
                               ▼
                        AI Generated Answer
                               │
                               ▼
                           React Frontend
```

## 3. Architecture Principles
- Modular Design
- Separation of Concerns
- API-First Development
- Stateless Backend
- Secure Authentication
- Production-Ready Deployment
- Scalable Components

## 4. Core Components
### 4.1 Frontend
**Responsibilities**
- User login and registration
- PDF upload and document management
- Chat interface and history
- Dashboard and settings

**Technology**
- React
- Vite
- TailwindCSS
- Axios

### 4.2 Backend
**Responsibilities**
- Authentication and authorization
- API routing and validation
- Business logic orchestration
- Error handling and logging

**Technology**
- FastAPI
- SQLAlchemy
- Pydantic

### 4.3 OCR Service
**Responsibilities**
- Convert PDF pages into images
- Perform OCR extraction
- Enhance image quality
- Detect and preserve document structure

**Technology**
- PaddleOCR
- PyMuPDF
- pdf2image
- Pillow

### 4.4 RAG Engine
**Responsibilities**
- Chunk text into semantically meaningful segments
- Generate embeddings
- Store and search vectors in FAISS
- Retrieve relevant context for answer generation
- Construct prompts for the LLM

**Technology**
- LangChain
- HuggingFace Embeddings
- FAISS

### 4.5 LLM Service
**Responsibilities**
- Generate context-aware responses
- Support conversational interaction
- Ground answers in retrieved document chunks

**Technology**
- Ollama
- OpenAI API

### 4.6 Database
**Responsibilities**
- Store user accounts
- Store document metadata
- Track OCR status and processing history
- Maintain chat history and user interactions

**Technology**
- PostgreSQL

## 5. Request Lifecycle
1. User uploads a PDF document.
2. The backend validates and stores the request.
3. The PDF is converted into images for OCR processing.
4. OCR extracts the document text.
5. The text is cleaned and normalized.
6. The cleaned text is split into chunks.
7. Embeddings are generated for each chunk.
8. The vectors are stored in FAISS.
9. Metadata is stored in PostgreSQL.
10. The user asks a question about the document.
11. Relevant chunks are retrieved from FAISS.
12. A prompt is constructed using the retrieved context.
13. The LLM generates a response.
14. The response is returned to the frontend.
15. The conversation is stored for future reference.

## 6. OCR Pipeline
```text
PDF
↓
Image Conversion
↓
Image Preprocessing
↓
PaddleOCR
↓
Text Cleaning
↓
Structured Text
```

## 7. RAG Pipeline
```text
Document
↓
Chunking
↓
Embeddings
↓
FAISS
↓
Retriever
↓
Prompt
↓
LLM
↓
Answer
```

## 8. Database Usage
### PostgreSQL Stores
- Users
- Documents
- Document metadata
- Chat history
- OCR processing status

### FAISS Stores
- Vector embeddings for semantic retrieval

## 9. Security
- JWT-based authentication
- Password hashing
- Input validation
- Role-based access control
- HTTPS in production
- File validation for uploaded documents

## 10. Logging
- Application logs
- API logs
- OCR logs
- AI logs
- Authentication logs

## 11. Error Handling
- Global exception handler
- API validation errors
- OCR failure recovery
- Retry logic for transient services
- Centralized logging

## 12. Scalability
- Horizontal API scaling
- Docker-based deployment
- Cloud deployment readiness
- Support for large documents and background processing

## 13. Technology Decision Records
### React
**Reason:** Enables fast frontend development and a modern user experience.

### FastAPI
**Reason:** Provides high performance and automatic API documentation.

### PaddleOCR
**Reason:** Offers strong OCR accuracy with multilingual support.

### PostgreSQL
**Reason:** Provides reliable relational storage for metadata and user data.

### FAISS
**Reason:** Supports efficient vector similarity search.

### LangChain
**Reason:** Simplifies retrieval-augmented generation workflows.

### Ollama/OpenAI
**Reason:** Provides flexible and high-quality language model inference.

### Docker
**Reason:** Ensures consistent deployment across development and production environments.

## 14. Implementation Notes
- Backend runtime target: Python 3.12+ with FastAPI as the API framework.
- Dependency management uses both backend/pyproject.toml and backend/requirements.txt for local development and packaging compatibility.
- The API is structured around versioned routers under the backend/app/api/v1 package to support future expansion without breaking backward compatibility.
- SQLAlchemy models are organized under backend/app/models and are designed for PostgreSQL-backed persistence with Alembic migration readiness.
- Health checks and API documentation are exposed through the FastAPI default /docs and /redoc endpoints.

## 15. Future Improvements
- Redis caching
- Background workers for asynchronous processing
- Kubernetes-based orchestration
- Monitoring and observability
- CI/CD automation
- Object storage integration
- Multi-tenant support
