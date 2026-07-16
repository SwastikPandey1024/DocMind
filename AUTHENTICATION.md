# Authentication Guide

## JWT Implementation

Located in `app/auth/jwt.py`:

### Token Creation
- **Access Token**: Short-lived (default 15 minutes)
- **Refresh Token**: Long-lived (default 7 days)
- Both use HS256 algorithm
- Payload includes: sub (user_id), type, exp, iat

```python
from app.auth.jwt import create_access_token, create_refresh_token

# Create tokens
access_token = create_access_token(subject=str(user_id))
refresh_token = create_refresh_token(subject=str(user_id))
```

### Token Validation
```python
from app.auth.jwt import decode_token, TokenDecodeError

try:
    payload = decode_token(token, expected_type="access")
    user_id = payload["sub"]
except TokenDecodeError:
    # Invalid or expired token
    raise HTTPException(status_code=401)
```

## Password Security

Located in `app/auth/password.py`:

### Hashing
- Uses Argon2 (recommended algorithm)
- Automatic salt generation
- Industry-standard implementation via `pwdlib`

```python
from app.auth.password import hash_password, verify_password

# Hash password
hashed = hash_password("user_password")

# Verify
is_valid = verify_password("user_password", hashed)
```

### Password Strength Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character

## API Endpoints

### Register
```
POST /api/v1/auth/register
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
}

Response:
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "user_id": "...",
        "name": "John Doe",
        "email": "john@example.com",
        "role": "user",
        "is_active": true,
        "created_at": "..."
    }
}
```

### Login
```
POST /api/v1/auth/login
{
    "email": "john@example.com",
    "password": "SecurePass123!"
}

Response:
{
    "success": true,
    "message": "Login successful",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "Bearer"
    }
}
```

### Get Current User
```
GET /api/v1/auth/me
Header: Authorization: Bearer {access_token}

Response:
{
    "success": true,
    "message": "Current user retrieved successfully",
    "data": {
        "user_id": "...",
        "name": "John Doe",
        "email": "john@example.com",
        "role": "user",
        "is_active": true,
        "created_at": "..."
    }
}
```

### Refresh Tokens
```
POST /api/v1/auth/refresh
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
    "success": true,
    "message": "Token refreshed successfully",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "Bearer"
    }
}
```

### Logout
```
POST /api/v1/auth/logout

Response:
{
    "success": true,
    "message": "Logout successful",
    "data": {
        "message": "Discard access and refresh tokens on the client."
    }
}
```

## Protected Routes

Use `get_current_user` dependency:

```python
from fastapi import Depends
from app.auth.dependencies import get_current_user
from app.models.user import User

@app.get("/api/v1/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.name}"}
```

## Security Headers

- `WWW-Authenticate: Bearer` on 401 responses
- `Authorization: Bearer {token}` required for protected endpoints

## Testing Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Get current user (replace TOKEN)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"

# Refresh token (replace REFRESH_TOKEN)
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "REFRESH_TOKEN"}'
```

## Error Responses

### Invalid credentials
```
401 Unauthorized
{
    "success": false,
    "message": "Invalid email or password.",
    "request_id": "..."
}
```

### Duplicate email
```
409 Conflict
{
    "success": false,
    "message": "A user with this email already exists.",
    "request_id": "..."
}
```

### Invalid token
```
401 Unauthorized
{
    "success": false,
    "message": "Invalid or expired access token.",
    "request_id": "..."
}
```

## Configuration

In `.env`:
```
JWT_SECRET=your-secure-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Logging

All auth events logged with request_id:
- Registration success/failure
- Login success/failure
- Token refresh success/failure
- Invalid credentials attempts
- Security events

## Production Checklist

- [ ] JWT_SECRET generated and stored securely
- [ ] HTTPS enabled (redirects HTTP to HTTPS)
- [ ] CORS origins restricted to your domain
- [ ] Rate limiting enabled on auth endpoints
- [ ] Auth logs monitored for suspicious activity
- [ ] Token expiration times appropriate for use case
- [ ] Password requirements meet security standards
