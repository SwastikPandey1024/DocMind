# Docker Compose Analysis - DocMind AI

**Status:** Incomplete for production use  
**Review Date:** 2024  
**Current State:** Single-service (PostgreSQL only)

---

## 1. CURRENT CONFIGURATION REVIEW

### ✅ WHAT'S WORKING

#### PostgreSQL Service
```yaml
postgres:
  image: postgres:16-alpine          ✅ Modern LTS version
  container_name: docmind-postgres   ✅ Named container
  restart: unless-stopped             ✅ Production-safe policy
  environment:
    POSTGRES_DB: docmind             ✅ Explicit database name
    POSTGRES_USER: postgres          ✅ Root user defined
    POSTGRES_PASSWORD: postgres      ✅ Password set (hardcoded - see issues)
  ports:
    - "5432:5432"                    ✅ Port exposed for dev access
  volumes:
    - postgres_data:/var/lib/postgresql/data  ✅ Data persistence
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres -d docmind"]
    interval: 10s                    ✅ Health monitoring
    timeout: 5s
    retries: 5                       ✅ Reasonable retry count

volumes:
  postgres_data:                     ✅ Named volume for data
```

---

## 2. CRITICAL PROBLEMS

### PROBLEM 1: Missing Backend Service 🔴
**Severity:** CRITICAL  
**Impact:** Cannot run FastAPI application in Docker

**Current State:**
- Only PostgreSQL defined in docker-compose.yml
- Backend service completely missing
- Frontend service completely missing

**Why It Matters:**
- `docker-compose up` will only start PostgreSQL
- FastAPI app must be run separately (development only)
- No way to orchestrate full stack

**What's Missing:**
```yaml
services:
  backend:
    # NOT DEFINED - needs:
    # - build context (Dockerfile.backend)
    # - depends_on: postgres
    # - environment variables (DATABASE_URL pointing to postgres service)
    # - ports: 8000
    # - volumes: for uploads, logs
    # - healthcheck

  frontend:
    # NOT DEFINED - needs:
    # - build context (Dockerfile.frontend)
    # - ports: 80/443
    # - depends_on: backend (optional, frontend can load independently)
```

---

### PROBLEM 2: Hardcoded Database Credentials 🔴
**Severity:** CRITICAL (Production Risk)  
**Impact:** Security vulnerability, secrets in version control

**Current State:**
```yaml
environment:
  POSTGRES_PASSWORD: postgres  # Hardcoded, visible in git
```

**Why It's Bad:**
- Credentials stored in plaintext in git
- Same credentials across all environments (dev, staging, prod)
- Cannot be changed without modifying docker-compose.yml
- Violates security best practices

**What Should Be:**
```yaml
environment:
  POSTGRES_DB: ${POSTGRES_DB:-docmind}
  POSTGRES_USER: ${POSTGRES_USER:-postgres}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?error "POSTGRES_PASSWORD required"}
```

Loaded from:
- `.env` file (local dev, git-ignored)
- CI/CD secrets (GitHub Actions)
- Docker secrets (production swarms)
- Environment variables (Kubernetes, ECS)

---

### PROBLEM 3: DATABASE_URL Points to localhost 🔴
**Severity:** CRITICAL (Runtime Error)  
**Impact:** Backend cannot connect to PostgreSQL in Docker

**Current Backend Default:**
```python
# backend/app/core/settings.py
database_url: str = Field(
    default="postgresql+psycopg2://postgres:postgres@localhost:5432/docmind",
    validation_alias="DATABASE_URL"
)
```

**Problem:**
- Backend container runs in Docker network
- `localhost:5432` inside container ≠ host machine's localhost
- Connection string must use service name `postgres` (Docker DNS)
- Without override, backend WILL fail to connect

**Connection String Issue:**
```
WRONG:  postgresql+psycopg2://postgres:postgres@localhost:5432/docmind
        └─ "localhost" resolves to container itself in Docker network

CORRECT: postgresql+psycopg2://postgres:postgres@postgres:5432/docmind
         └─ "postgres" is the Docker service name
```

---

### PROBLEM 4: No Network Isolation 🔴
**Severity:** HIGH  
**Impact:** All containers on default bridge network (insecure, no service isolation)

