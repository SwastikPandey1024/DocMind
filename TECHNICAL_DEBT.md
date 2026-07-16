# Technical Debt List - DocMind AI

**Total Issues: 33 | Critical: 6 | High: 8 | Medium: 10 | Low: 9**

---

## 1. CRITICAL ISSUES (Fix Immediately - Week 1)

### TD-001: No Dockerfiles
- **Status:** 🔴 BLOCKING  
- **Location:** Root directory  
- **Effort:** 2-3 hours  
- **Impact:** CRITICAL - Cannot containerize, no production deployment possible  
- **Description:**  
  - No `Dockerfile.backend` (FastAPI service)
  - No `Dockerfile.frontend` (React app)
  - No `.dockerignore` file
  - docker-compose.yml incomplete (only PostgreSQL)
- **Root Cause:** Containerization planned but not executed
- **Solution:**
  - Create multi-stage Dockerfile for backend (Python 3.12, Alpine base)
  - Create multi-stage Dockerfile for frontend (Node 20 → nginx)
  - Create .dockerignore (exclude node_modules, __pycache__, .git, etc.)
  - Update docker-compose.yml with all services
- **Files to Create:**
  - `Dockerfile.backend`
  - `Dockerfile.frontend`
  - `.dockerignore`
  - Update `docker-compose.yml`

---

### TD-002: Multiple React Entry Points
- **Status:** 🔴 BLOCKING  
- **Location:** `frontend/src/`  
- **Effort:** 30 minutes  
- **Impact:** CRITICAL - App initialization confusion, multiple execution paths  
- **Description:**
  - `frontend/src/main.jsx` (placeholder, missing setup)
  - `frontend/src/main.tsx` (full setup with QueryClient, BrowserRouter)
  - `frontend/src/App.jsx` (placeholder, simple heading)
  - `frontend/src/app/App.tsx` (actual app with providers)
- **Root Cause:** Multiple refactors, old files not cleaned up
- **Solution:**
  - Keep `frontend/src/main.tsx` (has full provider setup)
  - Keep `frontend/src/app/App.tsx` (actual app component)
  - DELETE `frontend/src/main.jsx`
  - DELETE `frontend/src/App.jsx`
- **Files to Delete:**
  - `frontend/src/main.jsx`
  - `frontend/src/App.jsx`

---

### TD-003: Duplicate API Response Schemas
- **Status:** 🔴 BLOCKING  
- **Location:** `backend/app/`  
- **Effort:** 30 minutes  
- **Impact:** CRITICAL - DRY violation, import ambiguity  
- **Description:**
  - `backend/app/schemas/common.py` (ApiResponse, ErrorResponse)
  - `backend/app/api/v1/schemas/common.py` (identical code)
- **Root Cause:** Legacy folder structure not cleaned up
- **Solution:**
  - DELETE `backend/app/schemas/common.py`
  - KEEP `backend/app/api/v1/schemas/common.py` (versioned location)
  - Update all imports to use canonical location
- **Files to Delete:**
  - `backend/app/schemas/common.py`

---

### TD-004: Duplicate Vite Configuration
- **Status:** 🔴 BLOCKING  
- **Location:** `frontend/`  
- **Effort:** 15 minutes  
- **Impact:** CRITICAL - Build tool confusion  
- **Description:**
  - `frontend/vite.config.js` (JavaScript version)
  - `frontend/vite.config.ts` (TypeScript version, should be canonical)
- **Root Cause:** Dual config files, unclear which is used
- **Solution:**
  - VERIFY both files are identical
  - DELETE `frontend/vite.config.js`
  - KEEP `frontend/vite.config.ts` (TypeScript project should use .ts)
- **Files to Delete:**
  - `frontend/vite.config.js`

---

### TD-005: Zero Test Coverage
- **Status:** 🔴 BLOCKING  
- **Location:** `tests/`  
- **Effort:** 2-4 weeks (significant)  
- **Impact:** CRITICAL - No automated testing, high risk of regressions  
- **Description:**
  - `tests/backend/.gitkeep` only, no test files
  - `tests/e2e/.gitkeep` only, no e2e tests
  - `tests/frontend/.gitkeep` only, no component tests
  - No pytest configuration
  - No vitest configuration
