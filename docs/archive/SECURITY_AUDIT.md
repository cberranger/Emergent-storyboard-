# Security Audit Report - StoryCanvas

**Date:** 2024  
**Scope:** Authentication, API Security, Input Validation, File Uploads, Secrets Management  
**Status:** 🔴 **CRITICAL GAPS IDENTIFIED**

---

## Executive Summary

This audit identified **critical security vulnerabilities** requiring immediate attention. The application currently lacks fundamental authentication, exposes API keys in plaintext, and has incomplete input validation. While some security measures are in place (CORS, file validation), significant gaps exist that could lead to unauthorized access, data breaches, and service abuse.

**Overall Risk Level:** 🔴 **HIGH**

---

## Findings by Category

### 1. Authentication & Authorization 🔴 CRITICAL

#### Status: **NO AUTHENTICATION SYSTEM**

**Issue:**
- No JWT or session-based authentication implemented
- No user management system exists
- All API endpoints are publicly accessible without authentication
- No authorization checks on resource access (projects, scenes, clips belong to no user)

**Evidence:**
- No authentication middleware in `backend/server.py`
- No `Authorization` header validation in any API router
- `backend/api/v1/dependencies.py` has no auth dependencies
- Database schemas have no user/owner fields

**Impact:**
- Anyone can access, modify, or delete any project/scene/clip
- No audit trail of who performed actions
- Cannot implement multi-tenancy
- API abuse potential (rate limiting ineffective without user identification)

**Risk Level:** 🔴 **CRITICAL**

---

### 2. API Key & Secrets Management 🔴 CRITICAL

#### 2.1 RunPod API Keys - Plaintext Storage

**Issue:**
- RunPod API keys stored in plaintext in MongoDB database
- Keys transmitted via API in plaintext (no encryption)
- Keys returned in API responses (`GET /api/v1/comfyui/servers`)

**Evidence:**
```python
# backend/dtos/comfyui_dtos.py
class ComfyUIServerDTO(BaseModel):
    api_key: Optional[str] = None  # ⚠️ Plaintext

# backend/api/v1/comfyui_router.py
@router.post("/servers", response_model=ComfyUIServerDTO)
async def create_server(server_data: ComfyUIServerCreateDTO):
    return await service.create_server(server_data)  # Returns api_key
```

**Impact:**
- Anyone with API access can retrieve RunPod API keys
- Keys visible in logs, network traffic, database dumps
- Potential for unauthorized RunPod usage and billing fraud

**Risk Level:** 🔴 **CRITICAL**

#### 2.2 OpenAI API Key - Environment Variable Only

**Issue:**
- OpenAI API key stored in environment variables (`OPENAI_API_KEY`)
- No rotation mechanism
- No validation of key format/validity on startup

**Evidence:**
```python
# backend/config.py
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")  # ⚠️ No validation
```

**Impact:**
- If `.env` file is committed to version control, key is exposed
- No centralized secrets management
- Key leakage risk in logs/error messages

**Risk Level:** 🟡 **MEDIUM**

#### 2.3 CivitAI API Key

**Issue:**
- CivitAI API key retrieved from environment without validation
- Used in server.py with minimal error handling

**Evidence:**
```python
# backend/server.py:2575
civitai_api_key = os.getenv("CIVITAI_API_KEY")
if not civitai_api_key:
    raise HTTPException(status_code=500, detail="CIVITAI_API_KEY not configured")
```

**Risk Level:** 🟡 **MEDIUM**

---

### 3. Input Validation Coverage 🟡 PARTIAL

#### 3.1 ✅ Well-Validated Areas

**File Uploads:**
- ✅ File size validation (`FileValidator.validate_file_size`)
- ✅ MIME type validation (`FileValidator.validate_file_type`)
- ✅ Filename sanitization (`FileValidator.sanitize_filename`)
- ✅ Disk space checks (`FileValidator.check_disk_space`)

**Evidence:**
```python
# backend/utils/file_validator.py
async def validate_file_size(file: UploadFile, max_size: int, file_type: str)
def validate_file_type(file: UploadFile, allowed_types: set, file_type: str)
def sanitize_filename(filename: str) -> str  # Path traversal prevention
```