**Current State:**
```yaml
# No networks defined
# All services on default "bridge" network (exposed)
# Any container can access postgres without authentication
```

**What Should Be:**
```yaml
networks:
  docmind:
    driver: bridge

services:
  postgres:
    networks:
      - docmind
  
  backend:
    networks:
      - docmind
  
  frontend:
    networks:
      - docmind
```

**Why It Matters:**
- Default bridge network has no isolation
- Services must use IP addresses (not DNS)
- Not suitable for multi-tenant or security-sensitive deployments

---

### PROBLEM 5: Incomplete Storage Configuration 🟠
**Severity:** HIGH  
**Impact:** Document uploads not persisted or accessible

**Current State:**
```yaml
volumes:
  postgres_data:/var/lib/postgresql/data  # Only DB data
  # Missing: uploads, logs, vectors, embeddings
```

**What's Missing:**
```yaml
volumes:
  postgres_data: {}
  uploads:       # /storage/uploads
  vectors:       # /storage/vectors (FAISS indices)
  embeddings:    # /storage/embeddings (cached)
  logs:          # /var/log/docmind
```

**Backend Storage Issue:**
```python
# backend/app/core/settings.py
upload_dir: str = Field(default="./storage/uploads", ...)
```

- `./storage/uploads` relative to backend container's working directory
- Not mounted from host, so:
  - Uploads lost when container stops
  - Cannot access files from host machine
  - Scaling to multiple containers breaks (each has own local storage)

---

### PROBLEM 6: Port Exposure Misconfiguration 🟠
**Severity:** MEDIUM  
**Impact:** Services not accessible or publicly exposed inappropriately

**Current State:**
```yaml
ports:
  - "5432:5432"  # PostgreSQL exposed to host (dev-only acceptable)
```

**Frontend Issue:**
- No port exposed (frontend cannot be accessed from host)

**Backend Issue:**
- No port exposed (backend cannot be accessed from host)

**Production Risk:**
- If ports are exposed, database accessible to any network
- If ports are NOT exposed, services not accessible from host

---

### PROBLEM 7: No Environment Variable File 🟡
**Severity:** MEDIUM  
**Impact:** Manual setup required, not reproducible

**Current State:**
- No `.env` file referenced in docker-compose.yml
- No `.env.example` in repository
- Developers must manually set each environment variable

**What Should Exist:**
```bash
# .env (git-ignored)
POSTGRES_DB=docmind
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password-here
DATABASE_URL=postgresql+psycopg2://postgres:your-secure-password-here@postgres:5432/docmind

# Backend
JWT_SECRET=your-jwt-secret-production
APP_ENV=development
OPENAI_API_KEY=your-key-here
OLLAMA_HOST=http://ollama:11434

# Frontend
VITE_API_BASE_URL=http://backend:8000
```

---

### PROBLEM 8: Missing Health Checks for Backend/Frontend 🟡
**Severity:** MEDIUM  
**Impact:** Cannot determine service readiness

**Current State:**
```yaml
postgres:
  healthcheck: [defined]

backend: [no healthcheck]
frontend: [no healthcheck]
```

**Missing:**
```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 30s  # Wait for startup

frontend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost/"]
    interval: 10s
    timeout: 5s
    retries: 5
```

---

### PROBLEM 9: No Dependency Ordering 🟡
**Severity:** MEDIUM  
**Impact:** Backend may start before PostgreSQL is ready

**Current State:**
- PostgreSQL has healthcheck, but
- No `depends_on` with `condition: service_healthy`
- No wait-for-postgres script in backend startup

**What's Missing:**
```yaml
backend:
  depends_on:
    postgres:
      condition: service_healthy  # Wait for healthcheck
```

---

### PROBLEM 10: No Ollama/LLM Service 🟡
**Severity:** MEDIUM  
**Impact:** LLM features require external setup