- **Root Cause:** Test structure scaffolded but not implemented
- **Solution:**
  - Setup pytest for backend (conftest.py, fixtures)
  - Setup vitest for frontend
  - Write unit tests for services, repositories, utilities
  - Write integration tests for API endpoints
  - Write component tests for React components
  - Target 70%+ code coverage
- **Timeline:**
  - Week 1: Setup (4-6 hours)
  - Week 2-3: Unit tests (16-20 hours)
  - Week 3-4: Integration & component tests (16-20 hours)

---

### TD-006: Unused Architecture Layers (Clean Architecture Template Not Implemented)
- **Status:** 🔴 BLOCKING  
- **Location:** `backend/app/domain/`, `backend/app/infrastructure/`, `backend/app/interfaces/`  
- **Effort:** 4-6 hours  
- **Impact:** CRITICAL - Code bloat, developer confusion, no abstraction layers  
- **Description:**
  - `/domain/entities/` (empty, no entity abstractions)
  - `/domain/repositories/` (empty, no abstract repository interfaces)
  - `/infrastructure/database/` (empty, duplicate of /database/)
  - `/infrastructure/ocr/` (empty placeholder, OCR logic in /services/)
  - `/infrastructure/rag/` (empty placeholder, RAG logic in /services/)
  - `/interfaces/api/` (empty, no API interface definitions)
  - `/middleware/` (.gitkeep only, auth via dependencies)
  - `/utils/` (.gitkeep only, no utilities)
