# Environment Variables Migration Guide - Docker Deployment

**Scope:** Changes required for Docker Compose orchestration  
**Status:** Analysis only - no implementation  

---

## 1. CRITICAL ENVIRONMENT VARIABLE CHANGES

### 1.1 Database Connection String

**Current Default (Development):**
```
localhost:5432 (host machine)
```

**In Docker Container:**
```
postgres:5432 (Docker service name)
```

**Change Required:**

| Context | Current | Required | Reason |
|---------|---------|----------|--------|
| Local dev (no Docker) | `postgresql+psycopg2://postgres:postgres@localhost:5432/docmind` | No change | localhost works |
| Docker Compose | N/A (uses default) | `postgresql+psycopg2://postgres:{DB_PASS}@postgres:5432/docmind` | Service name DNS |
| Production (cloud) | N/A | `postgresql+psycopg2://postgres:{DB_PASS}@db.example.com:5432/docmind` | RDS/managed DB |

**Implementation Pattern:**

File: `docker-compose.yml`
```yaml
services:
  backend:
    environment:
      DATABASE_URL: "postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"
```

File: `.env` (docker-compose reads this)
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=docmind
```

**Backend Code (NO CHANGES NEEDED):**
```python
# backend/app/core/settings.py
database_url: str = Field(
    default="postgresql+psycopg2://postgres:postgres@localhost:5432/docmind",
    validation_alias="DATABASE_URL"  # ← Reads from environment
)
```

Backend will use `DATABASE_URL` env var if set, otherwise use default (localhost). In Docker, env var will be set.

---

### 1.2 Ollama/LLM Host

**Current Default:**
```
http://localhost:11434
```

**In Docker Container:**
```
http://ollama:11434
```

**Change Required:**

| Context | Current | Required | Reason |
|---------|---------|----------|--------|
| Local dev (no Docker) | `http://localhost:11434` | No change | localhost works |
| Docker Compose | N/A (uses default) | `http://ollama:11434` | Service name DNS |
| Production (cloud) | N/A | `http://ollama.example.com:11434` or managed LLM endpoint | External service |

**Implementation Pattern:**

File: `docker-compose.yml`
```yaml
services:
  backend:
    environment:
      OLLAMA_HOST: "${OLLAMA_HOST:-http://ollama:11434}"
```

File: `.env`
```
OLLAMA_HOST=http://ollama:11434
```

**Backend Code (NO CHANGES NEEDED):**
```python
# backend/app/core/settings.py
ollama_host: str = Field(
    default="http://localhost:11434",
    validation_alias="OLLAMA_HOST"  # ← Reads from environment
)
```

---

### 1.3 Upload Directory

**Current Default:**
```
./storage/uploads (relative to container working directory)
```

**In Docker Container:**
```
/app/storage/uploads (absolute path, mounted from host)
```

**Change Required:**

| Context | Current | Required | Reason |
|---------|---------|----------|--------|
| Local dev (no Docker) | `./storage/uploads` | No change | Relative path works |
| Docker Compose | N/A (uses default) | `/app/storage/uploads` | Absolute path for mount |
| Production | N/A | `/app/storage/uploads` | Consistent path |

**Implementation Pattern:**

File: `docker-compose.yml`
```yaml
services:
  backend:
    volumes:
      - ./storage/uploads:/app/storage/uploads
      - ./storage/vectors:/app/storage/vectors
      - ./storage/logs:/app/logs
    environment:
      UPLOAD_DIR: "/app/storage/uploads"
```

File: `.env`
```
UPLOAD_DIR=/app/storage/uploads
```

**Backend Code (NO CHANGES NEEDED):**
```python
# backend/app/core/settings.py
upload_dir: str = Field(
    default="./storage/uploads",
    validation_alias="UPLOAD_DIR"  # ← Reads from environment
)
```

---

### 1.4 Frontend API Base URL

**Current Default:**
```
(no default - must be set at build time for Vite)
```

**In Docker Development:**
```
http://backend:8000
```

**In Production:**
```
https://api.example.com
```

**Change Required:**

| Context | Current | Required | Reason |
|---------|---------|----------|--------|
| Local dev | `http://localhost:8000` | `http://localhost:8000` | Frontend and backend on host |
| Docker Compose | Must be set | `http://backend:8000` | Backend service name |
| Production | Must be set | `https://api.example.com` | Production domain |

**Implementation Pattern:**

File: `docker-compose.yml`
```yaml
services:
  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_BASE_URL: "http://backend:8000"
    environment:
      VITE_API_BASE_URL: "http://backend:8000"
```

File: `.env.docker`
```
VITE_API_BASE_URL=http://backend:8000
```

**Frontend Code (NO CHANGES NEEDED):**
```typescript
// frontend/src/services/api.ts
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
});
```

Frontend already reads from `VITE_API_BASE_URL` env var with fallback.

---

### 1.5 Database Credentials (Security)

