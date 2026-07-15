# API Design Notes

## Backend Endpoints
- POST /api/v1/documents/upload
- GET /api/v1/documents
- DELETE /api/v1/documents/{id}
- POST /api/v1/chat/query
- GET /api/v1/chat/history
- POST /auth/register
- POST /auth/login

## Response Conventions
- JSON payloads
- Standard error envelope with status and message
- Citation metadata included in chat responses
