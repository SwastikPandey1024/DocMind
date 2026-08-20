# Docker Assets

This folder contains container definitions and supporting files for running the system locally or in a production environment.

## Expected Files
- docker-compose.yml
- Dockerfile.backend
- Dockerfile.frontend
- nginx.conf

## Local Database

The root `docker-compose.yml` starts a PostgreSQL container for local development.

```bash
docker compose up -d postgres
```

The backend expects:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/docuchat
```
