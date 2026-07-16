# SPRINT 0 EXECUTION PLAN

**Overall Health Score:** 4.4/10 (🔴 CRITICAL)  
**Production Ready:** NO  
**Estimated Time to Stabilize:** 3-4 weeks (60-80 hours)

---

## PRIORITY-ORDERED EXECUTION PLAN

### PHASE 1: CRITICAL FIXES (Must do first - 6-8 hours)

#### Priority 1.1: Remove Frontend Entry Point Duplicates
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1 hour  
**Risk:** Low (backward compatible)  

**Tasks:**
1. Delete `frontend/src/main.jsx` (placeholder)
2. Delete `frontend/src/App.jsx` (placeholder)
3. Verify `frontend/src/main.tsx` is complete
4. Verify `frontend/src/app/App.tsx` is the app root
5. Update package.json entry point if needed

**Acceptance Criteria:**
- ✅ Only main.tsx exists as entry point
- ✅ Only app/App.tsx exists as root component
- ✅ Frontend builds without errors
- ✅ No import conflicts

---

#### Priority 1.2: Fix Frontend Vite Config Conflict
**Status:** ⏳ Ready to implement  
**Estimated Time:** 30 minutes  
**Risk:** Low (single file)  

**Tasks:**
1. Delete `frontend/vite.config.js` (port 5173)
2. Keep `frontend/vite.config.ts` (port 3000, has alias)
3. Verify build uses correct config
4. Test `npm run dev` starts on correct port

**Acceptance Criteria:**
- ✅ Only vite.config.ts exists
- ✅ Dev server starts on port 3000
- ✅ Path alias @ works

---

#### Priority 1.3: Fix Backend DATABASE_URL Default (Docker)
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1 hour  
**Risk:** Low (still backward compatible)  

**Tasks:**
1. Modify `backend/app/core/settings.py`
2. Change DATABASE_URL default from `localhost` to use service name
3. Make it recognizable for Docker (e.g., `postgres` service)
4. Preserve localhost compatibility for local dev

**Acceptance Criteria:**
- ✅ DATABASE_URL can accept env var
- ✅ Default works in Docker (uses `postgres` service)
- ✅ Local dev still works with override
- ✅ Production DATABASE_URL validates properly

**Exact Change:**
```python
# OLD
database_url: str = Field(
    default="postgresql+psycopg2://postgres:postgres@localhost:5432/docmind",
    validation_alias="DATABASE_URL"
)

# NEW (preserve localhost for dev, but make Docker-aware)
database_url: str = Field(
    default="postgresql+psycopg2://postgres:postgres@postgres:5432/docmind",  # Service name
    validation_alias="DATABASE_URL"
)
```

---

#### Priority 1.4: Fix Backend Duplicate Router Import
**Status:** ⏳ Ready to implement  
**Estimated Time:** 15 minutes  
**Risk:** Very low (code cleanup)  

**Tasks:**
1. In `backend/app/main.py`, remove line 5-6 (first import)
2. Keep line 17 (second import with documents_router)
3. Remove duplicate /health endpoint (already in health_router)
4. Verify app starts without errors

**Acceptance Criteria:**
- ✅ No duplicate imports
- ✅ No duplicate endpoints
- ✅ All routers registered once
- ✅ /health endpoint works

---

#### Priority 1.5: Consolidate Backend Dependencies
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1 hour  
**Risk:** Medium (version compatibility)  

**Tasks:**
1. Copy all dependencies from requirements.txt to pyproject.toml
2. Use exact versions from requirements.txt
3. Remove duplicate version specs
4. Add paddleocr, langchain, faiss-cpu, openai to pyproject.toml
5. Update pyproject.toml to be single source of truth

**Acceptance Criteria:**
- ✅ pyproject.toml has all 17 dependencies
- ✅ requirements.txt can be deleted (pyproject is source)
- ✅ Versions are pinned (==) for reproducibility
- ✅ Backend can install from pyproject.toml only

