# DocMind AI - Docker Deployment Guide

## Quick Start

### Development Environment

```bash
# Copy environment template
cp .env.example .env

# Start all services
docker-compose up --build

# Access services
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432
- Ollama: http://localhost:11434
```

### First Time Setup

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Wait for services to be healthy
docker-compose ps

# Check backend logs
docker-compose logs backend

# Run migrations manually (if needed)
docker-compose exec backend alembic upgrade head

# Download Ollama model (optional)
docker-compose exec ollama ollama pull llama2
```

## Production Deployment

### Prepare Production Environment

```bash
# Create production environment file
cp .env.production.example .env.production

# Update with your values
nano .env.production

# Set secure credentials
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD
JWT_SECRET=YOUR_RANDOM_SECRET_KEY
OPENAI_API_KEY=YOUR_API_KEY
```

### Deploy

```bash
# Using production compose file
docker-compose -f docker-compose.production.yml up -d

# Verify services
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f backend
```

## Verification

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend
curl http://localhost/

# Database
docker-compose exec postgres pg_isready -U postgres

# Ollama
curl http://localhost:11434/api/tags
```

### Database

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d docmind

# Run migrations
docker-compose exec backend alembic upgrade head

# Downgrade migrations
docker-compose exec backend alembic downgrade -1

# Check migration status
docker-compose exec backend alembic current
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Verify database connection
docker-compose exec backend python -c "from app.database.engine import engine; engine.connect()"

# Check environment variables
docker-compose exec backend env | grep DATABASE_URL
```

### Frontend shows blank page

```bash
# Check Nginx logs
docker-compose logs frontend

# Verify backend connectivity from frontend
docker-compose exec frontend curl http://backend:8000/health

# Check API base URL
docker-compose exec frontend cat /etc/nginx/nginx.conf
```

### Database connection refused

```bash
# Ensure PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Verify ports
docker-compose port postgres 5432
```

## Management

### Stop Services

```bash
# Graceful shutdown
docker-compose down

# Remove volumes too
docker-compose down -v

# Remove all images
docker-compose down -v --rmi all
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Follow specific pattern
docker-compose logs backend | grep ERROR
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Clean build cache
docker builder prune
```

## Performance Tuning

### Memory Limits

Edit `docker-compose.yml`:

```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 2G
      reservations:
        memory: 1G
```

### Database Performance

```bash
# Check connection pool
docker-compose exec backend python -c "from app.database.engine import engine; print(engine.pool)"

# Monitor queries
docker-compose exec postgres tail -f /var/log/postgresql/postgresql.log
```

## Backup & Restore

### Backup Database

```bash
# Backup to file
docker-compose exec postgres pg_dump -U postgres docmind > backup.sql

# Backup with compression
docker-compose exec postgres pg_dump -U postgres docmind | gzip > backup.sql.gz
```

### Restore Database

```bash
# Restore from file
docker-compose exec -T postgres psql -U postgres docmind < backup.sql

# Restore from compressed
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U postgres docmind
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - JWT signing key
- `OPENAI_API_KEY` - OpenAI API key (optional, Ollama is fallback)
- `OLLAMA_HOST` - Ollama server URL
- `EMBEDDING_MODEL` - HuggingFace model for embeddings
- `VITE_API_BASE_URL` - Frontend API endpoint

## Architecture

```
┌─────────────────────────────┐
│      Nginx (Frontend)       │
│     :80 -> React build      │
└──────────┬──────────────────┘
           │ /api proxy
┌──────────▼──────────────────┐
│   FastAPI Backend           │
│   :8000 -> Python app       │
└──────────┬──────────────────┘
           │
      ┌────┴─────┬──────────┐
      │           │          │
┌─────▼─┐  ┌─────▼──┐  ┌────▼────┐
│PostgreSQL│ │  Ollama │ │  FAISS  │
│  :5432  │  │ :11434 │  │ memory  │
└─────────┘  └────────┘  └─────────┘
```

All services communicate via Docker bridge network `docmind`.
