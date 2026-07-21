# API Design Notes

## Backend Endpoints
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- GET /api/v1/auth/me
- POST /api/v1/documents/upload
- GET /api/v1/documents
- GET /api/v1/documents/{document_id}
- DELETE /api/v1/documents/{document_id}
- POST /api/v1/chat
- POST /api/v1/chat/stream
- GET /api/v1/chat/history
- GET /api/v1/chat/history/{document_id}
- GET /api/v1/health
- GET /api/v1/ready

## Authentication

All protected endpoints require a JWT Bearer token in the `Authorization` header:

```bash
Authorization: Bearer <access_token>
```

### Register
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## Response Conventions
- JSON payloads
- Standard error envelope with status and message
- Citation metadata included in chat responses

## Full API Documentation

Interactive documentation is available via:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