---

#### Priority 1.6: Fix OLLAMA_HOST Default (Docker)
**Status:** ⏳ Ready to implement  
**Estimated Time:** 30 minutes  
**Risk:** Low (optional service)  

**Tasks:**
1. Modify `backend/app/core/settings.py`
2. Change OLLAMA_HOST default from `localhost:11434` to service name
3. Make it work in Docker (e.g., `ollama:11434`)
4. Preserve localhost for local dev

**Acceptance Criteria:**
- ✅ Default uses service name `ollama`
- ✅ Can override with env var
- ✅ Local dev can use localhost
- ✅ Production can use external URL

---

### PHASE 2: STRUCTURAL FIXES (6-8 hours)

#### Priority 2.1: Remove Duplicate Backend Schemas
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1 hour  
**Risk:** Medium (imports need updating)  

**Tasks:**
1. Delete `backend/app/schemas/common.py` (duplicate)
2. Verify all imports point to `/api/v1/schemas/common.py`
3. Update any imports from `/app/schemas/common.py`
4. Verify no import conflicts

**Acceptance Criteria:**
- ✅ Only `/api/v1/schemas/common.py` exists
- ✅ All imports use canonical location
- ✅ No circular imports
- ✅ Backend compiles

---

#### Priority 2.2: Remove Backend Config Re-export
**Status:** ⏳ Ready to implement  
**Estimated Time:** 30 minutes  
**Risk:** Low (unnecessary layer)  

**Tasks:**
1. Review if `/core/config.py` is actually used
2. If only re-export, delete it
3. Update all imports to use `/core/settings.py` directly
4. Verify backend compiles

**Acceptance Criteria:**
- ✅ No unnecessary re-export layer
- ✅ All imports consolidated
- ✅ Cleaner module structure

---

#### Priority 2.3: Remove Backend Base Model Re-export
**Status:** ⏳ Ready to implement  
**Estimated Time:** 30 minutes  
**Risk:** Low (unnecessary layer)  

**Tasks:**
1. Delete `backend/app/models/base.py` (re-export)
2. Update imports to use `/database/base.py`
3. Verify all ORM models import correctly
4. Backend compiles

**Acceptance Criteria:**
- ✅ Single source of truth for Base
- ✅ All models import from `/database/base.py`
- ✅ No circular imports

---

#### Priority 2.4: Clean Up Empty/Placeholder Directories
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1 hour  
**Risk:** Very low (just cleanup)  

**Tasks:**
1. Delete `backend/app/domain/` (empty, Clean Arch not implemented)
2. Delete `backend/app/infrastructure/` (empty placeholder)
3. Delete `backend/app/interfaces/` (empty placeholder)
4. Delete `backend/app/middleware/` (empty, auth via dependencies)
5. Delete `backend/app/utils/` (empty)
6. Update documentation

**Acceptance Criteria:**
- ✅ No empty directories
- ✅ Cleaner project structure
- ✅ No confusion about unused layers

---

#### Priority 2.5: Clean Up Frontend Empty Directories
**Status:** ⏳ Ready to implement  
**Estimated Time:** 30 minutes  
**Risk:** Very low (just cleanup)  

**Tasks:**
1. Delete `frontend/src/hooks/` (.gitkeep only)
2. Delete `frontend/src/layouts/` (layout in /components/layout instead)
3. Delete `frontend/src/store/` (will recreate with state management)
4. Keep `/pages`, `/components`, `/routes`, `/services`, `/types`, `/utils`

**Acceptance Criteria:**
- ✅ No redundant empty directories
- ✅ Clearer project structure

---

### PHASE 3: MISSING INFRASTRUCTURE (8-10 hours)

#### Priority 3.1: Fix Environment Variables (.env files)
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1 hour  
**Risk:** Low (documentation only)  

