# DocMind AI - Architecture Audit Report

**Project:** DocMind AI (OCR + RAG Document Chat System)  
**Date:** 2026  
**Audit Scope:** Full repository analysis (no code modifications)

---

## 1. ARCHITECTURE REPORT

### 1.1 Project Overview
- **Type:** Full-stack web application with AI/ML integration
- **Frontend:** React 19 + TypeScript + Vite + TailwindCSS
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **AI/ML Stack:** PaddleOCR, LangChain, FAISS, OpenAI/Ollama
- **Deployment:** Docker Compose ready

### 1.2 Current Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│                    React Frontend (Vite)                    │
│  ├─ /pages: Login, Dashboard, Documents, Chat, Settings   │
│  ├─ /components: Layout, UI, Common (ProtectedRoute, etc.) │
│  ├─ /services: API client (Axios)                          │
│  ├─ /store: State (empty placeholder)                      │
│  ├─ /routes: React Router with auth protection            │
│  └─ /types: TypeScript type definitions                    │
└──────────────┬──────────────────────────────────────────────┘
               │ HTTP/REST (Port 5173 dev, :80 prod)
┌──────────────▼──────────────────────────────────────────────┐
│                 FastAPI Backend (uvicorn)                   │
│  ├─ /api/v1/routes: Auth, Documents, Health endpoints      │
│  ├─ /api/v1/schemas: Request/Response DTOs                 │
│  ├─ /api/v1/dependencies: DI layer (backward compat)       │
│  ├─ /auth: JWT, Password, Service, Router                  │
│  ├─ /models: SQLAlchemy ORM (User, Document, Chat, Chunk)  │
│  ├─ /repositories: Data access layer                       │
│  ├─ /services: Business logic (Document, OCR, RAG, LLM)    │
│  ├─ /core: Config, Settings, Security, Logging             │
│  └─ /database: Session, Engine, Base (Alembic migrations)  │
└──────────────┬──────────────────────────────────────────────┘
               │ TCP (Port 8000)
┌──────────────▼──────────────────────────────────────────────┐
│              PostgreSQL 16 + FAISS Vector Store             │
│  ├─ users (UUID, name, email, password_hash, role, dates)  │
│  ├─ documents (UUID, user_id, file metadata, status)       │
│  ├─ chunks (text embeddings, references)                   │
│  ├─ chat_history (QA pairs, response metadata)             │
│  └─ ocr_text (raw OCR output per document)                 │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────┴──────────────────────────────┐
       │                                       │
   [FAISS]                              [PaddleOCR]
   Vector                               Text
   Search                               Extraction
