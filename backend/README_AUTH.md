# JWT Authentication System

This backend now includes a complete JWT authentication system with optional authorization for all endpoints.

## Features

- User registration and login
- JWT access tokens (60 min expiry) and refresh tokens (30 day expiry)
- Secure password hashing with bcrypt
- Per-user API key storage (RunPod, OpenAI, Civitai)
- Optional authentication on all endpoints (graceful degradation)
- CORS configured to handle Authorization headers

## Environment Variables

Add to your `.env` file:

```bash
JWT_SECRET_KEY=your-secret-key-here-change-in-production
```

**IMPORTANT**: Generate a secure secret key for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## API Endpoints

### Authentication

**POST /api/v1/auth/register**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**POST /api/v1/auth/login**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**POST /api/v1/auth/refresh**
```json
{
  "refresh_token": "eyJ..."
}
```

**GET /api/v1/auth/me**
Headers: `Authorization: Bearer <access_token>`

**PUT /api/v1/auth/me/api-keys**
Headers: `Authorization: Bearer <access_token>`
```json
{
  "runpod": "optional-runpod-key",
  "openai": "optional-openai-key",
  "civitai": "optional-civitai-key"
}
```

## Using Authentication

### Frontend Integration

```javascript
// Login
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { access_token, refresh_token } = await response.json();

// Store tokens
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);

// Make authenticated requests
const res = await fetch('/api/v1/projects', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

// Refresh expired token
const refreshRes = await fetch('/api/v1/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh_token })
});
const { access_token: new_token } = await refreshRes.json();
```

### Graceful Degradation

All existing endpoints support **optional** authentication:
- If no `Authorization` header is provided, endpoints work as before
- If a valid token is provided, user context is available
- If an invalid token is provided, it's silently ignored (no 401 error)

This allows existing frontends to work without changes while enabling new authenticated features.

## Database

New collection: `users`

Schema:
```javascript
{
  id: string,
  email: string,  // lowercase, unique
  username: string,  // lowercase, unique
  hashed_password: string,
  api_keys: {
    runpod: string | null,
    openai: string | null,
    civitai: string | null
  },
  is_active: boolean,
  created_at: datetime,
  updated_at: datetime
}
```

## Security Notes

1. Passwords are hashed with bcrypt before storage
2. JWT tokens are signed with HS256
3. Access tokens expire after 60 minutes
4. Refresh tokens expire after 30 days
5. API keys are stored in plaintext per-user (consider encryption for production)
6. CORS headers include Authorization support
7. All auth endpoints use HTTPS in production

## Testing

Run auth tests:
```bash
.venv\Scripts\python -m pytest test_auth.py -v
```

## Migration Notes

- No changes required to existing code
- All endpoints continue to work without authentication
- To require authentication on specific endpoints, replace `get_current_user_optional` with `get_current_user` in the endpoint dependency