**Current State:**
```
Hardcoded in docker-compose.yml:
POSTGRES_PASSWORD: postgres
```

**Required Change:**

```yaml
# Before (WRONG - hardcoded, visible in git):
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: postgres  ← Bad!

# After (CORRECT - from environment):
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?error "POSTGRES_PASSWORD required"}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-docmind}
```

File: `.env` (git-ignored)
```
POSTGRES_PASSWORD=generate-secure-random-string-here
```

**No Backend Code Changes:**
```python
# Backend uses DATABASE_URL which includes password
database_url: str = Field(
    default="postgresql+psycopg2://postgres:postgres@localhost:5432/docmind",
    validation_alias="DATABASE_URL"
)
```

---

### 1.6 JWT Secret (Security)

**Current Default:**
```
change-me-in-production
```

**Required Change:**

File: `.env`
```
JWT_SECRET=your-random-secret-key-generate-with-secrets-module-or-openssl
```

**Backend Code (NO CHANGES NEEDED):**
```python
# backend/app/core/settings.py
jwt_secret: str = Field(
    default="change-me-in-production",
    validation_alias="JWT_SECRET"  # ← Reads from environment
)

@field_validator("jwt_secret")
@classmethod
def validate_jwt_secret(cls, value: str, info: ValidationInfo) -> str:
    if info.data.get("environment") == Environment.PRODUCTION and value in {"change-me-in-production", ""}:
        raise ValueError("JWT_SECRET must be set in production")  # ← Already validates!
    return value
```

Backend already validates JWT_SECRET in production. Just set it in .env.

---

### 1.7 Application Environment

**Current Default:**
```
development
```

**Required Change:**

| Context | Current | Required | Reason |
|---------|---------|----------|--------|
| Local dev | `development` | No change | Debug mode OK |
| Docker dev | N/A | `development` | Debug, logs to stdout |
| Production | N/A | `production` | No debug, stricter validation |

File: `.env`
```
APP_ENV=development        # Docker dev
# or
APP_ENV=production         # Production
```

**Backend Code (NO CHANGES NEEDED):**
```python
environment: Literal["development", "testing", "production"] = Field(
    default=Environment.DEVELOPMENT,
    validation_alias="APP_ENV"
)
```

---

## 2. COMPLETE ENVIRONMENT VARIABLE REFERENCE

### Backend Environment Variables

| Variable | Current Default | Docker Compose Value | Purpose | Sensitive |
|----------|---|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg2://postgres:postgres@localhost:5432/docmind` | `postgresql+psycopg2://postgres:{POSTGRES_PASSWORD}@postgres:5432/docmind` | PostgreSQL connection | No (contains credentials) |
| `APP_ENV` | `development` | `development` | Environment mode | No |
| `DEBUG` | `false` | `false` | Debug logging | No |
| `JWT_SECRET` | `change-me-in-production` | Generated random string | JWT signing key | **YES** |
| `JWT_ALGORITHM` | `HS256` | `HS256` | JWT algorithm | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | `15` | Token TTL | No |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | `7` | Refresh token TTL | No |
| `UPLOAD_DIR` | `./storage/uploads` | `/app/storage/uploads` | Upload directory | No |
| `LOG_LEVEL` | `INFO` | `INFO` or `DEBUG` | Logging level | No |
| `OPENAI_API_KEY` | `null` | Set if using OpenAI | OpenAI API key | **YES** |
| `OLLAMA_HOST` | `http://localhost:11434` | `http://ollama:11434` | Ollama endpoint | No |

### Frontend Environment Variables

| Variable | Current Default | Docker Compose Value | Purpose | Sensitive |
|----------|---|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | `http://backend:8000` | Backend API endpoint | No |

### PostgreSQL Environment Variables

| Variable | Current Default | Docker Compose Value | Purpose | Sensitive |
|----------|---|---|---|---|
| `POSTGRES_DB` | (container env) `docmind` | `${POSTGRES_DB:-docmind}` | Database name | No |
| `POSTGRES_USER` | (container env) `postgres` | `${POSTGRES_USER:-postgres}` | DB user | No |
| `POSTGRES_PASSWORD` | (container env) `postgres` | `${POSTGRES_PASSWORD:?error required}` | DB password | **YES** |

---

## 3. ENVIRONMENT FILE TEMPLATES

### `.env.example` (for git)

```bash
# ============================================
# Database Configuration
# ============================================
POSTGRES_DB=docmind
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-me-in-production

# ============================================
# Backend Configuration
# ============================================
APP_NAME=DocMind
APP_VERSION=0.1.0
APP_ENV=development
DEBUG=true

# Database URL (auto-constructed from POSTGRES_* vars)
# or override if using external database
DATABASE_URL=postgresql+psycopg2://postgres:change-me@postgres:5432/docmind

# JWT Configuration
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Storage Configuration
UPLOAD_DIR=/app/storage/uploads

# Logging Configuration
LOG_LEVEL=INFO

# LLM Configuration
OPENAI_API_KEY=sk-your-key-here
OLLAMA_HOST=http://ollama:11434

# ============================================
# Frontend Configuration
# ============================================
VITE_API_BASE_URL=http://localhost:8000
```

