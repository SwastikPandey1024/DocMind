# Backend Foundation Guide

## CORS Middleware

Configured in `app/middleware/cors.py`:

### Development
- Allows all localhost variants
- Allows Docker network names (frontend, backend)
- Allows credentials

### Production
- Explicitly configured origins
- Update `setup_cors()` function with your domain

```python
# In middleware/cors.py - production configuration
allowed_origins = [
    "https://yourdomainl.com",
    "https://app.yourdomain.com",
]
```

## Exception Handling

Global exception handler in `app/middleware/exceptions.py`:

Catches:
- **SQLAlchemyError** → 500 Internal Server Error
- **ValueError** → 400 Bad Request
- **Any Exception** → 500 Internal Server Error

All exceptions:
- Logged with request_id
- Return standardized JSON response
- Include X-Request-ID header

## Request Logging

Middleware in `app/middleware/logging.py`:

Logs:
- HTTP method, path, status code
- Request/response time (milliseconds)
- Client IP address
- Query string parameters
- Errors with full context

Headers added:
- `X-Request-ID` - Unique request identifier
- `X-Process-Time` - Request duration in seconds

## Dependency Injection

In `app/database/dependencies.py`:

```python
# Usage in route handlers
from fastapi import Depends
from app.database.dependencies import get_db_session

@app.get("/items")
async def get_items(db: Session = Depends(get_db_session)):
    return db.query(Item).all()
```

Session automatically closed after request.

## Health Checks

Enhanced health endpoint in `app/api/v1/routes/health.py`:

Verifies:
- API is running
- Database connection working
- Required tables exist
- Returns timestamp of check

## Startup Validation

In `app/startup.py`:

Checks:
- Environment configuration
- Upload directory writable
- JWT secret set (production)
- Database URL format valid

Runs before application starts.

## Configuration Validation

In `app/core/settings.py`:

- JWT_SECRET required in production
- DATABASE_URL must be valid PostgreSQL/SQLite
- All settings loaded from .env or environment

## Graceful Shutdown

In `app/main.py` lifespan:

- Closes database connections
- Releases resources
- Logs shutdown

## Testing

```bash
# Test CORS
curl -H "Origin: http://localhost:3000" http://localhost:8000/health

# Test error handling
curl http://localhost:8000/api/v1/invalid-endpoint

# Test logging
docker-compose logs backend | grep "X-Request-ID"

# Test health check
curl http://localhost:8000/health
```

## Production Deployment

1. Set JWT_SECRET in production environment
2. Update CORS origins in middleware/cors.py
3. Set APP_ENV=production in .env
4. Set DEBUG=false
5. All validation runs automatically on startup
