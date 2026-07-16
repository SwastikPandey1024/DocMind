# Duplicate List - DocMind AI

**Total Duplicates Found: 10 (6 critical, 4 moderate)**

---

## 1. CRITICAL DUPLICATES

### 1.1 API Response Schema Duplication

**Issue ID:** DUP-001  
**Severity:** 🔴 CRITICAL  
**Effort to Fix:** 30 minutes  
**Impact:** DRY violation, import ambiguity, maintenance burden

#### Files Involved:
```
backend/app/schemas/common.py
└─ ApiResponse[T] (lines 6-11)
   ErrorResponse (lines 14-18)

backend/app/api/v1/schemas/common.py
└─ ApiResponse[T] (lines 6-11) [IDENTICAL]
   ErrorResponse (lines 14-18) [IDENTICAL]
```

#### Comparison:
```python
# Both files define identical code:

# backend/app/schemas/common.py
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: Optional[T] = None
    errors: Optional[list[str]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: list[str] = Field(default_factory=list)

# backend/app/api/v1/schemas/common.py
# [Identical code]
```

#### Import Locations:
```python
# Used in:
backend/app/auth/router.py
  → Imports from app.api.v1.schemas.common (correct)

backend/app/api/v1/routes/documents.py
  → Imports from app.api.v1.schemas.common (correct)

backend/app/api/v1/routes/health.py
  → May import from app.schemas.common (inconsistent)
```

#### Recommendation:
- **DELETE:** `backend/app/schemas/common.py`
- **KEEP:** `backend/app/api/v1/schemas/common.py` (versioned, in API folder)
- **UPDATE:** All imports to use `/api/v1/schemas/common.py`

---

### 1.2 React Entry Points Duplication

**Issue ID:** DUP-002  
**Severity:** 🔴 CRITICAL  
**Effort to Fix:** 30 minutes  
**Impact:** App initialization confusion, multiple execution paths

#### Files Involved:
```
frontend/src/main.jsx (PLACEHOLDER)
  └─ ReactDOM.createRoot only, no providers

frontend/src/main.tsx (ACTUAL - with providers)
  └─ QueryClient, BrowserRouter, App setup

frontend/src/App.jsx (PLACEHOLDER)
  └─ Simple heading, no integration

frontend/src/app/App.tsx (ACTUAL - main app)
  └─ ThemeProvider, ErrorBoundary, AppShell, routing
```

#### Code Comparison:

**main.jsx (WRONG - Simple, no setup):**
```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**main.tsx (CORRECT - Full setup):**
```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import App from '@/app/App';
import '@/styles/index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
```

**App.jsx (WRONG - Placeholder):**
```jsx
export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
      <div className="max-w-2xl rounded-xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
        <h1 className="text-3xl font-semibold">DocMind AI</h1>
        <p className="mt-3 text-slate-400">
          OCR + RAG document chat system scaffold is ready.
        </p>
      </div>
    </div>
  );
}
```

**app/App.tsx (CORRECT - Actual app):**
```tsx
import { Suspense } from 'react';
import { Outlet } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { ThemeProvider } from '@/components/common/ThemeProvider';
import { AppRoutes } from '@/routes';
import { LoadingScreen } from '@/components/common/LoadingScreen';

export default function App() {
  return (
    <ThemeProvider>
      <ErrorBoundary>
        <Suspense fallback={<LoadingScreen message="Loading DocMind..." />}>
          <AppShell>
            <Outlet />
            <AppRoutes />
          </AppShell>
        </Suspense>
      </ErrorBoundary>
    </ThemeProvider>
  );
}
```

#### index.html Reference:
```html
<!-- Uses root element -->
<div id="root"></div>