**Current State:**
- No Ollama service defined
- Backend config points to `http://localhost:11434` (won't work in Docker)

**What Should Be:**
```yaml
ollama:
  image: ollama/ollama:latest
  container_name: docmind-ollama
  networks:
    - docmind
  environment:
    OLLAMA_HOST: 0.0.0.0:11434
  volumes:
    - ollama_data:/root/.ollama
  ports:
    - "11434:11434"
  restart: unless-stopped
```

---

## 3. BACKEND CONFIGURATION ISSUES

### Issue 1: DATABASE_URL Default Points to localhost

**File:** `backend/app/core/settings.py`

**Current:**
```python
database_url: str = Field(
    default="postgresql+psycopg2://postgres:postgres@localhost:5432/docmind",
    validation_alias="DATABASE_URL"
)
```

**Problem:**
- Will not work in Docker Compose (localhost ≠ postgres service name)
- Backend will fail to start with connection error:
  ```
  Error: connect: Connection refused
  Is the server running on host "localhost" (127.0.0.1) and accepting
  TCP connections on port 5432?
  ```

**Required Change (not implemented):**
```python
# In docker-compose.yml or .env:
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/docmind
              ↑
              Service name in Docker network
```

---

### Issue 2: Hardcoded Credentials in Default

**File:** `backend/app/core/settings.py`

**Current:**
```python
database_url: str = Field(
    default="postgresql+psycopg2://postgres:postgres@localhost:5432/docmind",
                                      ↑      ↑
                            Credentials in code
)
```

**Problem:**
- If DATABASE_URL env var not set, credentials are in source code
- Credentials visible in git history
- Same credentials in dev/staging/production

**Required Change (not implemented):**
```python
database_url: str = Field(
    # No default - REQUIRE environment variable
    # Or use safer default:
    default="postgresql+psycopg2://${DB_USER}:${DB_PASS}@${DB_HOST}:5432/docmind",
    validation_alias="DATABASE_URL"
)
```

---

### Issue 3: Ollama Host Points to localhost

**File:** `backend/app/core/settings.py`

**Current:**
```python
ollama_host: str = Field(
    default="http://localhost:11434",
    validation_alias="OLLAMA_HOST"
)
```

**Problem:**
- Same issue as DATABASE_URL
- Will not reach ollama service from Docker container
- LLM queries will fail with connection error

**Required Change (not implemented):**
```python
# In docker-compose.yml or .env:
OLLAMA_HOST=http://ollama:11434
             ↑
             Service name in Docker network
```

---

### Issue 4: Upload Directory Is Local Path

**File:** `backend/app/core/settings.py`

**Current:**
```python
upload_dir: str = Field(
    default="./storage/uploads",
    validation_alias="UPLOAD_DIR"
)
```

**Problem:**
- Relative path `./storage/uploads`
- In Docker container, resolves relative to container working directory
- Files not accessible from host
- Volume mount not defined in docker-compose.yml
- Files lost when container stops

**Required Change (not implemented):**
```yaml
# In docker-compose.yml - define volume:
volumes:
  - ./storage/uploads:/app/storage/uploads

# In backend .env:
UPLOAD_DIR=/app/storage/uploads
```

---

### Issue 5: No Log Directory Mount

**File:** `backend/app/core/logging.py`

**Current:**
- Logging configured but no specific log file path
- Logs likely go to stdout (OK in containers)
- But if file logging added, same issue as uploads

**Future Issue:**
```python
# If logging adds file handler:
handlers:
  file_handler:
    filename: "./logs/docmind.log"  # ← Won't persist
```

---

## 4. ENVIRONMENT VARIABLE MIGRATION CHECKLIST

### Required Changes for Docker Deployment

**Database Connectivity:**
```
CURRENT (localhost):
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/docmind

REQUIRED (Docker service name):
DATABASE_URL=postgresql+psycopg2://postgres:{POSTGRES_PASSWORD}@postgres:5432/docmind
             ↑                                                        ↑
             Keep credentials from POSTGRES_PASSWORD env var    Service name
```

**Ollama/LLM Connectivity:**
```
CURRENT (localhost):
OLLAMA_HOST=http://localhost:11434

REQUIRED (Docker service name):
OLLAMA_HOST=http://ollama:11434
             ↑
             Service name in Docker network
```

**Upload Directory:**
```
CURRENT (relative path):
UPLOAD_DIR=./storage/uploads

REQUIRED (absolute path in container):
UPLOAD_DIR=/app/storage/uploads

And docker-compose.yml volume mount:
volumes:
  - ./storage/uploads:/app/storage/uploads
```

**Frontend API Base URL:**
```
CURRENT (localhost):
VITE_API_BASE_URL=http://localhost:8000

REQUIRED (Docker service name or domain):
VITE_API_BASE_URL=http://backend:8000         [dev Docker]
VITE_API_BASE_URL=http://api.example.com      [production]
```

**Database Credentials (Externalized):**
```
CURRENT (hardcoded in docker-compose.yml):
POSTGRES_PASSWORD=postgres

REQUIRED (from .env or secrets):
POSTGRES_PASSWORD={secure-password}
POSTGRES_DB=docmind
POSTGRES_USER=postgres
```

**JWT Secret (Security):**
```
CURRENT (default in code):
JWT_SECRET=change-me-in-production

REQUIRED (set in .env or secrets):
JWT_SECRET={generate-secure-random-string}
APP_ENV=production
DEBUG=false
```

---

## 5. RECOMMENDED IMPROVEMENTS

### High Priority

1. **Add Backend Service to docker-compose.yml**
   - Create Dockerfile.backend (multi-stage)
   - Build context: `./backend`
   - Expose port 8000
   - Set `depends_on: [postgres]` with healthcheck condition
   - Mount uploads volume
   - Mount logs volume

2. **Add Frontend Service to docker-compose.yml**
   - Create Dockerfile.frontend (multi-stage, Nginx)
   - Build context: `./frontend`
   - Expose port 80 (or 3000 for dev)
   - Mount env file for VITE_API_BASE_URL

3. **Externalize Credentials**
   - Create `.env.example` in root
   - Create `.env` (git-ignored) for local dev
   - Update docker-compose.yml to use env variables
   - Generate strong JWT_SECRET for production

4. **Fix DATABASE_URL Default**
   - Remove hardcoded localhost
   - Use `{POSTGRES_PASSWORD}@postgres:5432` pattern
   - Or require DATABASE_URL env variable (no default)

5. **Define Custom Network**
   ```yaml
   networks:
     docmind:
       driver: bridge
   
   services:
     postgres:
       networks:
         - docmind
   ```

### Medium Priority

6. **Add Health Checks to Backend/Frontend**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
     interval: 10s
     timeout: 5s
     retries: 5
     start_period: 30s
   ```

7. **Mount Storage Volumes**
   ```yaml
   volumes:
     postgres_data: {}
     uploads: {}
     vectors: {}
     logs: {}
   
   services:
     backend:
       volumes:
         - ./storage/uploads:/app/storage/uploads
         - ./storage/vectors:/app/storage/vectors
         - ./storage/logs:/app/logs
   ```

8. **Add Ollama Service (Optional)**
   ```yaml
   ollama:
     image: ollama/ollama:latest
     networks:
       - docmind
     volumes:
       - ollama_data:/root/.ollama
     ports:
       - "11434:11434"
   ```

9. **Add PostgreSQL Logging/Backups**
   ```yaml
   postgres:
     logging:
       driver: "json-file"
       options:
         max-size: "200k"
         max-file: "10"
   ```

10. **Add Restart Policies to All Services**
    ```yaml
    restart: unless-stopped  # Or: on-failure, no, always
    ```

---

## 6. PRODUCTION READINESS CHECKLIST

- [ ] Dockerfile.backend created and tested
- [ ] Dockerfile.frontend created and tested
- [ ] docker-compose.yml includes all services
- [ ] .env file created (git-ignored) with production secrets
- [ ] DATABASE_URL uses service name `postgres` (not localhost)
- [ ] OLLAMA_HOST uses service name `ollama` (not localhost)
- [ ] VITE_API_BASE_URL points to backend service or domain
- [ ] All storage volumes defined and mounted
- [ ] Health checks defined for all services
- [ ] depends_on with condition: service_healthy set
- [ ] Custom network defined (not default bridge)
- [ ] JWT_SECRET generated and stored securely
- [ ] POSTGRES_PASSWORD not hardcoded
- [ ] No credentials in docker-compose.yml or git
- [ ] Backend logs mounted to persistent volume
- [ ] docker-compose up --build runs without errors
- [ ] All services pass healthchecks
- [ ] Backend can connect to PostgreSQL
- [ ] Frontend can call backend API
- [ ] Document upload works end-to-end
- [ ] Production secrets in CI/CD pipeline (GitHub Actions)

---

**End of Docker Compose Analysis**

*No files were modified during this analysis*