### `.env` (local development, git-ignored)

```bash
# Copy from .env.example and customize for local dev
POSTGRES_PASSWORD=your-secure-local-password
JWT_SECRET=your-local-jwt-secret-random-string
OPENAI_API_KEY=sk-your-test-key
VITE_API_BASE_URL=http://localhost:8000
```

### `.env.docker` (Docker Compose, git-ignored)

```bash
# For docker-compose up
POSTGRES_PASSWORD=docker-local-password-not-production-grade
JWT_SECRET=docker-local-jwt-secret-random-string
APP_ENV=development
DEBUG=true
VITE_API_BASE_URL=http://backend:8000
OLLAMA_HOST=http://ollama:11434
```

### `.env.production` (Production, git-ignored, secrets manager)

```bash
# Generate with:
# python -c "import secrets; print(secrets.token_urlsafe(32))"

POSTGRES_PASSWORD=<generate-secure-random>
JWT_SECRET=<generate-secure-random>
OPENAI_API_KEY=<from-secrets-manager>
APP_ENV=production
DEBUG=false
VITE_API_BASE_URL=https://api.example.com
DATABASE_URL=postgresql+psycopg2://postgres:<password>@db.example.com:5432/docmind
```

---

## 4. DOCKER-COMPOSE.YML ENV VAR UPDATES

**Changes Needed in docker-compose.yml:**

```yaml
# BEFORE (current - hardcoded):
services:
  postgres:
    environment:
      POSTGRES_DB: docmind
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

# AFTER (required - using env vars):
services:
  postgres:
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-docmind}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?error "POSTGRES_PASSWORD required"}
  
  backend:
    environment:
      DATABASE_URL: "postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"
      APP_ENV: ${APP_ENV:-development}
      DEBUG: ${DEBUG:-false}
      JWT_SECRET: ${JWT_SECRET:?error "JWT_SECRET required in production"}
      UPLOAD_DIR: ${UPLOAD_DIR:-/app/storage/uploads}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OLLAMA_HOST: ${OLLAMA_HOST:-http://ollama:11434}
  
  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_BASE_URL: ${VITE_API_BASE_URL:-http://backend:8000}
    environment:
      VITE_API_BASE_URL: ${VITE_API_BASE_URL:-http://backend:8000}
```

---

## 5. MIGRATION STEPS (DO NOT IMPLEMENT YET)

1. **Create `.env.example`** in repository root
   - Document all environment variables
   - Include default values and examples
   - Mark sensitive variables with `[SENSITIVE]`

2. **Create `.env` locally** (git-ignored)
   - Copy from `.env.example`
   - Fill in local development values
   - Generate secure random strings for JWT_SECRET, POSTGRES_PASSWORD

3. **Update `docker-compose.yml`**
   - Replace hardcoded values with `${VAR_NAME}` syntax
   - Add default values with `:-` operator
   - Add required validation with `:?` operator

4. **Test locally with `docker-compose up`**
   - Verify all services start
   - Check DATABASE_URL is correct
   - Test backend can connect to postgres
   - Test frontend can call backend

5. **Setup CI/CD secrets** (GitHub Actions)
   - Store `POSTGRES_PASSWORD` as secret
   - Store `JWT_SECRET` as secret
   - Store `OPENAI_API_KEY` as secret
   - Pass to docker-compose via env file

6. **Setup production secrets** (your deployment platform)
   - Use managed secrets (AWS Secrets Manager, Azure Key Vault, etc.)
   - Generate secure random values
   - Rotate regularly

---

## 6. VALIDATION CHECKLIST

- [ ] DATABASE_URL uses `postgres` service name (not `localhost`)
- [ ] OLLAMA_HOST uses `ollama` service name (not `localhost`)
- [ ] UPLOAD_DIR is absolute path `/app/storage/uploads`
- [ ] VITE_API_BASE_URL is `http://backend:8000` for Docker
- [ ] JWT_SECRET is generated and not hardcoded
- [ ] POSTGRES_PASSWORD is externalized to .env
- [ ] All sensitive vars marked in documentation
- [ ] .env file exists and is git-ignored
- [ ] .env.example committed to git
- [ ] docker-compose.yml uses variable substitution syntax
- [ ] No credentials hardcoded in any YAML files
- [ ] Backend passes settings validation in production mode
- [ ] `docker-compose config` shows correct values
- [ ] `docker-compose up` starts all services
- [ ] Backend logs show successful database connection
- [ ] Frontend can call backend API

---

**End of Environment Variables Migration Guide**

*Analysis complete - no files modified, no implementation yet*