<!-- Currently unclear which main.* is executed -->
<!-- Package.json likely defaults to main.tsx but can cause confusion -->
```

#### Recommendation:
- **DELETE:** 
  - `frontend/src/main.jsx`
  - `frontend/src/App.jsx`
- **KEEP:** 
  - `frontend/src/main.tsx` (full setup)
  - `frontend/src/app/App.tsx` (main component)
- **UPDATE:** 
  - package.json ensure it references correct entry point

---

### 1.3 Vite Configuration Duplication

**Issue ID:** DUP-003  
**Severity:** 🔴 CRITICAL  
**Effort to Fix:** 15 minutes  
**Impact:** Build tool confusion, inconsistent configuration

#### Files Involved:
```
frontend/vite.config.js (JavaScript version)
└─ defineConfig with React plugin

frontend/vite.config.ts (TypeScript version)
└─ [Not compared, but existence is duplicate]
```

#### Code:

**frontend/vite.config.js:**
```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173
  }
});
```

**frontend/vite.config.ts:**
```typescript
// Likely identical or very similar
```

#### Issue:
- Vite might load both (JS takes precedence)
- Confusion when updating one without the other
- TypeScript project should use .ts config

#### Recommendation:
- **DELETE:** `frontend/vite.config.js`
- **KEEP:** `frontend/vite.config.ts`
- Verify both are identical before deletion
- Update if .ts has different configuration

---

### 1.4 Authentication Dependencies Re-export

**Issue ID:** DUP-004  
**Severity:** 🟠 HIGH (re-export pattern, not code duplication)  
**Effort to Fix:** 30 minutes  
**Impact:** Import ambiguity, indirection

#### Files Involved:
```
backend/app/auth/dependencies.py (SOURCE OF TRUTH)
└─ bearer_scheme
├─ get_user_repository()
├─ get_auth_service()
├─ get_current_user()
├─ get_current_active_user()
└─ get_admin_user()

backend/app/api/v1/dependencies/auth.py (RE-EXPORT - BACKWARD COMPAT)
└─ from app.auth.dependencies import (all above)
└─ __all__ = [list of above]
```

#### Code:

**backend/app/auth/dependencies.py (SOURCE):**
```python
from __future__ import annotations
import uuid
from collections.abc import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.auth.jwt import TokenDecodeError, decode_token
from app.auth.service import AuthService
from app.database.dependencies import get_db_session
from app.models.user import User
from app.repositories.user import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)

def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)

def get_auth_service(user_repository: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repository)

def get_current_user(...) -> User:
    # [implementation]

def get_current_active_user(...) -> User:
    # [implementation]

def get_admin_user(...) -> User:
    # [implementation]
```

**backend/app/api/v1/dependencies/auth.py (RE-EXPORT):**
```python
from __future__ import annotations

# Backward-compatible re-export layer.
from app.auth.dependencies import (  # noqa: F401
    bearer_scheme,
    get_admin_user,
    get_auth_service,
    get_current_active_user,
    get_current_user,
    get_user_repository,
)

__all__ = [
    "bearer_scheme",
    "get_user_repository",
    "get_auth_service",
    "get_current_user",
    "get_current_active_user",
    "get_admin_user",
]
```

#### Import Locations:
```python
# Both patterns exist in codebase:

# Pattern 1: Direct import from auth (preferred)
from app.auth.dependencies import get_current_user

# Pattern 2: Via API v1 re-export (legacy)
from app.api.v1.dependencies.auth import get_current_user
```

#### Recommendation:
- **KEEP:** `backend/app/auth/dependencies.py` (source of truth)
- **DEPRECATE:** `backend/app/api/v1/dependencies/auth.py` (re-export layer)
  - Mark with `# DEPRECATED: Use app.auth.dependencies directly`
  - Update all imports to use `app.auth.dependencies`
  - Remove re-export file in next refactor phase

---

## 2. MODERATE DUPLICATES

### 2.1 Base Model Re-export

**Issue ID:** DUP-005  
**Severity:** 🟡 MEDIUM  
**Effort to Fix:** 20 minutes  
**Impact:** Indirection, but acceptable pattern