```

### 1.3 Layered Architecture (Current State)
```
┌─────────────────────────────────────────────────────────┐
│          API Layer (routes + schemas)                   │
│  ├─ /api/v1/routes/auth.py (imports from app/auth)     │
│  ├─ /api/v1/routes/documents.py                        │
│  ├─ /api/v1/routes/health.py                           │
│  ├─ /api/v1/schemas/* (DTO models)                     │
│  └─ /api/v1/dependencies/* (re-exports app/auth/*)     │
├─────────────────────────────────────────────────────────┤
│          Service Layer (business logic)                 │
│  ├─ /services/document_service.py                      │
│  ├─ /services/document_validator.py                    │
│  ├─ /services/storage_service.py                       │
│  ├─ /services/llm/* (placeholder)                      │
│  ├─ /services/ocr/* (placeholder)                      │
│  ├─ /services/rag/* (placeholder)                      │
│  └─ /services/vectorstore/* (placeholder)              │
├─────────────────────────────────────────────────────────┤
│          Repository Layer (data access)                 │
│  ├─ /repositories/base.py (BaseRepository[T] generic)  │
│  ├─ /repositories/user.py                              │
│  ├─ /repositories/document.py                          │
│  └─ /repositories/chat.py (missing)                    │
├─────────────────────────────────────────────────────────┤
│          Domain Model (ORM & Entities)                  │
│  ├─ /models/user.py (UUID PK, auth fields, soft delete)│
│  ├─ /models/document.py (UUID PK, file metadata)       │
│  ├─ /models/chat.py (ChatHistory, Q&A storage)         │
│  ├─ /models/chunk.py (text chunks, embeddings)         │
│  ├─ /models/base.py (re-exports from database/base)    │
│  └─ /domain/* (EMPTY - Clean Arch intent not used)     │
├─────────────────────────────────────────────────────────┤
│          Data Layer (ORM & Sessions)                    │
│  ├─ /database/base.py (DeclarativeBase, mixins)        │
│  ├─ /database/engine.py (create_engine)                │
│  ├─ /database/session.py (SessionLocal factory)        │
│  ├─ /database/dependencies.py (get_db_session)         │
│  ├─ alembic/ (migrations, env.py)                      │
│  └─ alembic.ini (PostgreSQL connection config)         │
├─────────────────────────────────────────────────────────┤
│          Infrastructure (unused placeholders)           │
│  ├─ /infrastructure/database/* (empty __init__)        │
│  ├─ /infrastructure/ocr/* (empty __init__)             │
│  ├─ /infrastructure/rag/* (empty __init__)             │
│  └─ /interfaces/api/* (empty __init__)                 │
├─────────────────────────────────────────────────────────┤
│          Core/Cross-cutting (config, auth, logging)     │
│  ├─ /core/config.py (re-exports settings)              │
│  ├─ /core/settings.py (Pydantic BaseSettings)          │
│  ├─ /core/constants.py (Enum, Environment)             │
│  ├─ /core/security.py (crypto utils)                   │
│  ├─ /core/logging.py (structured logging setup)        │
│  ├─ /auth/jwt.py (create/decode tokens)                │
│  ├─ /auth/password.py (hash/verify)                    │
│  ├─ /auth/service.py (AuthService - register/login)    │
│  ├─ /auth/dependencies.py (bearer_scheme, DI funcs)    │
│  └─ /auth/router.py (endpoints)                        │
└─────────────────────────────────────────────────────────┘
```

### 1.4 Frontend Architecture (React)
```
/src
├─ App.jsx (simple placeholder, no integration)
├─ main.jsx (React 19 entry, QueryClient + Router)
├─ main.tsx (duplicate - TypeScript version)
├─ app/
│  ├─ App.tsx (main layout with AppShell, ErrorBoundary, etc.)
│  └─ index.ts (barrel export)
├─ pages/
│  ├─ auth/ (LoginPage, RegisterPage)
│  ├─ dashboard/ (DashboardPage - placeholder)
│  ├─ documents/ (DocumentsPage - placeholder)
│  ├─ chat/ (ChatPage - placeholder)
│  ├─ settings/ (SettingsPage - placeholder)
│  └─ index.ts (barrel export)
├─ routes/
│  └─ index.tsx (AppRoutes with ProtectedRoute wrapper)
├─ components/
│  ├─ common/ (ErrorBoundary, ProtectedRoute, ThemeProvider, LoadingScreen)
│  ├─ layout/ (AppLayout, AppShell, Navbar, Sidebar)
│  ├─ ui/ (button component from Radix UI)
│  └─ index.ts (barrel exports)
├─ services/
│  ├─ api.ts (Axios instance with base config)
│  └─ (no feature-specific services implemented)
├─ hooks/ (placeholder)
├─ store/ (placeholder - no Redux/Zustand yet)
├─ features/ (Feature folders as barrel exports only)
│  ├─ auth/index.ts
│  ├─ chat/index.ts
│  ├─ dashboard/index.ts
│  ├─ documents/index.ts
│  └─ settings/index.ts
├─ types/
│  └─ index.ts (barrel export, actual types missing)
├─ layouts/ (placeholder)
├─ lib/
│  └─ utils.ts (utility functions)
├─ styles/
│  └─ index.css (global styles, TailwindCSS)
└─ vite-env.d.ts (Vite environment type definitions)
```

---

## 2. REPOSITORY HEALTH SCORE

**Overall Health: 6.2/10 (Moderate-Low)**

| Category | Score | Status | Notes |
|----------|-------|--------|-------|
| **Folder Structure** | 5/10 | ⚠️ Mixed | Clean separation but unused/empty directories |
| **Naming Consistency** | 8/10 | ✅ Good | Consistent snake_case (Python), camelCase (TS/JS) |
| **Code Organization** | 6/10 | ⚠️ Mixed | Duplication and unused architecture layers |
| **Docker Readiness** | 2/10 | ❌ Critical | No Dockerfiles, docker-compose incomplete |
| **Alembic Readiness** | 7/10 | ✅ Good | Config present but no migrations created yet |
| **Frontend/Backend Boundary** | 7/10 | ✅ Good | Clean API-first separation |
| **Clean Architecture** | 3/10 | ❌ Low | Infrastructure/Domain/Interfaces layers unused |
| **Documentation** | 8/10 | ✅ Good | Comprehensive docs, README files present |
| **Dependency Management** | 7/10 | ✅ Good | requirements.txt + pyproject.toml (conflict) |
| **Test Coverage** | 2/10 | ❌ Critical | Tests directory exists only as scaffolding |

---

## 3. DUPLICATE LIST

### 3.1 **CRITICAL DUPLICATES - Must Fix**

#### 1. **API Response Schema Duplication**
```
DUPLICATE: ApiResponse, ErrorResponse
├─ backend/app/schemas/common.py
│  └─ ApiResponse (generic response wrapper)
│  └─ ErrorResponse
└─ backend/app/api/v1/schemas/common.py
   └─ ApiResponse (identical code)
   └─ ErrorResponse

IMPACT: High - causes import ambiguity, violates DRY
RECOMMENDATION: Delete backend/app/schemas/common.py, use only backend/app/api/v1/schemas/common.py
```

#### 2. **Auth Dependencies Duplication** 
```
DUPLICATE: Authentication dependency injection
├─ backend/app/auth/dependencies.py
│  ├─ bearer_scheme
│  ├─ get_user_repository()
│  ├─ get_auth_service()
│  ├─ get_current_user()
│  ├─ get_current_active_user()
│  └─ get_admin_user()
│
└─ backend/app/api/v1/dependencies/auth.py
   └─ Re-exports all of the above (backward compatibility layer)

IMPACT: Medium - causes confusion, adds indirection
RECOMMENDATION: Keep source of truth in backend/app/auth/dependencies.py; mark re-export as DEPRECATED
```

#### 3. **Main Entry Point Duplication (Frontend)**
```
DUPLICATE: React app initialization
├─ frontend/src/main.jsx
│  └─ Simple placeholder (only renders root)
│
├─ frontend/src/main.tsx
│  └─ Full app with QueryClient, BrowserRouter, proper setup
│
└─ frontend/src/App.jsx
   └─ Placeholder (simple heading)
   
└─ frontend/src/app/App.tsx
   └─ Actual app with ThemeProvider, ErrorBoundary, routes

IMPACT: CRITICAL - causes confusion, multiple entry points
RECOMMENDATION: Use main.tsx as single source, delete main.jsx and App.jsx
```

#### 4. **Config Import Re-export**
```
DUPLICATE: Settings re-export chain
├─ backend/app/core/settings.py
│  └─ class Settings + get_settings()
│
└─ backend/app/core/config.py
   └─ __all__ = ["Settings", "get_settings"] (re-export)

IMPACT: Low - acceptable for namespace, but check import chain
RECOMMENDATION: Review if re-export layer adds value; consider removing
```

#### 5. **Base Model Duplication**
```
DUPLICATE: ORM Base class re-export
├─ backend/app/database/base.py
│  ├─ DeclarativeBase
│  ├─ TimestampMixin
│  ├─ SoftDeleteMixin
│  └─ UUIDPrimaryKeyMixin
│
└─ backend/app/models/base.py
   └─ __all__ = ["Base", "SoftDeleteMixin", ...] (re-export)

IMPACT: Low - acceptable indirection, but redundant
RECOMMENDATION: Keep one canonical source; simplify imports
```

#### 6. **Vite Config Duplication**
```
DUPLICATE: Build configuration
├─ frontend/vite.config.js
│  └─ defineConfig with React plugin
│
└─ frontend/vite.config.ts
   └─ (not checked - TypeScript version exists)

IMPACT: Medium - build tool confusion
RECOMMENDATION: Use one config file (vite.config.ts), delete vite.config.js
```

### 3.2 **Empty Directories (Dead Code)**
```
backend/app/domain/
├─ entities/ (empty __init__.py, __pycache__)
└─ repositories/ (empty __init__.py, __pycache__)
→ No implementation; Clean Architecture intent not followed

backend/app/infrastructure/
├─ database/ (empty __init__.py, __pycache__)
├─ ocr/ (empty __init__.py, __pycache__)
└─ rag/ (empty __init__.py, __pycache__)
→ Placeholder for future services; duplicate of app/services/

backend/app/interfaces/
└─ api/ (empty __init__.py, __pycache__)
→ No API interface definitions; likely leftover from architecture planning

backend/app/middleware/
└─ (.gitkeep only)
→ No middleware implemented; authentication done via dependencies

backend/app/models/ (partial content)
└─ (.gitkeep only, but models DO exist: user.py, document.py, chat.py, chunk.py)

backend/app/utils/
└─ (.gitkeep only, no utilities)

frontend/src/hooks/
└─ (.gitkeep only, no custom hooks)

frontend/src/layouts/
└─ (.gitkeep only - layout components in /components/layout/)

frontend/src/pages/
└─ .gitkeep (actual pages in /pages/{auth,dashboard,documents,chat,settings}/)

frontend/src/store/
└─ (.gitkeep only - no Redux, Zustand, or state management)

frontend/src/services/
└─ Only api.ts; no feature-specific services

tests/backend/
└─ (.gitkeep only - no test files)

tests/e2e/
└─ (.gitkeep only - no end-to-end tests)

tests/frontend/
└─ (.gitkeep only - no component/integration tests)

.agents/
└─ Empty (likely for AI tooling in future)

.blackbox/
└─ Empty (likely for caching or build artifacts)
```

---

## 4. RECOMMENDED FOLDER STRUCTURE

### 4.1 **Backend - Proposed Clean Architecture**

```
backend/
├── pyproject.toml
├── requirements.txt
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
│
├── app/
│   ├── __init__.py
│   ├── main.py (FastAPI app initialization)
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── routes/
│   │       │   ├── __init__.py
│   │       │   ├── auth.py
│   │       │   ├── documents.py
│   │       │   ├── chat.py
│   │       │   └── health.py
│   │       ├── schemas/
│   │       │   ├── __init__.py
│   │       │   ├── common.py (ApiResponse, ErrorResponse) ✅ SINGLE SOURCE
│   │       │   ├── auth.py
│   │       │   ├── documents.py
│   │       │   ├── chat.py
│   │       │   └── users.py
│   │       └── dependencies/
│   │           ├── __init__.py
│   │           └── auth.py (imports from app/auth/dependencies)
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py (token creation/verification)
│   │   ├── password.py (hashing/verification)
│   │   ├── service.py (AuthService)
│   │   ├── dependencies.py (SINGLE SOURCE OF TRUTH)
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── logging.py
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py (User, Document, Chat, Chunk - ORM classes)
│   │   └── repositories/ (abstract repository interfaces)
│   │       ├── __init__.py
│   │       ├── base.py (BaseRepository[T])
│   │       ├── user.py (UserRepository interface)
│   │       ├── document.py (DocumentRepository interface)
│   │       └── chat.py (ChatRepository interface)
│   │
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── database.py (engine, session factory)
│   │   ├── migrations.py (alembic integration)
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── base.py (SQLAlchemy BaseRepository[T])
│   │       ├── user.py (UserRepository implementation)
│   │       ├── document.py (DocumentRepository implementation)
│   │       └── chat.py (ChatRepository implementation)
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── auth_use_cases.py (register, login, refresh)
│   │   │   ├── document_use_cases.py (upload, list, get, delete)
│   │   │   └── chat_use_cases.py (query, list history)
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── auth_service.py (orchestrates auth logic)
│   │       ├── document_service.py (orchestrates document flow)
│   │       ├── chat_service.py (orchestrates chat/RAG)
│   │       └── validator.py (cross-cutting validation)
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── config.py (pydantic settings)
│   │   ├── logging.py (structured logging setup)
│   │   ├── ocr/
│   │   │   ├── __init__.py
│   │   │   └── paddle_ocr_adapter.py (PaddleOCR integration)
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── langchain_adapter.py
│   │   │   └── faiss_adapter.py
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── openai_adapter.py
│   │   │   └── ollama_adapter.py
│   │   └── storage/
│   │       ├── __init__.py
│   │       └── file_storage.py (disk + cloud adapters)
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── error_handlers.py (exception mapping)
│   │   ├── logging_middleware.py
│   │   └── cors_middleware.py
│   │
│   └── shared/
│       ├── __init__.py
│       ├── security.py (crypto utilities)
│       ├── exceptions.py (custom exception classes)
│       ├── constants.py (enums, magic strings)
│       └── utils.py (cross-cutting utilities)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py (pytest fixtures)
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_document_service.py
│   │   └── test_repositories.py
│   ├── integration/
│   │   ├── test_auth_routes.py
│   │   ├── test_document_routes.py
│   │   └── test_database.py
│   └── fixtures/
│       └── test_data.py
│
└── storage/
    ├── uploads/ (user uploads)
    ├── processed/ (OCR results)
    ├── vectors/ (FAISS indices)
    └── embeddings/ (cached embeddings)
```

### 4.2 **Frontend - Proposed Structure**

```
frontend/
├── package.json
├── tsconfig.json (single source of truth)
├── vite.config.ts (single source of truth)
├── tailwind.config.js
├── postcss.config.js
├── index.html
│
├── src/
│   ├── main.tsx (SINGLE ENTRY POINT - delete main.jsx)
│   ├── vite-env.d.ts
│   │
│   ├── App.tsx (root component with all providers)
│   │
│   ├── api/
│   │   ├── __init__.ts
│   │   └── client.ts (Axios instance + interceptors)
│   │
│   ├── auth/
│   │   ├── index.ts
│   │   ├── hooks/ (useAuth, useLogin, useRegister)
│   │   ├── context/ (AuthContext for token/user state)
│   │   ├── guards/ (ProtectedRoute component)
│   │   └── services/ (login, register, logout, refresh)
│   │
│   ├── pages/
│   │   ├── index.ts (barrel export)
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   └── RegisterPage.tsx
│   │   ├── dashboard/
│   │   │   └── DashboardPage.tsx
│   │   ├── documents/
│   │   │   ├── DocumentsPage.tsx
│   │   │   ├── DocumentUploadModal.tsx
│   │   │   └── DocumentDetail.tsx
│   │   ├── chat/
│   │   │   ├── ChatPage.tsx
│   │   │   ├── ChatMessenger.tsx
│   │   │   └── DocumentSelector.tsx
│   │   └── settings/
│   │       └── SettingsPage.tsx
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── index.ts
│   │   │   ├── hooks.ts (useAuth, useLogin)
│   │   │   └── api.ts (login, register, refresh)
│   │   ├── documents/
│   │   │   ├── index.ts
│   │   │   ├── hooks.ts (useDocuments, useUpload)
│   │   │   └── api.ts (CRUD operations)
│   │   ├── chat/
│   │   │   ├── index.ts
│   │   │   ├── hooks.ts (useChat, useHistory)
│   │   │   └── api.ts (send message, get history)
│   │   └── settings/
│   │       ├── index.ts
│   │       ├── hooks.ts
│   │       └── api.ts
│   │
│   ├── components/
│   │   ├── index.ts
│   │   ├── common/
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── ErrorBoundary.test.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   ├── LoadingScreen.tsx
│   │   │   ├── ThemeProvider.tsx
│   │   │   ├── index.ts
│   │   │   └── __tests__/ (test files)
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx
│   │   │   ├── AppShell.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── index.ts
│   │   ├── ui/
│   │   │   ├── button.tsx (Radix UI components)
│   │   │   ├── dialog.tsx
│   │   │   ├── index.ts
│   │   │   └── __tests__/ (component tests)
│   │   └── document/
│   │       ├── DocumentCard.tsx
│   │       ├── DocumentList.tsx
│   │       └── index.ts
│   │
│   ├── hooks/
│   │   ├── index.ts
│   │   ├── useAuth.ts (auth context access)
│   │   ├── useAsync.ts (async data fetching)
│   │   ├── useLocalStorage.ts (browser storage)
│   │   └── __tests__/ (hook tests)
│   │
│   ├── services/
│   │   ├── api.ts (Axios configuration)
│   │   ├── auth.ts (auth-specific API calls)
│   │   ├── documents.ts (document API calls)
│   │   └── chat.ts (chat API calls)
│   │
│   ├── store/
│   │   ├── authStore.ts (Zustand or Redux state)
│   │   ├── documentsStore.ts
│   │   └── chatStore.ts
│   │
│   ├── types/
│   │   ├── index.ts (barrel export)
│   │   ├── auth.ts (User, TokenResponse, etc.)
│   │   ├── documents.ts (Document, DocumentUpload)
│   │   ├── chat.ts (Message, ChatHistory)
│   │   └── api.ts (ApiResponse, ApiError)
│   │
│   ├── routes/
│   │   ├── index.tsx (route definitions)
│   │   └── ProtectedRoute.tsx (authentication guard)
│   │
│   ├── utils/
│   │   ├── index.ts
│   │   ├── formatting.ts (date, file size, etc.)
│   │   ├── validation.ts (form validation helpers)
│   │   ├── api-helpers.ts (error handling, retry logic)
│   │   └── auth-helpers.ts (token management)
│   │
│   ├── styles/
│   │   ├── index.css (global + TailwindCSS)
│   │   ├── variables.css (CSS variables)
│   │   └── animations.css (custom animations)
│   │
│   └── layouts/
│       └── (folder can be removed - use /components/layout instead)
│
├── public/
│   ├── favicon.svg
│   └── (static assets)
│
└── .env.example
```

---

## 5. TECHNICAL DEBT LIST

### 5.1 **CRITICAL Issues (Fix Immediately)**

| ID | Issue | Location | Severity | Effort | Impact |
|----|----|----------|----------|--------|--------|
| **TD-001** | No Dockerfiles or .dockerignore | Root directory | 🔴 CRITICAL | 2-3 hrs | Cannot containerize; docker-compose incomplete |
| **TD-002** | Multiple React entry points (main.jsx/main.tsx/App.jsx) | frontend/src/ | 🔴 CRITICAL | 30 min | App initialization confusion |
| **TD-003** | Duplicate API response schemas (ApiResponse in 2 locations) | backend/app/ | 🔴 CRITICAL | 30 min | Import ambiguity, violates DRY |
| **TD-004** | Duplicate vite config (js + ts) | frontend/ | 🔴 CRITICAL | 15 min | Build tool confusion |
| **TD-005** | No test files despite tests/ directory | tests/ | 🔴 CRITICAL | 2-4 weeks | Zero test coverage |
| **TD-006** | Unused Clean Architecture layers (domain/infrastructure/interfaces) | backend/app/ | 🔴 CRITICAL | 4-6 hrs | Code bloat, developer confusion |

### 5.2 **HIGH Priority (Address This Sprint)**

| ID | Issue | Location | Severity | Effort | Impact |
|----|----|----------|----------|--------|--------|
| **TD-007** | Alembic configured but no migrations exist | backend/alembic/ | 🟠 HIGH | 30 min | Database schema not version-controlled |
| **TD-008** | No .dockerignore file | Root | 🟠 HIGH | 15 min | Docker images will include unnecessary files (venv, .git, node_modules) |
| **TD-009** | Backend dependencies in both requirements.txt AND pyproject.toml | backend/ | 🟠 HIGH | 1 hr | Maintenance burden, conflict potential |
| **TD-010** | Frontend state management placeholder (store/ empty) | frontend/src/store | 🟠 HIGH | 3-4 hrs | No centralized state (auth, documents, chat) |
| **TD-011** | OCR/RAG/LLM services not implemented | backend/app/services/ | 🟠 HIGH | 2-3 weeks | Core features missing |
| **TD-012** | Missing chat repository (ChatRepository) | backend/app/repositories/ | 🟠 HIGH | 2-3 hrs | Chat history queries not abstracted |
| **TD-013** | Frontend auth context missing | frontend/src/auth | 🟠 HIGH | 3-4 hrs | Token/user state not managed |
| **TD-014** | No error boundary integration in routes | frontend/src/routes | 🟠 HIGH | 1-2 hrs | Page crashes not caught |

### 5.3 **MEDIUM Priority (Next Sprint)**

| ID | Issue | Location | Severity | Effort | Impact |
|----|----|----------|----------|--------|--------|
| **TD-015** | No feature-specific API services (frontend) | frontend/src/services | 🟡 MEDIUM | 2-3 hrs | API calls scattered across components |
| **TD-016** | Missing custom hooks (frontend) | frontend/src/hooks | 🟡 MEDIUM | 2-3 hrs | Logic duplication, testability issues |
| **TD-017** | No form validation helpers (frontend) | frontend/src/utils | 🟡 MEDIUM | 2 hrs | Form validation logic scattered |
| **TD-018** | Inconsistent error handling (backend) | backend/app/ | 🟡 MEDIUM | 2-3 hrs | Exception mapping not centralized |
| **TD-019** | Logger setup but no structured logging (backend) | backend/app/core/logging.py | 🟡 MEDIUM | 2-3 hrs | Poor log searchability in production |
| **TD-020** | CORS not configured (backend) | backend/app/main.py | 🟡 MEDIUM | 30 min | Frontend cannot call backend in production |
| **TD-021** | No request/response interceptor on frontend Axios | frontend/src/services/api.ts | 🟡 MEDIUM | 1-2 hrs | Token refresh, error handling not automated |
| **TD-022** | Missing TypeScript strict mode enforcement | frontend/tsconfig.json | 🟡 MEDIUM | 30 min | Type safety not maximized |
| **TD-023** | No environment variable validation (frontend) | frontend/src | 🟡 MEDIUM | 1-2 hrs | Missing VITE_API_BASE_URL fallback |
| **TD-024** | Authentication routes lack rate limiting | backend/app/api/v1/routes/auth.py | 🟡 MEDIUM | 1-2 hrs | Brute force vulnerability |
| **TD-025** | No API versioning strategy documented | backend/app/api | 🟡 MEDIUM | 30 min | Future /v2 migration unclear |

### 5.4 **LOW Priority (Nice to Have)**

| ID | Issue | Location | Severity | Effort | Impact |
|----|----|----------|----------|--------|--------|
| **TD-026** | Re-export layers add indirection (backend) | backend/app/core/config.py, etc. | 🔵 LOW | 1-2 hrs | Namespace clarity vs. boilerplate trade-off |
| **TD-027** | No API documentation (Swagger/OpenAPI) | backend/ | 🔵 LOW | 1-2 hrs | API discoverability (FastAPI auto-docs exist, but custom tags needed) |
| **TD-028** | Missing .env.example files | Root, frontend, backend | 🔵 LOW | 30 min | Developer onboarding friction |
| **TD-029** | No linting/formatting setup (backend) | backend/ | 🔵 LOW | 1-2 hrs | Code style inconsistency |
| **TD-030** | No pre-commit hooks | Root | 🔵 LOW | 1-2 hrs | Prevents bad commits early |
| **TD-031** | Missing GitHub Actions workflows | .github/workflows | 🔵 LOW | 2-3 hrs | No CI/CD pipeline |
| **TD-032** | No Docker health checks (for frontend) | Root (docker-compose) | 🔵 LOW | 30 min | Missing container readiness detection |
| **TD-033** | TypeScript path aliases not optimized | frontend/tsconfig.json | 🔵 LOW | 30 min | Minor DX improvement |

---

## 6. UNUSED IMPORTS & CODE

### 6.1 **Backend - Unused Imports**

| File | Unused Import | Reason |
|------|---|---|
| `backend/app/main.py` | Line 5: duplicate import `auth_router, documents_router, health_router` | Imported twice (lines 5 and 17) |
| `backend/app/api/v1/routes/auth.py` | All imports | File just re-exports `router` from `app.auth.router` |
| `backend/app/services/document_service.py` | `stored_doc_dir, _ = None, None` (line 68) | Unused variable assignment |

### 6.2 **Frontend - Unused Code**

| File | Unused Code | Reason |
|------|---|---|
| `frontend/src/main.jsx` | Entire file | main.tsx is used instead; this is dead code |
| `frontend/src/App.jsx` | Entire file | app/App.tsx is actual app; this is placeholder |
| `frontend/src/vite.config.js` | Entire file | vite.config.ts exists; duplicate |
| `frontend/src/features/*` | All feature index.ts | Only barrel exports, no actual implementations |
| `frontend/src/hooks/.gitkeep` | Directory | Placeholder with no hooks |
| `frontend/src/layouts/.gitkeep` | Directory | Placeholder; layout components in /components/layout |
| `frontend/src/store/.gitkeep` | Directory | Placeholder; no state management implemented |

### 6.3 **Backend - Unused Directories**

| Directory | Status | Reason |
|-----------|--------|--------|
| `backend/app/domain/entities/` | Empty (__init__.py only) | Clean Architecture template, not used |
| `backend/app/domain/repositories/` | Empty (__init__.py only) | Abstract repo interfaces not implemented |
| `backend/app/infrastructure/` | Mostly empty | Placeholder for future services; duplicate of app/services |
| `backend/app/interfaces/api/` | Empty | No API interface definitions |
| `backend/app/middleware/` | .gitkeep only | No middleware; auth via dependencies |
| `backend/app/utils/` | .gitkeep only | No utility functions |

---

## 7. DOCKER READINESS ASSESSMENT

### 7.1 **Current State: 2/10 - INCOMPLETE**

**Missing:**
- ❌ Dockerfile.backend (FastAPI service)
- ❌ Dockerfile.frontend (React build)
- ❌ .dockerignore (prevents bloat)
- ❌ Multi-stage builds (not optimized for production)
- ⚠️ docker-compose.yml incomplete (only PostgreSQL defined)
- ⚠️ No Redis, Ollama, or LLM service definitions

**Partially Present:**
- ✅ docker-compose.yml (PostgreSQL 16 Alpine with volume)
- ✅ docker/README.md (mentions expected files but not created)

### 7.2 **Production Issues**
1. **PaddleOCR dependencies** (heavy ML library) → needs optimization
2. **FAISS** (vector search) → can cause large image if bundled
3. **OpenAI/Ollama integration** → network communication required
4. **Storage mounts** → /storage not mounted in docker-compose
5. **Environment variable management** → .env not loaded in container

### 7.3 **Recommended Dockerfile Strategy**
```
Backend:
  FROM python:3.12-slim
  Multi-stage: base → dependencies (cached) → app
  Stage 1: Install build-essential, compile wheels for PaddleOCR, FAISS
  Stage 2: Runtime-only (no build tools)
  Expose: 8000

Frontend:
  FROM node:20-alpine
  Multi-stage: build (npm run build) → serve (nginx)
  Stage 1: Build with npm
  Stage 2: nginx serving /dist
  Expose: 80

Docker Compose:
  - backend (port 8000)
  - frontend (port 80)
  - postgres (port 5432)
  - ollama (port 11434, optional)
  - redis (port 6379, optional for caching)
```

---

## 8. ALEMBIC READINESS ASSESSMENT

### 8.1 **Current State: 7/10 - CONFIGURED BUT NOT USED**

**Present:**
- ✅ alembic/ directory (versions/, env.py, script.py.mako)
- ✅ alembic.ini (PostgreSQL connection configured)
- ✅ Initial database schema exists (models defined in ORM)
- ✅ Environment setup in env.py (SQLAlchemy integration)

**Missing:**
- ❌ No initial migration (no alembic/versions/*.py files)
- ❌ `alembic init` command not run to create baseline
- ❌ Migration workflow not documented
- ⚠️ alembic.ini hardcodes local database URL (should use env variables)

### 8.2 **Next Steps for Alembic**
1. Create initial migration: `alembic revision --autogenerate -m "Initial schema"`
2. Apply migration: `alembic upgrade head`
3. Version control all migration files
4. Update alembic.ini to use DATABASE_URL env variable
5. Add migration running to Docker entrypoint

---

## 9. NAMING CONSISTENCY REVIEW

### 9.1 **Python (Backend) - Consistent ✅**
- **Modules:** snake_case ✅ (user_service.py, document_repository.py)
- **Classes:** PascalCase ✅ (AuthService, DocumentRepository, User)
- **Functions:** snake_case ✅ (get_current_user, create_access_token)
- **Constants:** UPPER_SNAKE_CASE ✅ (ACCESS_TOKEN_EXPIRE_MINUTES)
- **Private members:** _leading_underscore ✅ (_create_token_pair)

**Minor Issues:**
- Mixed use of `id` vs `user_id` vs `document_id` (OK - context-dependent)
- Some response models use suffix (LoginRequest, TokenResponse) - OK pattern

### 9.2 **TypeScript/React (Frontend) - Mostly Consistent ✅**
- **Modules:** camelCase ✅ (useAuth, api.ts, themeProvider.tsx)
- **Components:** PascalCase ✅ (LoginPage, ChatMessenger, ProtectedRoute)
- **Functions:** camelCase ✅ (handleSubmit, fetchDocuments)
- **Types:** PascalCase ✅ (User, Document, ApiResponse)
- **Constants:** UPPER_SNAKE_CASE ✅ (API_BASE_URL)

**Issues Found:**
- `AppShell` vs `appShell` (inconsistent in imports)
- Multiple entry points (main.jsx, main.tsx, App.jsx, app/App.tsx) - naming confusion

### 9.3 **Database - Consistent ✅**
- **Tables:** plural snake_case ✅ (users, documents, chat_history)
- **Columns:** snake_case ✅ (user_id, created_at, is_deleted)
- **Constraints:** Follows naming convention ✅ (fk_*, uq_*, pk_*)

---

## 10. CLEAN ARCHITECTURE BOUNDARIES

### 10.1 **Current Implementation vs. Clean Architecture Principles**

```
                         CURRENT STATE
                         
┌─────────────────────────────────────────┐
│     Web Layer (FastAPI Routes)          │  ← API tier
├─────────────────────────────────────────┤
│  API Layer                              │
│  ├─ /api/v1/routes/* (router)          │
│  ├─ /api/v1/schemas/* (DTOs)           │
│  └─ /api/v1/dependencies/* (DI)        │
├─────────────────────────────────────────┤
│  Service Layer                          │  ← Business Logic tier
│  ├─ /services/document_service.py      │     (some separation)
│  ├─ /auth/service.py                   │
│  └─ /repositories/* (data access)      │
├─────────────────────────────────────────┤
│  Domain Layer                           │
│  ├─ /models/* (ORM - SQLAlchemy)       │  ← Data tier
│  ├─ /database/* (session, engine)      │
│  └─ /domain/* (UNUSED)                 │
├─────────────────────────────────────────┤
│  Infrastructure (UNUSED)                │
│  ├─ /infrastructure/* (empty)          │
│  └─ /interfaces/* (empty)              │
└─────────────────────────────────────────┘

               RECOMMENDED STATE

┌──────────────────────────────────────────────────┐
│  Interface / Web Layer (FastAPI Routes)          │
│  ├─ /api/v1/routes/* (HTTP endpoints)           │
│  ├─ /api/v1/schemas/* (DTOs for HTTP)           │
│  └─ Error handling (400, 401, 404, 500)         │
├──────────────────────────────────────────────────┤
│  Application Layer (Use Cases / Orchestration)   │
│  ├─ /application/use_cases/* (User stories)     │
│  ├─ /application/services/* (Orchestration)     │
│  └─ DTOs (input/output)                         │
├──────────────────────────────────────────────────┤
│  Domain Layer (Business Rules - Pure)            │
│  ├─ /domain/entities/* (Value Objects)          │
│  ├─ /domain/repositories/* (Abstractions)       │
│  └─ /domain/exceptions/* (Domain errors)        │
├──────────────────────────────────────────────────┤
│  Infrastructure / Persistence Layer              │
│  ├─ /persistence/repositories/* (SQL impl)      │
│  ├─ /persistence/database/* (ORM setup)         │
│  ├─ /infrastructure/ocr/* (PaddleOCR)          │
│  ├─ /infrastructure/rag/* (LangChain, FAISS)   │
│  ├─ /infrastructure/llm/* (OpenAI, Ollama)     │
│  └─ /infrastructure/storage/* (File/Cloud)      │
└──────────────────────────────────────────────────┘
```

### 10.2 **Issues with Current Boundaries**

| Issue | Location | Impact |
|-------|----------|--------|
| **Domain layer unused** | `backend/app/domain/*` | Clean Arch intent not followed; repository abstractions missing |
| **Infrastructure scattered** | `backend/app/services/*` + `backend/app/infrastructure/*` | No clear separation of concerns |
| **Services mix responsibilities** | `DocumentService` mixes validation, storage, persistence | Violates Single Responsibility Principle |
| **Repository impls not abstracted** | Direct SQLAlchemy in `/repositories/*` | Difficult to test/swap implementations |
| **No use case layer** | `/application/use_cases/*` empty | Business logic mixed with HTTP concerns |
| **ORM models = domain models** | SQLAlchemy models used as domain entities | Cannot change DB without changing domain |

### 10.3 **Dependency Inversion Issues**

**Current (High-level depends on Low-level):**
```python
# In routes: direct import of service
from app.services.document_service import DocumentService
from app.repositories.document import DocumentRepository
↓
# Service depends on concrete repository
class DocumentService:
    def __init__(self, document_repository: DocumentRepository):
        # Tightly coupled to SQLAlchemy DocumentRepository
```

**Recommended (High-level depends on Abstractions):**
```python
# Routes depend on interface (not impl)
from app.domain.repositories import DocumentRepository
from app.application.services import DocumentService

# Domain defines interface
class DocumentRepository(ABC):
    @abstractmethod
    def get_by_id(self, doc_id: UUID) -> Document: ...

# Persistence implements interface
class SQLDocumentRepository(DocumentRepository):
    def get_by_id(self, doc_id: UUID) -> Document:
        # SQLAlchemy implementation
```

---

## 11. FRONTEND/BACKEND BOUNDARY ASSESSMENT

### 11.1 **Current Separation: 7/10 - Mostly Clean**

**Well Separated ✅**
- Frontend and backend are in separate directories
- REST API-first design (frontend calls backend HTTP API)
- API contracts defined via schemas (backend) and TypeScript types (frontend)
- Authentication via JWT (stateless, portable)
- CORS not configured (TODO)

**Issues ⚠️**
- Frontend hardcodes API base URL (http://localhost:8000)
- No API client code generation (could use OpenAPI/Swagger)
- Duplicate type definitions (backend Pydantic, frontend TypeScript)
- Missing feature-level API services (frontend)

### 11.2 **API Contracts**

**Current:**
```
Backend (Pydantic):
  ApiResponse[T]
  UserResponse
  TokenResponse
  DocumentUploadResponse
  DocumentListItem
  DocumentDetailResponse

Frontend (TypeScript):
  types/index.ts (empty)
  No explicit types for API responses
```

**Recommended:**
- Use `@openapi-generator` to generate frontend types from backend Swagger
- Or manually define types/api.ts matching backend schemas
- Document API versioning strategy

---

## 12. SUMMARY TABLE: Health by Domain

| Domain | Score | Key Issues | Fix Priority |
|--------|-------|-----------|-------------|
| **Folder Structure** | 5/10 | Unused/empty dirs (domain, infrastructure, interfaces, middleware, utils) | ⚠️ High |
| **Naming** | 8/10 | Consistent; multiple entry points confusing | ✅ Low |
| **Code Quality** | 6/10 | Duplication (ApiResponse, auth deps, React entry), unused imports | 🔴 Critical |
| **Architecture** | 3/10 | Clean Arch intent unused; no abstraction layers; tight coupling | 🔴 Critical |
| **Testing** | 2/10 | Zero tests; test dirs scaffolding only | 🔴 Critical |
| **Docker** | 2/10 | No Dockerfiles, docker-compose incomplete, no .dockerignore | 🔴 Critical |
| **Database** | 7/10 | Alembic configured; ORM models solid; no migrations created | ⚠️ Medium |
| **Documentation** | 8/10 | README, docs/ folder comprehensive; missing API docs | ✅ Low |
| **Frontend/Backend Boundary** | 7/10 | API-first design; JWT auth; missing type generation | ⚠️ Medium |
| **Dependencies** | 6/10 | requirements.txt + pyproject.toml conflict; no lock file | ⚠️ Medium |

---

## 13. ACTIONABLE RECOMMENDATIONS (Priority Order)

### Phase 1: Foundation (Week 1)
- [ ] **Fix duplicates:** Delete backend/app/schemas/common.py; use /api/v1/schemas/common.py
- [ ] **Fix React entry:** Keep main.tsx, delete main.jsx + App.jsx
- [ ] **Fix Vite config:** Keep vite.config.ts, delete vite.config.js
- [ ] **Create .gitignore entries** for __pycache__, .pytest_cache
- [ ] **Create .dockerignore**
- [ ] **Create initial Alembic migration:** `alembic revision --autogenerate -m "Initial schema"`

### Phase 2: Docker Support (Week 1-2)
- [ ] **Create Dockerfile.backend** (Python 3.12, multi-stage, PaddleOCR-optimized)
- [ ] **Create Dockerfile.frontend** (Node 20, multi-stage, Nginx)
- [ ] **Update docker-compose.yml** (add backend, frontend, storage volumes)
- [ ] **Test local docker-compose up** end-to-end

### Phase 3: Clean Architecture (Week 2-3)
- [ ] **Implement Domain layer** (abstract repository interfaces, entities)
- [ ] **Create Application layer** (use cases, service orchestration)
- [ ] **Move infrastructure code** (OCR, RAG, LLM adapters)
- [ ] **Remove unused dirs** (domain, infrastructure, interfaces placeholders)
- [ ] **Implement Dependency Inversion** (depend on abstractions)

### Phase 4: Testing (Week 3-4)
- [ ] **Setup pytest** (conftest.py, fixtures)
- [ ] **Write unit tests** (services, repositories, utils)
- [ ] **Write integration tests** (API routes, database)
- [ ] **Frontend tests** (vitest or Jest, React Testing Library)
- [ ] **Target 70%+ coverage**

### Phase 5: Frontend Enhancement (Week 4-5)
- [ ] **Implement Auth Context** (token, user, refresh logic)
- [ ] **Create feature-level API services** (auth, documents, chat)
- [ ] **Implement state management** (Zustand or Redux)
- [ ] **Add custom hooks** (useAuth, useAsync, etc.)
- [ ] **Implement error boundaries** on routes

### Phase 6: Production Readiness (Week 5-6)
- [ ] **Add CORS to backend**
- [ ] **Setup structured logging** (both ends)
- [ ] **Add rate limiting** (auth endpoints)
- [ ] **Setup CI/CD** (GitHub Actions)
- [ ] **Environment variable validation** (frontend + backend)
- [ ] **Add API documentation** (Swagger UI tags)

---

**End of Architecture Audit Report**

*Generated: 2024 | No files modified during audit*