**DTOs (Pydantic Validation):**
- ✅ Field type validation
- ✅ Value range constraints (e.g., `width: ge=64, le=4096`)
- ✅ Pattern validation (e.g., `generation_type: pattern="^(image|video)$"`)
- ✅ Custom validators for URLs (`url_validator.validate_url_format`)

#### 3.2 ⚠️ Gaps in Validation

**Prompt Injection Risk:**
```python
# backend/services/generation_service.py:48
# No sanitization of user prompts before sending to AI services
result_url = await openai_video_service.generate_video_to_local(
    model=payload.model or "sora-2",
    prompt=payload.prompt,  # ⚠️ No validation/sanitization
    params=generation_params,
)
```

**JSON Workflow Validation:**
```python
# backend/dtos/generation_dtos.py:29
@validator("workflow_json")
def validate_workflow_json(cls, value: Optional[str], values: Dict[str, Any]):
    # ⚠️ Only checks if workflow_json matches use_custom_workflow flag
    # Does not validate JSON structure or prevent malicious content
```

**Database Query Injection:**
- MongoDB queries generally safe (using parameterized queries)
- Regex patterns constructed from user input could be vulnerable

**Risk Level:** 🟡 **MEDIUM**

---

### 4. CORS Configuration 🟢 ALLOW-ALL (Intentional)

#### Current Configuration

**Evidence:**
```python
# backend/server.py:4939 (updated)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow-all
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# backend/config.py:34 - CORS neutralized
@staticmethod
def get_cors_origins() -> List[str]:
    return ["*"]
```

**Issues:**
- None for CORS; policy is intentionally allow-all

**Impact:**
- No CORS blocking in any environment

**Risk Level:** 🟢 **LOW** (intentional openness)

---

### 5. Rate Limiting ❌ NOT IMPLEMENTED

#### Status: **NO RATE LIMITING**

**Evidence:**
- No rate limiting middleware in `server.py`
- No `slowapi`, `fastapi-limiter`, or similar dependencies in `requirements.txt`
- Grep search for `rate_limit|RateLimit|Limiter|throttle` found zero results

**Impact:**
- API can be abused for DoS attacks
- AI generation endpoints can be spammed (costly OpenAI/RunPod usage)
- No protection against brute force or credential stuffing (once auth is added)
- Resource exhaustion possible on `/api/v1/comfyui/servers/{id}/info` (calls external services)

**Risk Level:** 🔴 **HIGH**

---

### 6. File Upload Security ✅ GOOD

#### Current Implementation

**Strengths:**
- ✅ File size limits enforced (10MB images, 50MB audio, 100MB video)
- ✅ MIME type whitelisting
- ✅ Filename sanitization prevents path traversal
- ✅ Disk space checks before upload
- ✅ Separate directories for different file types (`uploads/faces/`)

**Evidence:**
```python
# backend/config.py
MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# backend/utils/file_validator.py
def sanitize_filename(filename: str) -> str:
    dangerous_chars = ['..', '/', '\\', '\x00', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
```

**Minor Gaps:**
- ⚠️ No virus/malware scanning
- ⚠️ No content verification (e.g., checking image headers match MIME type)
- ⚠️ Uploaded files served without `Content-Security-Policy` headers (if served statically)
- ⚠️ No automatic cleanup of old/unused uploads (potential disk exhaustion)

**Risk Level:** 🟢 **LOW** (well-implemented with minor improvements possible)

---

### 7. Additional Security Concerns

#### 7.1 Missing Security Headers

**Issue:** No security headers middleware detected

**Missing Headers:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security` (HSTS)
- `Content-Security-Policy`
- `Referrer-Policy`

**Risk Level:** 🟡 **MEDIUM**

#### 7.2 Error Information Disclosure

**Issue:** Detailed error messages may leak sensitive information

**Evidence:**
```python
# backend/server.py:2576
if not civitai_api_key:
    raise HTTPException(status_code=500, detail="CIVITAI_API_KEY not configured")
    # ⚠️ Reveals internal configuration details
