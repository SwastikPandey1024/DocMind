# DocMind AI

AI-powered OCR + RAG Document Chat System

DocMind AI is a production-oriented document intelligence platform that lets users upload PDFs, extract text using OCR, index the content, and converse with their documents through a Retrieval-Augmented Generation (RAG) pipeline.

## ✨ Features
- PDF upload and document management
- OCR extraction using PaddleOCR
- Text cleaning and chunking
- Embedding generation and vector search with FAISS
- Semantic document Q&A using LangChain + Ollama/OpenAI
- Secure authentication and chat history
- React-based frontend and FastAPI backend
- Dockerized deployment support

## 🏗️ Architecture

```text
User -> React Frontend -> FastAPI Backend -> OCR / RAG / LLM Services -> PostgreSQL + FAISS
```

## 🛠️ Tech Stack
### Frontend
- React
- Vite
- TailwindCSS

### Backend
- FastAPI
- Pydantic
- SQLAlchemy

### Database & Search
- PostgreSQL
- FAISS

### AI / OCR
- PaddleOCR
- LangChain
- HuggingFace Embeddings
- Ollama / OpenAI

### DevOps
- Docker
- GitHub Actions

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop
- PostgreSQL

### Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend exposes Swagger UI at http://127.0.0.1:8000/docs and ReDoc at http://127.0.0.1:8000/redoc.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up --build
```

## 📁 Project Structure
```text
document-chat-system/
├── backend/
├── frontend/
├── storage/
├── tests/
├── docker/
├── docs/
└── scripts/
```

## 📚 Documentation
- Architecture: [docs/Architecture.md](docs/Architecture.md)
- Database Design: [docs/Database.md](docs/Database.md)
- API Spec: [docs/API.md](docs/API.md)
- PRD: [docs/PRD.md](docs/PRD.md)
- SRS: [docs/SRS.md](docs/SRS.md)

## 🤝 Contributing
Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

## 📄 License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
