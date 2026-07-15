# Backend Service

This folder contains the FastAPI backend for document ingestion, OCR processing, vector indexing, retrieval, and chat orchestration.

## Folder Structure
- app/core: shared configuration, settings, and logging
- app/api: versioned API routes, schemas, and dependencies
- app/models: SQLAlchemy ORM models
- app/schemas: request and response models
- app/database: database session and migration helpers
- app/services: business logic and integrations
- tests: backend test coverage

## Runtime Notes
- Python 3.12+ is targeted for the backend scaffold.
- Dependency management uses the backend pyproject.toml and requirements.txt files.
- The app entrypoint is app.main:app and can be served with uvicorn.

## Local Database

Start PostgreSQL from the repository root:

```bash
docker compose up -d postgres
```

Run migrations from the backend folder:

```bash
python -m alembic upgrade head
```

The default local database URL is:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/docmind
```