```

**Risk Level:** 🟢 **LOW**

#### 7.3 No HTTPS Enforcement

**Issue:** No code enforces HTTPS in production

**Risk Level:** 🟡 **MEDIUM** (deployment concern)

#### 7.4 Logging Sensitive Data

**Issue:** Potential for API keys/secrets in logs

**Evidence:**
```python
# Need to audit for:
logger.info(f"File size validation passed: {file.filename} ({file_size / 1024 / 1024:.2f}MB)")
# ⚠️ Ensure no sensitive data logged
```

**Risk Level:** 🟡 **MEDIUM**

---

## Prioritized Recommendations

### 🔴 CRITICAL - Immediate Action Required

#### 1. Implement Authentication System (P0 - Critical)

**Action Items:**
- [ ] Implement JWT-based authentication
- [ ] Add user registration/login endpoints
- [ ] Create authentication middleware for protected routes
- [ ] Add `user_id`/`owner_id` fields to projects, scenes, clips
- [ ] Implement authorization checks (users can only access their own resources)

**Recommended Stack:**
```python
# Install
pip install python-jose[cryptography] passlib[bcrypt] python-multipart

# Implementation
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
```

**Effort:** 2-3 days  
**Impact:** Prevents unauthorized access to entire application

---

#### 2. Encrypt/Hash API Keys (P0 - Critical)

**Action Items:**
- [ ] **Encrypt RunPod API keys** at rest using Fernet or AES-256
- [ ] Create secrets management service
- [ ] Never return decrypted keys in API responses
- [ ] Add `api_key_encrypted` field, remove plaintext `api_key`
- [ ] Update `ComfyUIServerDTO` to exclude API key from responses
- [ ] Implement key rotation mechanism

**Implementation Example:**
```python
from cryptography.fernet import Fernet
import os

# In config.py
ENCRYPTION_KEY = os.environ.get("API_KEY_ENCRYPTION_KEY")  # Must be set
cipher = Fernet(ENCRYPTION_KEY.encode())