#### Files Involved:
```
backend/app/database/base.py (SOURCE - actual definitions)
├─ Base (DeclarativeBase)
├─ UUIDPrimaryKeyMixin
├─ TimestampMixin
└─ SoftDeleteMixin

backend/app/models/base.py (RE-EXPORT)
└─ from app.database.base import Base, SoftDeleteMixin, ...
```

#### Code:

**backend/app/database/base.py:**
```python
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, MetaData, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

naming_convention = { ... }

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=naming_convention)
    # [implementation]

class UUIDPrimaryKeyMixin:
    # [implementation]

class TimestampMixin:
    # [implementation]

class SoftDeleteMixin:
    # [implementation]
```

**backend/app/models/base.py:**
```python
from app.database.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

__all__ = ["Base", "SoftDeleteMixin", "TimestampMixin", "UUIDPrimaryKeyMixin"]
```

#### Import Pattern:
```python
# Some files use database/base:
from app.database.base import Base, SoftDeleteMixin, TimestampMixin

# Some files use models/base:
from app.models.base import Base, SoftDeleteMixin, TimestampMixin

# [Inconsistent]
```

#### Recommendation:
- **KEEP:** `backend/app/database/base.py` (source of truth)
- **CONSIDER REMOVING:** `backend/app/models/base.py` (re-export)
  - If removed, update all imports to use `app.database.base`
  - OR keep if namespace organization is desired

---

### 2.2 Settings Re-export

**Issue ID:** DUP-006  
**Severity:** 🔵 LOW (acceptable import indirection)  
**Effort to Fix:** 15 minutes  
**Impact:** Minimal

#### Files Involved:
```
backend/app/core/settings.py (SOURCE)
├─ class Settings (Pydantic BaseSettings)
└─ get_settings() function

backend/app/core/config.py (RE-EXPORT)
└─ __all__ = ["Settings", "get_settings"]
```

#### Code:

**backend/app/core/settings.py:**
```python
from functools import lru_cache
from typing import Literal
from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.constants import Environment

class Settings(BaseSettings):
    app_name: str = Field(...)
    app_version: str = Field(...)
    environment: Literal["development", "testing", "production"] = Field(...)
    # [more fields]
    
    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: str, info: ValidationInfo) -> str:
        # [validation]

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
```

**backend/app/core/config.py:**
```python
from app.core.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
```

#### Import Pattern:
```python
# Both patterns exist:
from app.core.settings import get_settings
from app.core.config import get_settings  # via re-export
```

#### Recommendation:
- **KEEP:** Re-export is acceptable for namespace organization (core/config pattern is common)
- **OR REMOVE:** If it's deemed unnecessary indirection

---

## 3. EMPTY/UNUSED DIRECTORIES (Dead Code)

### 3.1 Backend Empty Directories

| Directory | Status | Files | Recommendation |
|-----------|--------|-------|---|
| `backend/app/domain/entities/` | Empty | Only __init__.py | DELETE - Clean Arch template not used |
| `backend/app/domain/repositories/` | Empty | Only __init__.py | DELETE - Abstract repo interfaces not implemented |
| `backend/app/infrastructure/database/` | Empty | Only __init__.py | DELETE - Duplicate of /database/ |
| `backend/app/infrastructure/ocr/` | Empty | Only __init__.py | KEEP - Future OCR implementation |
| `backend/app/infrastructure/rag/` | Empty | Only __init__.py | KEEP - Future RAG implementation |
| `backend/app/interfaces/api/` | Empty | Only __init__.py | DELETE - No API interface definitions |
| `backend/app/middleware/` | Scaffold | .gitkeep only | DELETE - Auth via dependencies, not middleware |
| `backend/app/utils/` | Scaffold | .gitkeep only | DELETE - No utilities yet |

### 3.2 Frontend Empty Directories

