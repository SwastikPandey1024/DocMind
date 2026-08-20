# Software Requirements Specification (SRS)

## Project
DocuChat AI - OCR Powered Intelligent Document Chat System

## Version
| Version | Date | Author |
|----------|------|--------|
| 1.0 | July 2026 | Swastik Pandey |

## 1. Introduction
### 1.1 Purpose
This document specifies the software requirements for developing an AI-powered document chat system that enables users to upload PDF documents, extract text using OCR, generate embeddings, retrieve relevant information using RAG, and interact with documents through natural language conversations.

### 1.2 Scope
The system provides:
- PDF upload and management
- OCR extraction from scanned documents
- Text preprocessing and cleaning
- Chunk generation and indexing
- Embedding creation and storage
- Vector search and retrieval
- AI-powered chat responses
- User authentication and chat history
- PostgreSQL metadata storage

## 2. Overall Description
### 2.1 Product Perspective
The system is a web application consisting of a React frontend, a FastAPI backend, an OCR service, a RAG engine, a PostgreSQL database, and an LLM inference layer. The architecture supports modular processing from document ingestion to response generation.

### 2.2 User Classes
- Guest
- Registered User
- Administrator

### 2.3 Operating Environment
#### Frontend
- React
- TailwindCSS

#### Backend
- Python 3.12
- FastAPI

#### Database
- PostgreSQL

#### AI and Retrieval Stack
- PaddleOCR
- LangChain
- FAISS
- HuggingFace Embeddings
- Ollama/OpenAI

#### Deployment
- Docker
- Linux-based environment

## 3. Functional Requirements
### 3.1 Authentication
- FR-01: The system shall allow users to register an account.
- FR-02: The system shall allow users to log in securely.
- FR-03: The system shall allow users to log out.
- FR-04: The system shall use JWT-based authentication for protected routes.

### 3.2 Document Module
- FR-05: The system shall allow users to upload PDF files.
- FR-06: The system shall allow users to delete uploaded documents.
- FR-07: The system shall list all uploaded documents for a user.
- FR-08: The system shall store and display document metadata.

### 3.3 OCR Module
- FR-09: The system shall convert PDF pages into images for OCR processing.
- FR-10: The system shall extract text from scanned and digital PDF documents.
- FR-11: The system shall enhance image quality before OCR where feasible.
- FR-12: The system shall clean and normalize OCR output.

### 3.4 RAG Module
- FR-13: The system shall split extracted text into logical chunks.
- FR-14: The system shall generate embeddings for each chunk.
- FR-15: The system shall store the embeddings and index in FAISS.
- FR-16: The system shall retrieve semantically similar chunks for a query.
- FR-17: The system shall construct prompts using the retrieved context.
- FR-18: The system shall generate AI responses grounded in retrieved context.

### 3.5 Chat Module
- FR-19: The system shall allow users to ask questions about uploaded documents.
- FR-20: The system shall store conversation history.
- FR-21: The system shall allow users to view previous chats.

### 3.6 User Module
- FR-22: The system shall support basic profile management.
- FR-23: The system shall allow users to update their password.

## 4. Non-Functional Requirements
### 4.1 Performance
- OCR processing for a moderate 20-page document shall complete within 10 seconds under normal conditions.
- Chat responses shall be returned in less than 5 seconds for standard queries.

### 4.2 Security
- The system shall use JWT-based authentication.
- Passwords shall be stored using secure hashing.
- The system shall validate all user inputs.
- HTTPS shall be used in production deployments.
- Role-based access shall be supported for administrators.

### 4.3 Reliability
- The system shall log errors and operational events.
- The system shall provide graceful handling for failed OCR or retrieval steps.
- The system shall support retry logic for transient failures.

### 4.4 Maintainability
- The system shall be implemented using modular code organization.
- The system shall follow a service-oriented architecture.
- Unit tests and documentation shall be maintained for core modules.

### 4.5 Scalability
- The system shall support multiple concurrent users.
- The system shall support large document uploads and multi-document indexing.
- The system shall support deployment in containerized environments.

## 5. External Interfaces
### 5.1 User Interface
The system shall provide a React-based dashboard including login, upload, chat, history, and settings screens.

### 5.2 APIs
The backend shall expose REST endpoints such as:
- POST /auth/register
- POST /auth/login
- POST /documents/upload
- GET /documents
- POST /chat
- GET /history

### 5.3 Database
The system shall use PostgreSQL to store:
- Users
- Documents
- OCR text
- Chunks
- Embeddings metadata
- Chat history

## 6. Data Flow
1. User uploads a PDF.
2. The document is processed by the OCR module.
3. Extracted text is cleaned and normalized.
4. Text is chunked into smaller segments.
5. Embeddings are generated for each chunk.
6. The vector index is stored in FAISS.
7. The retrieval module fetches relevant chunks for a user query.
8. The LLM generates a response grounded in the retrieved context.
9. The response is returned to the user in the chat interface.

## 7. Constraints
- Internet access may be required for cloud-based LLM usage.
- GPU availability is optional and may vary by deployment environment.
- Open-source tools are preferred for the initial implementation.
- The project timeline is constrained by academic or internship delivery requirements.

## 8. Assumptions
- Users upload PDF documents in standard formats.
- PostgreSQL is available for application data storage.
- FAISS indexes can be stored locally or in a mounted volume.
- PaddleOCR and required Python dependencies are available in the environment.

## 9. Future Enhancements
- Multi-document chat across an entire knowledge base
- Table-aware retrieval and structured data extraction
- Voice-based interaction and speech-to-text support
- Image-based OCR and document annotation
- Cloud storage integration and enterprise deployment
- Fine-tuned domain-specific LLMs

## 10. System Context Diagram
```text
+--------------------+
|       User         |
+---------+----------+
          |
          v
+--------------------+
|   React Frontend   |
+---------+----------+
          |
          v
+--------------------+
|   FastAPI Backend  |
+---------+----------+
          |
    +-----+------+--------------------+
    |            |                    |
    v            v                    v
 PaddleOCR   PostgreSQL           FAISS
    |                                 |
    +-------------+-------------------+
                  |
                  v
             LangChain
                  |
                  v
          Ollama / OpenAI
                  |
                  v
               Response
```