- **Root Cause:** Clean Architecture template created but not implemented
- **Solution:**
  - DELETE unused template directories (domain/entities, infrastructure/*, interfaces/*, middleware, utils)
  - Implement proper domain layer with abstractions
  - Implement proper application layer with use cases
  - Keep infrastructure directories only for real implementations (ocr, rag, llm, storage)
  - See recommended folder structure in ARCHITECTURE_AUDIT.md
- **Files to Delete:**
  - `backend/app/domain/entities/`
  - `backend/app/domain/repositories/` (abstract version)
  - `backend/app/infrastructure/database/` (duplicate)
  - `backend/app/interfaces/api/`
  - `backend/app/middleware/`
  - `backend/app/utils/`

---

## 2. HIGH PRIORITY ISSUES (Fix This Sprint - Week 1-2)

### TD-007: No Alembic Migrations
- **Status:** 🟠 HIGH  
- **Location:** `backend/alembic/`  
- **Effort:** 30 minutes  
- **Impact:** HIGH - Database schema not version-controlled  
- **Description:**
  - alembic.ini configured for PostgreSQL
  - No migration files in alembic/versions/
  - Initial schema only exists in ORM models
- **Root Cause:** Alembic setup incomplete
- **Solution:**
  - Run `alembic revision --autogenerate -m "Initial schema"`
  - Run `alembic upgrade head` to verify
  - Commit migration files to version control
  - Update alembic.ini to use DATABASE_URL env variable
- **Commands:**
  ```bash
  cd backend
  alembic revision --autogenerate -m "Initial schema"
  alembic upgrade head
  ```

---

### TD-008: No .dockerignore File
- **Status:** 🟠 HIGH  
- **Location:** Root directory  
- **Effort:** 15 minutes  
- **Impact:** HIGH - Docker images will be bloated  
- **Description:**
  - No .dockerignore file
  - Docker build will include venv, node_modules, .git, __pycache__, etc.
  - Resulting images 10x+ larger than necessary
- **Root Cause:** Dockerization not finalized
- **Solution:**
  - Create `.dockerignore` with common exclusions:
    ```
    .git
    .gitignore
    .dockerignore
    Dockerfile*
    docker-compose.yml
    node_modules
    dist
    build
    __pycache__
    .pytest_cache
    .venv
    venv
    *.pyc
    .env
    .env.*
    .DS_Store
    .idea
    .vscode
    .coverage
    htmlcov
    storage/uploads
    storage/logs
    storage/temp
    .agents
    .blackbox
    ```

---

### TD-009: Backend Dependencies in Two Files
- **Status:** 🟠 HIGH  
- **Location:** `backend/requirements.txt`, `backend/pyproject.toml`  
- **Effort:** 1 hour  
- **Impact:** HIGH - Maintenance burden, conflict potential  
- **Description:**
  - `requirements.txt` has full dependency list (16 packages)
  - `pyproject.toml` has different set of dependencies (missing some, has different versions)
  - Conflicting version specifications
  - Unclear which is source of truth
- **Root Cause:** Dual dependency management, transition from requirements.txt to pyproject.toml incomplete
- **Solution:**
  - Choose one source of truth (pyproject.toml is modern standard)
  - Consolidate all dependencies in pyproject.toml
  - Delete requirements.txt OR make it dynamically generated
  - Use pip-compile or poetry for lock file
  - Example updated pyproject.toml:
    ```toml
    [project]
    dependencies = [
      "fastapi>=0.115.0",
      "uvicorn[standard]>=0.30.0",
      "sqlalchemy>=2.0.35",
      "alembic>=1.13.0",
      "psycopg2-binary>=2.9.0",
      "pydantic>=2.8.0",
      "pydantic-settings>=2.0.0",
      "python-dotenv>=1.0.0",
      "python-jose[cryptography]>=3.3.0",
      "pwdlib[argon2]>=0.3.0",
      "email-validator>=2.0.0",
      "pytest>=9.0.0",
      "httpx>=0.28.0",
      "paddleocr>=2.8.0",
      "langchain>=0.3.0",
      "faiss-cpu>=1.8.0",
      "openai>=1.0.0",
    ]
    ```

---

### TD-010: Frontend State Management Missing
- **Status:** 🟠 HIGH  
- **Location:** `frontend/src/store/`  
- **Effort:** 3-4 hours  
- **Impact:** HIGH - Auth state, document state, chat state not managed  
- **Description:**
  - `/store/` only has .gitkeep
  - No Redux, Zustand, or other state management
  - Auth token/user stored locally/cookies (not managed)
  - Document list state not managed
  - Chat messages not persisted or managed
- **Root Cause:** Frontend scaffolding incomplete
- **Solution:**
  - Choose state management (Zustand recommended for simplicity)
  - Implement authStore (token, user, isAuthenticated)
  - Implement documentsStore (list, current, uploading)
  - Implement chatStore (messages, selectedDocument, loading)
  - Example Zustand store:
    ```tsx
    import create from 'zustand'
    
    interface AuthStore {
      token: string | null
      user: User | null
      isAuthenticated: boolean
      setAuth: (token: string, user: User) => void
      logout: () => void
    }
    
    export const useAuthStore = create<AuthStore>((set) => ({
      token: localStorage.getItem('token'),
      user: null,
      isAuthenticated: !!localStorage.getItem('token'),
      setAuth: (token, user) => set({ token, user, isAuthenticated: true }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),
    }))
    ```

---

### TD-011: OCR/RAG/LLM Services Not Implemented
- **Status:** 🟠 HIGH  
- **Location:** `backend/app/services/`, `backend/app/infrastructure/`  
- **Effort:** 2-3 weeks (significant)  
- **Impact:** HIGH - Core features not functional  
- **Description:**
  - `/services/ocr/.gitkeep` only (PaddleOCR not integrated)
  - `/services/rag/.gitkeep` only (LangChain/FAISS not integrated)
  - `/services/llm/.gitkeep` only (OpenAI/Ollama not integrated)
  - `/services/vectorstore/.gitkeep` only (FAISS not integrated)
  - Document upload exists, but OCR processing missing
  - No RAG pipeline (document chunking, embedding, retrieval)
  - No LLM integration for chat responses
- **Root Cause:** Core functionality scaffolded but not implemented
- **Solution:**
  - Implement OCR service (PaddleOCR adapter)
  - Implement text chunking service
  - Implement embedding service (HuggingFace)
  - Implement FAISS vector store adapter
  - Implement RAG service (retrieval + ranking)
  - Implement LLM service (OpenAI/Ollama adapter)
  - Create background tasks for async processing
  - Timeline: 2-3 weeks of development

---

### TD-012: Missing Chat Repository
- **Status:** 🟠 HIGH  
- **Location:** `backend/app/repositories/`  
- **Effort:** 2-3 hours  
- **Impact:** HIGH - Chat history queries not abstracted  
- **Description:**
  - ChatRepository interface not defined
  - ChatRepository implementation not created
  - Chat queries (list, search, delete) have no abstraction
  - Tight coupling between routes and database
- **Root Cause:** Repository pattern incomplete
- **Solution:**
  - Create `backend/app/repositories/chat.py`
  - Implement ChatRepository with methods:
    - `list_by_user(user_id, limit, offset)`
    - `get_by_id(chat_id, user_id)`
    - `get_by_document(document_id, user_id)`
    - `create(chat_data)`
    - `delete(chat_id, user_id)`
  - Update routes to use repository

---

### TD-013: Frontend Auth Context Missing
- **Status:** 🟠 HIGH  
- **Location:** `frontend/src/auth/`  
- **Effort:** 3-4 hours  
- **Impact:** HIGH - Auth token/user state not managed properly  
- **Description:**
  - No AuthContext or auth hook
  - Token storage/refresh logic not centralized
  - Login/logout/register flows not abstracted
  - Protected routes exist but no auth state provider
- **Root Cause:** Auth scaffolding incomplete
- **Solution:**
  - Create `frontend/src/auth/context.tsx` (AuthContext)
  - Create `frontend/src/auth/useAuth.ts` (useAuth hook)
  - Implement token storage (localStorage or cookies)
  - Implement token refresh logic
  - Implement logout
  - Example:
    ```tsx
    const AuthContext = createContext<AuthContextType | undefined>(undefined)
    
    export function AuthProvider({ children }) {
      const [token, setToken] = useState(localStorage.getItem('token'))
      const [user, setUser] = useState<User | null>(null)
      
      const login = async (email, password) => {
        const response = await api.post('/api/v1/auth/login', { email, password })
        setToken(response.data.access_token)
        localStorage.setItem('token', response.data.access_token)
        setUser(response.data.user)
      }
      
      // [More methods]
    }
    ```

---

### TD-014: Error Boundary Not Integrated in Routes
- **Status:** 🟠 HIGH  
- **Location:** `frontend/src/routes/`  
- **Effort:** 1-2 hours  
- **Impact:** HIGH - Page crashes not caught, poor UX  
- **Description:**
  - ErrorBoundary component exists but not used at route level
  - Individual page crashes can crash entire app
  - No error UI shown to users
- **Root Cause:** Error handling incomplete
- **Solution:**
  - Wrap route components with ErrorBoundary
  - Create error fallback UI
  - Implement error logging
  - Example:
    ```tsx
    <Route 
      path="/documents" 
      element={
        <ErrorBoundary>
          <DocumentsPage />
        </ErrorBoundary>
      } 
    />
    ```

---

## 3. MEDIUM PRIORITY ISSUES (Next Sprint - Week 2-3)

### TD-015: No Feature-Specific API Services (Frontend)
- **Status:** 🟡 MEDIUM  
- **Location:** `frontend/src/services/`  
- **Effort:** 2-3 hours  
- **Impact:** MEDIUM - API calls scattered across components  
- **Description:**
  - Only `frontend/src/services/api.ts` (base Axios config)
  - No `frontend/src/services/auth.ts` (login, register, refresh)
  - No `frontend/src/services/documents.ts` (upload, list, get, delete)
  - No `frontend/src/services/chat.ts` (send message, history)
- **Root Cause:** Frontend service layer not implemented
- **Solution:**
  - Create `frontend/src/services/auth.ts` with functions:
    - `login(email, password)`
    - `register(name, email, password)`
    - `refresh(refreshToken)`
  - Create `frontend/src/services/documents.ts` with functions:
    - `uploadDocument(file)`
    - `listDocuments()`
    - `getDocument(documentId)`
    - `deleteDocument(documentId)`
  - Create `frontend/src/services/chat.ts` with functions:
    - `sendMessage(documentId, question)`
    - `getChatHistory(documentId)`

---

### TD-016: No Custom Hooks (Frontend)
- **Status:** 🟡 MEDIUM  
- **Location:** `frontend/src/hooks/`  
- **Effort:** 2-3 hours  
- **Impact:** MEDIUM - Logic duplication, poor testability  
- **Description:**
  - No `useAuth()` hook
  - No `useAsync()` hook for data fetching
  - No `useLocalStorage()` hook
  - No `useDebounce()` hook
- **Root Cause:** Custom hook library not implemented
- **Solution:**
  - Create hooks in `frontend/src/hooks/`:
    - `useAuth()` - access auth context
    - `useAsync(asyncFunction)` - manage loading, data, error states
    - `useLocalStorage(key)` - persist/retrieve from localStorage
    - `useDebounce(value, delay)` - debounce values
    - `useFetch(url)` - wrapper around useAsync for API calls

---

### TD-017: No Form Validation Helpers (Frontend)
- **Status:** 🟡 MEDIUM  
- **Location:** `frontend/src/utils/`  
- **Effort:** 2 hours  
- **Impact:** MEDIUM - Form validation logic scattered  
- **Description:**
  - No form validation utilities
  - Each form implements validation separately
  - No centralized error messages
- **Root Cause:** Utils layer not implemented
- **Solution:**
  - Create `frontend/src/utils/validation.ts`:
    - `validateEmail(email)`
    - `validatePassword(password)`
    - `validateFormData(data, schema)`
  - Create `frontend/src/utils/formatting.ts`:
    - `formatDate(date)`
    - `formatFileSize(bytes)`
    - `formatCurrency(amount)`

---

### TD-018: Inconsistent Error Handling (Backend)
- **Status:** 🟡 MEDIUM  
- **Location:** `backend/app/`  
- **Effort:** 2-3 hours  
- **Impact:** MEDIUM - Error mapping not centralized  
- **Description:**
  - HTTPException raised directly from services
  - Error messages inconsistent
  - No custom exception classes
  - No error logging consistent
- **Root Cause:** Error handling architecture not defined
- **Solution:**
  - Create `backend/app/shared/exceptions.py`:
    ```python
    class DomainException(Exception):
        pass
    
    class DocumentNotFound(DomainException):
        pass
    
    class UnauthorizedAccess(DomainException):
        pass
    ```
  - Create error handler middleware
  - Map domain exceptions to HTTP status codes
  - Implement consistent error response format

---

### TD-019: Logger Setup But No Structured Logging (Backend)
- **Status:** 🟡 MEDIUM  
- **Location:** `backend/app/core/logging.py`, `backend/app/`  
- **Effort:** 2-3 hours  
- **Impact:** MEDIUM - Poor log searchability in production  
- **Description:**
  - Logger configured but basic
  - No structured logging (JSON format)
  - No correlation IDs for request tracing
  - Log entries use `extra={}` dict (inconsistent)
- **Root Cause:** Logging not optimized for production
- **Solution:**
  - Implement structured logging (python-json-logger)
  - Add correlation ID middleware
  - Implement context logging
  - Format logs as JSON for ELK/CloudWatch parsing

---

### TD-020: CORS Not Configured (Backend)
- **Status:** 🟡 MEDIUM  
- **Location:** `backend/app/main.py`  
- **Effort:** 30 minutes  
- **Impact:** MEDIUM - Frontend cannot call backend in production  
- **Description:**
  - No CORS middleware
  - Frontend requests will be blocked in production
  - Works in dev only due to local setup
- **Root Cause:** CORS not added to FastAPI app
- **Solution:**
  - Add CORSMiddleware to main.py:
    ```python
    from fastapi.middleware.cors import CORSMiddleware
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[os.getenv("CORS_ORIGINS", "http://localhost:5173")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```

---

### TD-021: No Request/Response Interceptor (Frontend Axios)
- **Status:** 🟡 MEDIUM  
- **Location:** `frontend/src/services/api.ts`  
- **Effort:** 1-2 hours  
- **Impact:** MEDIUM - Token refresh, error handling not automated  
- **Description:**
  - Basic Axios instance, no interceptors
  - Token not automatically added to requests
  - 401 responses not handled (no token refresh)
  - Errors not uniformly handled
- **Root Cause:** API client not production-ready
- **Solution:**
  - Add request interceptor (add auth token)
  - Add response interceptor (handle 401, retry with refresh)
  - Implement centralized error handling
  - Example:
    ```ts
    api.interceptors.request.use((config) => {
      const token = localStorage.getItem('token')
      if (token) config.headers.Authorization = `Bearer ${token}`
      return config
    })
    
    api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Refresh token and retry
        }
        return Promise.reject(error)
      }
    )
    ```

---

### TD-022: TypeScript Strict Mode Not Enforced (Frontend)
- **Status:** 🟡 MEDIUM  
- **Location:** `frontend/tsconfig.json`  
- **Effort:** 30 minutes  
- **Impact:** MEDIUM - Type safety not maximized  
- **Description:**
  - `strict: true` is enabled
  - But some files have implicit `any` types
  - Not all files are .tsx (some .jsx exist)
- **Root Cause:** TypeScript config incomplete
- **Solution:**
  - Ensure `strict: true` is set
  - Add `noImplicitAny: true`
  - Add `noImplicitThis: true`
  - Add `noUnusedLocals: true`
  - Add `noUnusedParameters: true`
  - Add `noFallthroughCasesInSwitch: true`

---

### TD-023: Missing Environment Variable Validation (Frontend)
- **Status:** 🟡 MEDIUM  
- **Location:** `frontend/src/`  
- **Effort:** 1-2 hours  
- **Impact:** MEDIUM - Misconfiguration not caught  
- **Description:**
  - `VITE_API_BASE_URL` has fallback but no validation
  - Missing error if env var is invalid URL
  - No validation on build time
- **Root Cause:** Env var handling not validated
- **Solution:**
  - Create `frontend/src/config.ts`:
    ```ts
    export const config = {
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      isDev: import.meta.env.DEV,
      isProd: import.meta.env.PROD,
    }
    
    // Validate on app startup
    if (!config.apiBaseUrl) {
      throw new Error('VITE_API_BASE_URL is required')
    }
    ```

---

### TD-024: Authentication Routes Lack Rate Limiting (Backend)
- **Status:** 🟡 MEDIUM  
- **Location:** `backend/app/api/v1/routes/auth.py`  
- **Effort:** 1-2 hours  
- **Impact:** MEDIUM - Brute force vulnerability  
- **Description:**
  - Auth endpoints have placeholder comment about rate limiting
  - No actual rate limiting implemented
  - No brute force protection
- **Root Cause:** Rate limiting not implemented
- **Solution:**
  - Use slowapi or fastapi-limiter library
  - Apply to /register, /login, /refresh endpoints
  - Example:
    ```python
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    
    limiter = Limiter(key_func=get_remote_address)
    
    @router.post("/login")
    @limiter.limit("5/minute")
    def login(...): ...
    ```

---

### TD-025: No API Versioning Strategy Documented (Backend)
- **Status:** 🟡 MEDIUM  
- **Location:** `backend/app/api/`  
- **Effort:** 30 minutes  
- **Impact:** MEDIUM - Future /v2 migration unclear  
- **Description:**
  - Only `/api/v1/` exists currently
  - No documentation on how to add v2
  - No deprecation strategy for v1
- **Root Cause:** API versioning strategy not documented
- **Solution:**
  - Document API versioning approach (URL path, headers, etc.)
  - Create ARCHITECTURE.md section on API evolution
  - Document deprecation timeline
  - Plan for v2 migration when needed

---

## 4. LOW PRIORITY ISSUES (Nice to Have - Week 4+)

### TD-026: Re-export Layers Add Indirection
- **Status:** 🔵 LOW  
- **Location:** `backend/app/core/config.py`, `backend/app/models/base.py`  
- **Effort:** 1-2 hours  
- **Impact:** LOW - Namespace clarity vs. boilerplate trade-off  
- **Description:**
  - `/core/config.py` re-exports from `/core/settings.py`
  - `/models/base.py` re-exports from `/database/base.py`
- **Root Cause:** Re-export pattern (common but creates indirection)
- **Solution (Optional):**
  - Keep if namespace organization is desired
  - Or remove and update all imports to source files
  - No functional impact, purely organizational

---

### TD-027: No API Documentation (Swagger/OpenAPI Tags)
- **Status:** 🔵 LOW  
- **Location:** `backend/app/`  
- **Effort:** 1-2 hours  
- **Impact:** LOW - API discoverability (FastAPI auto-docs exist but need tagging)  
- **Description:**
  - FastAPI auto-generates Swagger UI
  - But endpoint tags and descriptions could be better
  - Swagger UI exists at /docs but not customized
- **Root Cause:** API documentation not enhanced
- **Solution (Optional):**
  - Add response examples to schemas
  - Add detailed descriptions to endpoints
  - Customize Swagger UI theme
  - Reference: http://localhost:8000/docs

---

### TD-028: Missing .env.example Files
- **Status:** 🔵 LOW  
- **Location:** Root, `backend/`, `frontend/`  
- **Effort:** 30 minutes  
- **Impact:** LOW - Developer onboarding friction  
- **Description:**
  - No `.env.example` for local development
  - Developers don't know what env vars are required
- **Root Cause:** Environment setup documentation incomplete
- **Solution:**
  - Create `.env.example` in root:
    ```
    # Backend
    DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/docmind
    JWT_SECRET=change-me-in-production
    OPENAI_API_KEY=your-key-here
    OLLAMA_HOST=http://localhost:11434
    
    # Frontend
    VITE_API_BASE_URL=http://localhost:8000
    ```
  - Create similar files in backend/ and frontend/

---

### TD-029: No Linting/Formatting Setup (Backend)
- **Status:** 🔵 LOW  
- **Location:** `backend/`  
- **Effort:** 1-2 hours  
- **Impact:** LOW - Code style inconsistency  
- **Description:**
  - No ruff, black, or flake8 configured
  - No formatting rules enforced
- **Root Cause:** Code quality tools not setup
- **Solution (Optional):**
  - Add ruff for linting
  - Add black for formatting
  - Add pyproject.toml configuration
  - Add pre-commit hook

---

### TD-030: No Pre-commit Hooks
- **Status:** 🔵 LOW  
- **Location:** Root (`.pre-commit-config.yaml`)  
- **Effort:** 1-2 hours  
- **Impact:** LOW - Prevents bad commits early  
- **Description:**
  - No pre-commit hooks
  - Bad code can be committed
- **Root Cause:** CI enforcement not in place
- **Solution (Optional):**
  - Create `.pre-commit-config.yaml`:
    ```yaml
    repos:
      - repo: https://github.com/psf/black
        rev: 23.1.0
        hooks:
          - id: black
      - repo: https://github.com/astral-sh/ruff-pre-commit
        rev: v0.1.0
        hooks:
          - id: ruff
      - repo: https://github.com/pre-commit/pre-commit-hooks
        rev: v4.4.0
        hooks:
          - id: trailing-whitespace
          - id: end-of-file-fixer
    ```

---

### TD-031: No GitHub Actions Workflows
- **Status:** 🔵 LOW  
- **Location:** `.github/workflows/`  
- **Effort:** 2-3 hours  
- **Impact:** LOW - No CI/CD pipeline  
- **Description:**
  - `.github/workflows/` directory exists but empty
  - No automated testing on pull requests
  - No automated deployment
- **Root Cause:** CI/CD not configured
- **Solution (Optional):**
  - Create `test.yml` (runs pytest + vitest on PR)
  - Create `lint.yml` (runs ruff, black, eslint on PR)
  - Create `deploy.yml` (builds and deploys on merge to main)

---

### TD-032: Missing Docker Health Checks (for Frontend)
- **Status:** 🔵 LOW  
- **Location:** `docker-compose.yml`  
- **Effort:** 30 minutes  
- **Impact:** LOW - Missing container readiness detection  
- **Description:**
  - PostgreSQL has healthcheck
  - Frontend/Backend don't have healthchecks
- **Root Cause:** Incomplete docker-compose configuration
- **Solution (Optional):**
  - Add healthcheck to backend:
    ```yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    ```
  - Add healthcheck to frontend:
    ```yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    ```

---

### TD-033: TypeScript Path Aliases Not Optimized
- **Status:** 🔵 LOW  
- **Location:** `frontend/tsconfig.json`  
- **Effort:** 30 minutes  
- **Impact:** LOW - Minor DX improvement  
- **Description:**
  - Basic `@/*` alias exists
  - Could add more specific aliases for better organization
- **Root Cause:** Path aliases minimally configured
- **Solution (Optional):**
  - Expand tsconfig.json paths:
    ```json
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@pages/*": ["./src/pages/*"],
      "@services/*": ["./src/services/*"],
      "@hooks/*": ["./src/hooks/*"],
      "@types/*": ["./src/types/*"],
    }
    ```

---

## 5. ISSUE MATRIX: Severity vs. Effort

```
EFFORT
  ↑
  │  TD-011 (2-3w)   TD-005 (2-4w)
  │  ●                ●
  │
  │        TD-012     TD-013    TD-009
  │        ●          ●         ●
  │        TD-014     TD-018
  │        ●          ●
  │
  │  TD-007  TD-008  TD-001  TD-002  TD-003  TD-004
  │  ●       ●       ●       ●       ●       ●
  └─────────────────────────────────────────────► SEVERITY
    LOW    MEDIUM    HIGH   CRITICAL
```

---

## 6. PRIORITY ROADMAP

### Week 1: Foundation (Critical Issues)
- [ ] **TD-001:** Create Dockerfiles (2-3h)
- [ ] **TD-002:** Fix React entry points (30m)
- [ ] **TD-003:** Fix API schema duplication (30m)
- [ ] **TD-004:** Fix Vite config (15m)
- [ ] **TD-006:** Remove unused dirs (15m)
- [ ] **TD-007:** Create initial Alembic migration (30m)
- [ ] **TD-008:** Create .dockerignore (15m)
- **Total:** ~6-7 hours

### Week 2: High Priority
- [ ] **TD-009:** Consolidate dependencies (1h)
- [ ] **TD-010:** Implement state management (3-4h)
- [ ] **TD-011:** Implement OCR/RAG/LLM (plan & start, 2-3w ongoing)
- [ ] **TD-012:** Create Chat repository (2-3h)
- [ ] **TD-013:** Implement Auth context (3-4h)
- [ ] **TD-014:** Add error boundary to routes (1-2h)
- **Total:** ~13-16 hours

### Week 3: Medium Priority
- [ ] **TD-015:** Feature-specific API services (2-3h)
- [ ] **TD-016:** Custom hooks (2-3h)
- [ ] **TD-017:** Form validation helpers (2h)
- [ ] **TD-018:** Consistent error handling (2-3h)
- [ ] **TD-019:** Structured logging (2-3h)
- [ ] **TD-020:** CORS configuration (30m)
- [ ] **TD-021:** Request/response interceptors (1-2h)
- [ ] **TD-022:** TypeScript strict mode (30m)
- [ ] **TD-023:** Env var validation (1-2h)
- [ ] **TD-024:** Rate limiting (1-2h)
- **Total:** ~16-20 hours

### Week 4+: Low Priority & Testing
- [ ] **TD-005:** Comprehensive testing (2-4 weeks)
- [ ] **TD-026 - TD-033:** Optional improvements (6-10h)
- **Total:** 2-4 weeks ongoing

---

## 7. EFFORT SUMMARY

| Priority | Count | Total Hours | Timeline |
|----------|-------|---|---|
| Critical | 6 | 6-7 | 1 day |
| High | 8 | 13-16 | 3 days |
| Medium | 10 | 16-20 | 3-4 days |
| Low | 9 | 6-10 | 1-2 days |
| **TOTAL (excluding testing)** | **33** | **41-53** | **1-2 weeks** |
| **TOTAL (with testing)** | **34** | **87-141** | **2-4 weeks** |

---

**End of Technical Debt List**

*No code was modified during this analysis*