**Tasks:**
1. Update `.env.example` with Docker-compatible values
2. Add production notes (use service names)
3. Ensure all backend env vars documented
4. Ensure all frontend env vars documented
5. Create `.env.docker` template (for CI/CD)
6. Create `.env.production` template (for docs)

**Acceptance Criteria:**
- ✅ DATABASE_URL example uses `postgres` service name
- ✅ OLLAMA_HOST example uses `ollama` service name
- ✅ All variables explained
- ✅ Multiple environment templates

---

#### Priority 3.2: Add CORS Middleware (Backend)
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1-2 hours  
**Risk:** Low (standard middleware)  

**Tasks:**
1. Create `backend/app/middleware/cors.py`
2. Add CORS middleware to main.py
3. Configure allowed origins (localhost for dev, *.example.com for prod)
4. Allow credentials for auth endpoints
5. Add test to verify headers

**Acceptance Criteria:**
- ✅ CORS middleware added
- ✅ Credentials allowed
- ✅ Access-Control headers present
- ✅ Frontend can call backend without CORS errors

---

#### Priority 3.3: Add Error Handling Middleware (Backend)
**Status:** ⏳ Ready to implement  
**Estimated Time:** 2-3 hours  
**Risk:** Medium (complex error mapping)  

**Tasks:**
1. Create `backend/app/shared/exceptions.py` (custom exceptions)
2. Create `backend/app/middleware/error_handler.py` (middleware)
3. Add to main.py
4. Map domain exceptions to HTTP status codes
5. Return consistent error format
6. Log exceptions properly

**Acceptance Criteria:**
- ✅ Custom exceptions defined
- ✅ Global exception handler added
- ✅ Consistent error response format
- ✅ Errors logged with context

---

#### Priority 3.4: Add Request Logging Middleware (Backend)
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1-2 hours  
**Risk:** Low (standard middleware)  

**Tasks:**
1. Create `backend/app/middleware/logging.py`
2. Log request method, path, query params
3. Log response status, time
4. Add request ID/correlation ID
5. Redact sensitive data
6. Add to main.py

**Acceptance Criteria:**
- ✅ All requests logged
- ✅ Request duration recorded
- ✅ Sensitive data redacted
- ✅ Correlation ID present

---

#### Priority 3.5: Add Database Health Check (Startup)
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1-2 hours  
**Risk:** Low (startup check only)  

**Tasks:**
1. Create startup event in FastAPI
2. Test database connection
3. Test file permissions (upload dir)
4. Test configuration validity
5. Raise error if startup checks fail

**Acceptance Criteria:**
- ✅ Database connectivity verified at startup
- ✅ Upload directory accessible
- ✅ Configuration valid
- ✅ App fails fast if preconditions not met

---

### PHASE 4: DEPENDENCY & CONFIG (2-3 hours)

#### Priority 4.1: Fix CI/CD Workflow
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1-2 hours  
**Risk:** Low (CI/CD improvement)  

**Tasks:**
1. Update `python-version` to 3.12 (matches backend)
2. Add backend pytest tests
3. Add frontend vitest tests
4. Add backend linting (ruff)
5. Add frontend linting (eslint)
6. Add backend type checking (mypy)
7. Add frontend type checking (tsc)

**Acceptance Criteria:**
- ✅ CI runs tests (not just compile)
- ✅ CI runs linting
- ✅ CI runs type checking
- ✅ PR blocked if tests fail

---

#### Priority 4.2: Update Documentation
**Status:** ⏳ Ready to implement  
**Estimated Time:** 1 hour  
**Risk:** Very low (docs only)  

**Tasks:**
1. Update README.md with current status
2. Update ARCHITECTURE.md
3. Add SPRINT_0_STABILIZATION.md
4. Document all critical fixes
5. Add production deployment notes
6. Add troubleshooting guide

**Acceptance Criteria:**
- ✅ All changes documented
- ✅ Clear setup instructions
- ✅ Deployment guide updated

---

### PHASE 5: PRODUCTION READINESS (2-3 hours)