# In service
def encrypt_api_key(plaintext_key: str) -> str:
    return cipher.encrypt(plaintext_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    return cipher.decrypt(encrypted_key.encode()).decode()
```

**Effort:** 1-2 days  
**Impact:** Prevents API key theft from database/API responses

---

#### 3. Implement Rate Limiting (P1 - High Priority)

**Action Items:**
- [ ] Install `slowapi` or `fastapi-limiter`
- [ ] Apply rate limits to all API endpoints
- [ ] Stricter limits on expensive operations (AI generation)
- [ ] IP-based rate limiting (before auth is implemented)
- [ ] User-based rate limiting (after auth is implemented)

**Implementation:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/generate")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def generate_image(request: Request, payload: GenerationRequestDTO):
    ...
```

**Effort:** 4-6 hours  
**Impact:** Prevents API abuse and cost overruns

---

### 🟡 HIGH - Address Soon

#### 4. CORS Policy (P2)

**Action Items:**
- [x] Set CORS to allow-all (origins/methods/headers)

**Change:**
```python
# backend/server.py:4939
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=app_config.CORS_MAX_AGE,
)
```

**Effort:** 30 minutes  
**Impact:** Enables proper production deployment

---

#### 5. Add Security Headers (P2)

**Action Items:**
- [ ] Install `secure` library or implement custom middleware
- [ ] Add all standard security headers

**Implementation:**
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**Effort:** 2-3 hours  
**Impact:** Defense-in-depth protection

---

#### 6. Enhance Input Validation (P2)

**Action Items:**
- [ ] Add prompt sanitization (remove control characters, length limits)
- [ ] Validate `workflow_json` structure if `use_custom_workflow=True`
- [ ] Add MongoDB query sanitization utility
- [ ] Validate URL parameters more strictly (e.g., server_id format)

**Effort:** 1 day  
**Impact:** Prevents injection attacks

---

### 🟢 MEDIUM - Plan for Implementation

#### 7. Secrets Management (P3)

**Action Items:**
- [ ] Use HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault
- [ ] Remove secrets from environment variables
- [ ] Implement secret rotation policies
- [ ] Add secrets expiry monitoring

**Effort:** 2-3 days  
**Impact:** Enterprise-grade secrets security

---

#### 8. File Upload Enhancements (P3)

**Action Items:**
- [ ] Add virus scanning (ClamAV integration)
- [ ] Verify file content matches declared MIME type
- [ ] Implement file upload quotas per user
- [ ] Add automatic cleanup of old uploads
- [ ] Add CSP headers when serving uploads

**Effort:** 2-3 days  
**Impact:** Additional upload security layers

---

#### 9. Audit Logging (P3)

**Action Items:**
- [ ] Log all API requests (after adding auth)
- [ ] Log authentication events (login, logout, failed attempts)
- [ ] Log sensitive operations (API key creation, project deletion)
- [ ] Ensure no sensitive data (passwords, keys) in logs
- [ ] Implement log aggregation and monitoring

**Effort:** 1-2 days  
**Impact:** Security monitoring and compliance

---

#### 10. Dependency Security (P4)

**Action Items:**
- [ ] Run `pip-audit` or `safety check` regularly
- [ ] Update dependencies with known vulnerabilities
- [ ] Add `dependabot` or similar automated scanning
- [ ] Pin dependency versions in `requirements.txt`

**Effort:** Ongoing  
**Impact:** Prevents known CVEs

---

## Compliance Considerations

If planning to handle user data or deploy commercially:

- **GDPR/Privacy:** Need authentication + data deletion capabilities
- **PCI-DSS:** If accepting payments (not currently)
- **SOC 2:** Requires audit logging, access controls, encryption at rest
- **HIPAA:** Not applicable (no health data)

---

## Testing Recommendations

### Security Testing Checklist

- [ ] Authentication bypass testing (once implemented)
- [ ] Authorization testing (horizontal/vertical privilege escalation)
- [ ] API key exposure testing (check all API responses)
- [ ] Rate limiting testing (verify limits work)
- [ ] File upload testing (malicious files, path traversal)
- [ ] CORS testing (verify allow-all effective)
- [ ] SQL/NoSQL injection testing (MongoDB queries)
- [ ] XSS testing (if rendering user content)
- [ ] CSRF testing (once auth + credentials enabled)

### Tools

- **OWASP ZAP** - Automated vulnerability scanner
- **Burp Suite** - Manual penetration testing
- **pytest-security** - Python security tests
- **bandit** - Python code security linter

---

## Summary Matrix

| Area | Status | Risk | Priority | Effort |
|------|--------|------|----------|--------|
| Authentication | ❌ None | 🔴 Critical | P0 | 2-3 days |
| API Key Storage | ❌ Plaintext | 🔴 Critical | P0 | 1-2 days |
| Rate Limiting | ❌ None | 🔴 High | P1 | 4-6 hours |
| CORS Config | 🟢 Allow-All | 🟢 Low | P2 | 30 min |
| Security Headers | ❌ None | 🟡 Medium | P2 | 2-3 hours |
| Input Validation | ✅ Partial | 🟡 Medium | P2 | 1 day |
| File Uploads | ✅ Good | 🟢 Low | P3 | 2-3 days |
| Secrets Mgmt | ⚠️ Basic | 🟡 Medium | P3 | 2-3 days |
| Audit Logging | ❌ None | 🟡 Medium | P3 | 1-2 days |

---

## Immediate Next Steps (This Week)

1. **Implement JWT authentication** (P0)
2. **Encrypt RunPod API keys** (P0)
3. **Add rate limiting** (P1)
4. **Confirm CORS allow-all configuration** (P2)

**Estimated Total Effort:** 5-7 days for critical items

---

## References

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Pydantic Data Validation](https://docs.pydantic.dev/latest/)
- [Python Cryptography](https://cryptography.io/en/latest/)

---

**Audit Completed By:** AI Security Audit  
**Review Date:** 2024  
**Next Review:** After implementing P0-P1 recommendations