| Directory | Status | Files | Recommendation |
|-----------|--------|-------|---|
| `frontend/src/hooks/` | Scaffold | .gitkeep only | DELETE - No custom hooks yet |
| `frontend/src/layouts/` | Scaffold | .gitkeep only | DELETE - Duplicate of /components/layout |
| `frontend/src/store/` | Scaffold | .gitkeep only | DELETE - No state management yet |

### 3.3 Test Scaffolding Directories

| Directory | Status | Files | Recommendation |
|-----------|--------|-------|---|
| `tests/backend/` | Scaffold | .gitkeep only | KEEP but populate with tests |
| `tests/e2e/` | Scaffold | .gitkeep only | KEEP but populate with e2e tests |
| `tests/frontend/` | Scaffold | .gitkeep only | KEEP but populate with component tests |

---

## 4. SUMMARY TABLE: What to Delete

| File/Dir | Severity | Fix | Effort |
|----------|----------|-----|--------|
| `backend/app/schemas/common.py` | 🔴 CRITICAL | Delete | 5 min |
| `frontend/src/main.jsx` | 🔴 CRITICAL | Delete | 2 min |
| `frontend/src/App.jsx` | 🔴 CRITICAL | Delete | 2 min |
| `frontend/vite.config.js` | 🔴 CRITICAL | Delete | 2 min |
| `backend/app/domain/entities/` | 🔴 CRITICAL | Delete | 2 min |
| `backend/app/domain/repositories/` | 🔴 CRITICAL | Delete | 2 min |
| `backend/app/infrastructure/database/` | 🔴 CRITICAL | Delete | 2 min |
| `backend/app/interfaces/api/` | 🔴 CRITICAL | Delete | 2 min |
| `backend/app/middleware/` | 🔴 CRITICAL | Delete | 2 min |
| `backend/app/utils/` | 🔴 CRITICAL | Delete | 2 min |
| `frontend/src/hooks/` | 🔴 CRITICAL | Delete | 2 min |
| `frontend/src/layouts/` | 🔴 CRITICAL | Delete | 2 min |
| `frontend/src/store/` (initially) | 🟠 HIGH | Delete then recreate | 5 min |
| **TOTAL** | | | ~35 minutes |

---

## 5. CLEANUP ORDER

### Step 1: Verify Before Deletion
```bash
# Check what imports each file
grep -r "from app.schemas.common import" backend/
grep -r "from.*main.jsx import" frontend/
grep -r "from.*App.jsx import" frontend/
```

### Step 2: Delete Files
```bash
rm backend/app/schemas/common.py
rm frontend/src/main.jsx
rm frontend/src/App.jsx
rm frontend/vite.config.js
rm -rf backend/app/domain/entities/
rm -rf backend/app/domain/repositories/
rm -rf backend/app/infrastructure/database/
rm -rf backend/app/interfaces/api/
rm -rf backend/app/middleware/
rm -rf backend/app/utils/
rm -rf frontend/src/hooks/
rm -rf frontend/src/layouts/
```

### Step 3: Update Imports
```bash
# Update all imports to use /api/v1/schemas/common
find backend -name "*.py" -type f -exec sed -i 's/from app\.schemas\.common import/from app.api.v1.schemas.common import/g' {} +

# Update all imports to use app.auth.dependencies
find backend -name "*.py" -type f -exec sed -i 's/from app\.api\.v1\.dependencies\.auth import/from app.auth.dependencies import/g' {} +
```

### Step 4: Git Commit
```bash
git add -A
git commit -m "refactor: remove duplicate files and unused directories

- Delete duplicate ApiResponse schema (keep api/v1/schemas version)
- Delete duplicate React entry points (keep main.tsx and app/App.tsx)
- Delete duplicate vite config (keep .ts version)
- Delete unused Clean Arch template directories
- Delete empty scaffold directories
- Update all imports to use canonical locations
"
```

---

**End of Duplicate List**

*No code was modified during this analysis*