#### Priority 5.1: Prepare Docker Implementation
**Status:** ⏳ Analysis only (E-001)  
**Estimated Time:** Not in Sprint 0  

**Purpose:** Ensure all prerequisites met for E-001 Containerization

**Verification:**
- ✅ Backend code production-ready
- ✅ Frontend code production-ready
- ✅ Environment variables externalized
- ✅ All startup issues fixed
- ✅ Documentation complete
- ✅ Dependencies consolidated

---

## EXECUTION SEQUENCE

**Week 1: Critical Fixes**
1. Priority 1.1 - Remove entry point duplicates (1h)
2. Priority 1.2 - Fix Vite config (30m)
3. Priority 1.3 - Fix DATABASE_URL (1h)
4. Priority 1.4 - Remove duplicate imports (15m)
5. Priority 1.5 - Consolidate dependencies (1h)
6. Priority 1.6 - Fix OLLAMA_HOST (30m)
7. **Total: 4.25 hours**

**Week 1-2: Structural Fixes**
8. Priority 2.1 - Remove duplicate schemas (1h)
9. Priority 2.2 - Remove config re-export (30m)
10. Priority 2.3 - Remove base model re-export (30m)
11. Priority 2.4 - Clean up backend dirs (1h)
12. Priority 2.5 - Clean up frontend dirs (30m)
13. **Total: 3.5 hours**

**Week 2: Missing Infrastructure**
14. Priority 3.1 - Fix env files (1h)
15. Priority 3.2 - Add CORS middleware (1-2h)
16. Priority 3.3 - Add error handler (2-3h)
17. Priority 3.4 - Add request logging (1-2h)
18. Priority 3.5 - Add health check (1-2h)
19. **Total: 7-10 hours**

**Week 3: Dependencies & Config**
20. Priority 4.1 - Fix CI/CD (1-2h)
21. Priority 4.2 - Update documentation (1h)
22. **Total: 2-3 hours**

**Overall Total: 16.75 - 21 hours (2-3 weeks)**

---

## DELIVERABLES BY PHASE

### Phase 1 Deliverables
- ✅ Files modified list
- ✅ Risk assessment
- ✅ Testing commands
- ✅ Git commits

### Phase 2 Deliverables
- ✅ Refactored structure
- ✅ No breaking changes
- ✅ All imports working
- ✅ Backend compiles

### Phase 3 Deliverables
- ✅ Middleware implementations
- ✅ Error handling
- ✅ Request logging
- ✅ Health checks

### Phase 4 Deliverables
- ✅ Updated CI/CD
- ✅ Complete documentation
- ✅ Deployment guide

### Phase 5 Deliverables
- ✅ Sprint 0 certification (ready for E-001)
- ✅ Final health check (target 7/10 minimum)
- ✅ Handoff to E-001 (Containerization)

---

## SUCCESS CRITERIA FOR SPRINT 0

| Criteria | Target | Current | Status |
|----------|--------|---------|--------|
| Health Score | 7/10 | 4.4/10 | ⏳ Pending |
| Critical Issues | 0 | 10 | ⏳ Pending |
| Duplicates | 0 | 13 | ⏳ Pending |
| Test Pass Rate | 100% | N/A | ⏳ Pending |
| Docker Ready | 50%+ | 1% | ⏳ Pending |
| Production Ready | YES | NO | ⏳ Pending |
| All Docs Updated | YES | Partial | ⏳ Pending |

---

**After Sprint 0 Completion:**
- ✅ Project stabilized
- ✅ All critical issues fixed
- ✅ Ready for E-001 (Containerization)
- ✅ Production deployment possible

---

## NEXT PHASE AFTER SPRINT 0

**E-001: Containerization & Deployment (4-5 days)**
- Create Dockerfile.backend
- Create Dockerfile.frontend
- Update docker-compose.yml with all services
- Create docker-compose.production.yml
- Implement health checks for all services
- Verify end-to-end Docker deployment

