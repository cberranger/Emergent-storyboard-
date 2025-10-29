# Error Handling and Validation Audit Report

## Executive Summary

This audit reviews error handling and validation across the backend codebase. Overall, the system has a **solid foundation** with standardized error classes, comprehensive DTO validation, and security-focused validators. However, several gaps and inconsistencies were identified that should be addressed.

---

## 1. Standardized Error Classes (utils/errors.py)

### ✅ Strengths

1. **Well-structured error hierarchy** - All errors extend `APIError` with consistent formatting
2. **Comprehensive HTTP status coverage** - 400, 404, 409, 413, 422, 500, 503, 507 status codes
3. **Detailed error information** - Error codes, status codes, and context details
4. **Logging integration** - All errors automatically logged with context
5. **Helper functions** - `handle_db_error()` and `require_resource()` for common patterns

### ⚠️ Issues Found

1. **Duplicate class definitions**:
   - `ConflictError` defined twice (lines 59 and 101)
   - `ServiceUnavailableError` defined twice (lines 98 and 133)
   - `ServerError` defined once but `InternalServerError` serves similar purpose

2. **Inconsistent naming**:
   - `ServerError` vs `InternalServerError` (both for 500 errors)
   - Both are used but serve similar purposes

3. **Missing error types**:
   - No `UnauthorizedError` (401) - will be needed when auth is implemented
   - No `ForbiddenError` (403) - for permission-based access control
   - No `RateLimitError` (429) - for API rate limiting
   - No `BadGatewayError` (502) - for upstream service failures
   - No `GatewayTimeoutError` (504) - for timeout scenarios

### 📋 Recommendations

```python
# Remove duplicate definitions
# Keep ConflictError at line 101, remove line 59
# Keep ServiceUnavailableError at line 133, remove line 98

# Add missing error classes:
class UnauthorizedError(APIError):
    """Authentication required or failed"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, "UNAUTHORIZED")

class ForbiddenError(APIError):
    """Insufficient permissions"""
    def __init__(self, resource: str, action: str):
        message = f"Insufficient permissions to {action} {resource}"
        super().__init__(status.HTTP_403_FORBIDDEN, message, "FORBIDDEN")

class RateLimitError(APIError):
    """Rate limit exceeded"""
    def __init__(self, retry_after: Optional[int] = None):
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, message, "RATE_LIMIT_EXCEEDED")
```

---

## 2. DTO Validation Coverage

### ✅ Comprehensive Field Validation

All DTOs use Pydantic with proper constraints:

| DTO Category | Validation Coverage | Notes |
|-------------|-------------------|-------|
| **Project DTOs** | ✅ Excellent | min_length, max_length, ge constraints |
| **Scene DTOs** | ✅ Excellent | Field length limits, order validation |
| **Clip DTOs** | ✅ Excellent | Length/position validation, URL security checks |
| **Generation DTOs** | ✅ Good | Dimension limits (64-4096), steps (1-200), cfg (0.1-30) |
| **ComfyUI DTOs** | ✅ Good | HttpUrl validation, server type pattern |
| **Character DTOs** | ✅ Good | String length limits |
| **Template DTOs** | ✅ Good | Field constraints |
| **Queue DTOs** | ✅ Good | Pattern validation for generation types |
| **Media DTOs** | ✅ Good | Basic structure |

### ⚠️ Validation Gaps

#### 2.1 Generation Parameters (generation_dtos.py)

```python
# Current:
width: Optional[int] = Field(default=None, ge=64, le=4096)
height: Optional[int] = Field(default=None, ge=64, le=4096)

# Issues:
# - No aspect ratio validation
# - No check for common resolutions (512, 768, 1024, etc.)
# - video_fps allows 1-120 but extreme values may cause issues
# - No validation that steps * cfg is reasonable
```

**Recommendation**: Add custom validator for dimension compatibility:

```python
@validator('width', 'height')
def validate_dimensions(cls, v):
    if v and v % 8 != 0:
        raise ValueError('Dimensions must be divisible by 8')
    return v

@validator('video_fps')
def validate_fps(cls, v):
    if v and v not in [24, 25, 30, 60, 120]:
        logger.warning(f"Unusual FPS value: {v}")
    return v
```

#### 2.2 Character DTOs (character_dtos.py)

```python
# Current:
reference_images: List[str] = Field(default_factory=list)

# Issues:
# - No validation that URLs/paths are valid
# - No limit on number of reference images
# - No validation of image URLs for security
```

**Recommendation**: Add validators:

```python
@validator('reference_images')
def validate_reference_images(cls, v):
    if len(v) > 10:  # Reasonable limit
        raise ValueError('Maximum 10 reference images allowed')
    
    from utils.url_validator import url_validator
    for url in v:
        url_validator.validate_image_url(url)
    return v
```

#### 2.3 ComfyUI Server URL (comfyui_dtos.py)

```python
# Current validation:
url: HttpUrl  # Pydantic's HttpUrl validator

@validator("url")
def strip_trailing_slash(cls, value: HttpUrl) -> HttpUrl:
    return HttpUrl(str(value).rstrip("/"))

# Issues:
# - No validation of localhost/private IP addresses in production
# - No validation of port ranges
# - No SSRF protection
```

**Recommendation**: Add SSRF protection:

```python
@validator("url")
def validate_url_security(cls, value: HttpUrl) -> HttpUrl:
    from urllib.parse import urlparse
    import os
    
    parsed = urlparse(str(value))
    
    # In production, block private IPs unless explicitly allowed
    if os.environ.get('ENVIRONMENT') == 'production':
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            raise ValueError("Localhost URLs not allowed in production")
        # Add IP range checks for private networks
    
    return HttpUrl(str(value).rstrip("/"))
```

#### 2.4 Queue DTOs (queue_dtos.py)

```python
# Current:
priority: int = 0
params: Optional[Dict[str, Any]] = None

# Issues:
# - No bounds on priority (could be negative or extremely large)
# - No validation of params structure
```

**Recommendation**:

```python
priority: int = Field(default=0, ge=-10, le=10)
```

#### 2.5 Batch Generation (generation_dtos.py)

```python
# Current:
clip_ids: List[str] = Field(..., min_items=1)

# Issues:
# - No maximum limit (could cause DoS with thousands of clips)
# - No validation that clip IDs are valid UUIDs
```

**Recommendation**:

```python
clip_ids: List[str] = Field(..., min_items=1, max_items=100)

@validator('clip_ids')
def validate_clip_ids(cls, v):
    from uuid import UUID
    for clip_id in v:
        try:
            UUID(clip_id)
        except ValueError:
            raise ValueError(f"Invalid clip ID format: {clip_id}")
    return v
```

### 🔍 Missing Business Logic Validation in DTOs

#### Project/Scene/Clip Names
- Allow empty strings in some places despite min_length=1
- No validation for special characters that might break filesystem operations
- No uniqueness checks (should be in service layer, documented below)

#### Prompt Validation
```python
# No validation currently for:
# - Extremely long prompts (>5000 chars might cause model issues)
# - Invalid/dangerous content
# - Encoding issues
```

---

## 3. File Validator Implementation (utils/file_validator.py)

### ✅ Strengths

1. **Memory-efficient validation** - Reads files in 1MB chunks
2. **Size limits enforced** - MAX_MUSIC_SIZE (50MB), MAX_IMAGE_SIZE (10MB), MAX_VIDEO_SIZE (100MB)
3. **MIME type validation** - Checks against allowed types
4. **Disk space checks** - Prevents uploads when disk is full
5. **Filename sanitization** - Removes path traversal and dangerous characters
6. **Specialized validators** - Separate methods for music, image, video files

### ⚠️ Issues Found

#### 3.1 MIME Type Spoofing Vulnerability

```python
# Current:
def validate_file_type(file: UploadFile, allowed_types: set, file_type: str) -> None:
    if file.content_type not in allowed_types:
        raise HTTPException(...)

# Issue: Relies on client-provided content_type header
# An attacker can set content_type to "image/jpeg" for a malicious file
```

**Recommendation**: Add magic byte validation:

```python
import magic  # python-magic library

@staticmethod
async def validate_file_content(file: UploadFile, file_type: str) -> None:
    """Validate actual file content, not just MIME type"""
    await file.seek(0)
    header = await file.read(2048)
    await file.seek(0)
    
    detected_type = magic.from_buffer(header, mime=True)
    
    allowed_map = {
        'image': {'image/jpeg', 'image/png', 'image/webp', 'image/gif'},
        'video': {'video/mp4', 'video/webm', 'video/quicktime'},
        'music': {'audio/mpeg', 'audio/wav', 'audio/ogg'}
    }
    
    if detected_type not in allowed_map.get(file_type, set()):
        raise HTTPException(
            status_code=400,
            detail=f"File content does not match declared type"
        )
```

#### 3.2 Filename Sanitization Edge Cases

```python
# Current:
dangerous_chars = ['..', '/', '\\', '\x00', '<', '>', ':', '"', '|', '?', '*']
for char in dangerous_chars:
    filename = filename.replace(char, '_')

# Issues:
# - Unicode normalization attacks not handled
# - Reserved filenames not checked (CON, PRN, AUX on Windows)
# - Multiple extensions not validated (file.jpg.exe)
```

**Recommendation**:

```python
import unicodedata
import os

@staticmethod
def sanitize_filename(filename: str) -> str:
    # Normalize unicode
    filename = unicodedata.normalize('NFKD', filename)
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    
    # Remove path components
    filename = Path(filename).name
    
    # Check for reserved names (Windows)
    reserved = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                'LPT1', 'LPT2', 'LPT3'}
    name_without_ext = filename.rsplit('.', 1)[0].upper()
    if name_without_ext in reserved:
        filename = f'file_{filename}'
    
    # Remove dangerous characters
    dangerous_chars = ['..', '/', '\\', '\x00', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Ensure single extension
    parts = filename.split('.')
    if len(parts) > 2:
        filename = '_'.join(parts[:-1]) + '.' + parts[-1]
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1)
        filename = name[:250] + '.' + ext
    
    return filename or 'unnamed_file'
```

#### 3.3 Disk Space Check Race Condition

```python
# Current:
stat = shutil.disk_usage(path)
available_bytes = stat.free
if available_bytes < required_bytes:
    return False, ...

# Issue: Between check and file write, disk space could be consumed
# by other processes (TOCTOU - Time of Check, Time of Use)
```

**Recommendation**: Wrap file write in try-except to handle actual disk full errors:

```python
try:
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
except OSError as e:
    if e.errno == errno.ENOSPC:
        raise InsufficientStorageError(...)
    raise
```

#### 3.4 No File Content Scanning

- No antivirus/malware scanning
- No image dimension validation (e.g., decompression bomb protection)
- No video codec validation

**Recommendation**: Add basic image bomb protection:

```python
from PIL import Image

@staticmethod
async def validate_image_dimensions(file: UploadFile) -> None:
    """Prevent decompression bombs"""
    await file.seek(0)
    try:
        img = Image.open(file.file)
        width, height = img.size
        
        # Limit total pixels to prevent memory exhaustion
        max_pixels = 89_478_485  # 8192x8192 + margin
        if width * height > max_pixels:
            raise HTTPException(
                status_code=400,
                detail=f"Image dimensions too large: {width}x{height}"
            )
    finally:
        await file.seek(0)
```

---

## 4. URL Validation Security (utils/url_validator.py)

### ✅ Strengths

1. **Path traversal protection** - Multiple pattern checks including URL encoded variants
2. **Scheme validation** - Only http, https, file allowed
3. **Filename sanitization** - Removes dangerous characters
4. **Separate validators** - For image URLs and video URLs
5. **Logging** - All validations logged for audit trail

### ⚠️ Security Issues

#### 4.1 SSRF (Server-Side Request Forgery) Vulnerability

```python
# Current:
ALLOWED_SCHEMES = {'http', 'https', 'file'}

# Issues:
# - 'file' scheme allows reading arbitrary local files
# - No IP address validation (can target internal services)
# - No port validation (can scan internal ports)
# - No domain whitelist
```

**Critical Fix Required**:

```python
import ipaddress
from urllib.parse import urlparse

ALLOWED_SCHEMES = {'http', 'https'}  # Remove 'file'

@staticmethod
def check_ssrf(url: str) -> Tuple[bool, str]:
    """Check for SSRF attacks"""
    try:
        parsed = urlparse(url)
        
        # Block file:// URLs
        if parsed.scheme == 'file':
            return False, "File URLs not allowed"
        
        # Check hostname
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid hostname"
        
        # Block localhost
        if hostname.lower() in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False, "Localhost URLs not allowed"
        
        # Try to resolve and check for private IPs
        try:
            import socket
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)
            
            # Block private networks
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return False, f"Private IP addresses not allowed: {ip}"
        except socket.gaierror:
            pass  # Allow if DNS fails - will fail on actual request
        
        # Block non-standard ports (optional, based on requirements)
        if parsed.port and parsed.port not in [80, 443, 8001]:
            return False, f"Port {parsed.port} not allowed"
        
        return True, "URL is safe"
        
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"
```

#### 4.2 Path Traversal Detection Incomplete

```python
# Current patterns:
PATH_TRAVERSAL_PATTERNS = [
    r'\.\./',  # ../
    r'\.\.',   # ..
    r'%2e%2e', # URL encoded ..
    r'%252e',  # Double URL encoded .
    r'\.\.\\', # ..\ (Windows)
]

# Missing:
# - Triple encoding (%25252e)
# - Unicode variations (．．)
# - Null byte injection (%00)
```

**Recommendation**:

```python
PATH_TRAVERSAL_PATTERNS = [
    r'\.\./',
    r'\.\.',
    r'%2e%2e',
    r'%252e',
    r'%25252e',  # Triple encoded
    r'\.\.',
    r'\.\.\\',
    r'%00',  # Null byte
    r'%2f\.\.%2f',  # Encoded ../
]

@staticmethod
def check_path_traversal(url: str) -> Tuple[bool, str]:
    # Decode multiple times to catch nested encoding
    decoded_url = url
    for _ in range(5):  # Max 5 levels of encoding
        prev = decoded_url
        decoded_url = unquote(decoded_url)
        if prev == decoded_url:
            break
    
    # Check all patterns
    for pattern in URLValidator.PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, decoded_url, re.IGNORECASE):
            return False, "Potential path traversal detected"
    
    return True, "URL is safe"
```

#### 4.3 Relative Path Handling

```python
# Current:
if not parsed.scheme and not url.startswith('/'):
    return False, "URL must have a valid scheme or be a relative path"

# Issue: Relative paths should be normalized to prevent directory traversal
```

**Recommendation**:

```python
@staticmethod
def normalize_relative_path(url: str) -> str:
    """Normalize relative paths to prevent traversal"""
    if url.startswith('/'):
        from pathlib import Path
        normalized = Path(url).resolve()
        # Ensure stays within uploads directory
        uploads_dir = Path('uploads').resolve()
        if not str(normalized).startswith(str(uploads_dir)):
            raise HTTPException(400, "Invalid path")
        return str(normalized)
    return url
```

#### 4.4 No Content-Type Validation

When URLs are fetched, there's no validation that the response is actually an image/video:

```python
# Add to validate_image_url and validate_video_url:
@staticmethod
async def validate_url_content_type(url: str, expected_types: set) -> None:
    """Verify URL returns expected content type"""
    async with aiohttp.ClientSession() as session:
        async with session.head(url, timeout=5) as response:
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            if content_type not in expected_types:
                raise HTTPException(
                    400, 
                    f"URL content type {content_type} not in {expected_types}"
                )
```

---

## 5. Business Logic Validation Gaps

### 5.1 Service Layer Validation (services/project_service.py)

#### ✅ Good Practices Found:
- Existence checks before operations (`if not project: raise ProjectNotFoundError`)
- Timeline overlap validation using `timeline_validator`
- Consistent use of standardized errors

#### ⚠️ Missing Validations:

##### 5.1.1 No Duplicate Name Checks

```python
# Current:
async def create_project(self, payload: ProjectCreateDTO) -> ProjectResponseDTO:
    dto = ProjectResponseDTO(...)
    await self._projects.create(dto.model_dump())
    return dto

# Issue: Can create multiple projects with same name
```

**Recommendation**:

```python
async def create_project(self, payload: ProjectCreateDTO) -> ProjectResponseDTO:
    # Check for duplicate name
    existing = await self._projects.find_by_name(payload.name)
    if existing:
        raise DuplicateResourceError("Project", payload.name)
    
    dto = ProjectResponseDTO(...)
    await self._projects.create(dto.model_dump())
    return dto
```

##### 5.1.2 No Cascade Delete Validation

```python
# Current delete_project has no checks for:
# - Active generation jobs
# - Exported content references
# - Queue items
```

**Recommendation**:

```python
async def delete_project(self, project_id: str):
    # Check for active jobs
    active_jobs = await self._check_active_jobs(project_id)
    if active_jobs:
        raise ConflictError(
            "Cannot delete project with active generation jobs",
            {"active_jobs": active_jobs}
        )
    
    # Warn about data loss
    scenes_count = await self._scenes.count_by_project(project_id)
    if scenes_count > 0:
        logger.warning(f"Deleting project {project_id} with {scenes_count} scenes")
    
    await self._projects.delete(project_id)
```

##### 5.1.3 No Clip Length Validation

```python
# In update_clip_timeline_position:
# - No check if new position + length exceeds music duration
# - No validation of negative lengths
# - No check for extremely long clips (>10 minutes)
```

**Recommendation**:

```python
async def update_clip(self, clip_id: str, clip_data: ClipUpdateDTO):
    if clip_data.length is not None:
        if clip_data.length <= 0:
            raise ValidationError("Clip length must be positive")
        if clip_data.length > 600:  # 10 minutes
            raise ValidationError("Clip length exceeds maximum (600 seconds)")
    
    # existing code...
```

### 5.2 Generation Service Validation (services/generation_service.py)

#### ⚠️ Missing Validations:

##### 5.2.1 No Model Compatibility Checks

```python
# Current:
model_type = detect_model_type(payload.model or "unknown")

# Issues:
# - No validation that model type supports generation_type
# - No check if LoRAs are compatible with model
# - No validation of parameter ranges for specific models
```

**Recommendation**:

```python
async def generate(self, payload: GenerationRequestDTO):
    # Validate model compatibility
    if payload.generation_type == "video":
        video_models = {'sora', 'wan', 'svd', 'hidream'}
        if not any(m in payload.model.lower() for m in video_models):
            raise ValidationError(
                f"Model {payload.model} does not support video generation"
            )
    
    # existing code...
```

##### 5.2.2 No Queue Depth Limits

```python
# No check for:
# - Maximum queue size per server
# - Maximum pending jobs per user
# - Batch size limits enforced at service level
```

##### 5.2.3 No Resource Estimation

```python
# No validation of:
# - Estimated VRAM requirements
# - Estimated generation time
# - Server capacity before queuing
```

### 5.3 Media Service Validation (services/media_service.py)

#### ⚠️ Issues:

##### 5.3.1 No Audio Format Validation

```python
# Current: Only checks MIME type
# Missing:
# - Audio duration extraction (for music_duration field)
# - Sample rate validation
# - Bit rate validation
# - Corrupted file detection
```

**Recommendation**:

```python
from mutagen import File as MutagenFile

async def upload_music(self, project_id: str, file: UploadFile):
    # existing validation...
    
    # Extract and validate audio metadata
    try:
        audio = MutagenFile(file_path)
        if audio is None:
            raise ValidationError("Corrupted or invalid audio file")
        
        duration = audio.info.length
        if duration <= 0 or duration > 3600:  # Max 1 hour
            raise ValidationError(f"Invalid audio duration: {duration}s")
        
        updates['music_duration'] = duration
    except Exception as e:
        raise ValidationError(f"Failed to read audio metadata: {str(e)}")
    
    # existing code...
```

##### 5.3.2 No Image Validation in upload_face_image

```python
# Missing:
# - Face detection (should verify image contains a face)
# - Image dimension validation
# - Image corruption detection
```

### 5.4 Timeline Validator (utils/timeline_validator.py)

#### ✅ Good implementation overall

#### ⚠️ Minor improvements:

```python
# Add validation for scene boundaries:
@staticmethod
def validate_scene_capacity(clips: List[Any], max_duration: Optional[float] = None):
    """Check if scene duration exceeds music duration"""
    if not max_duration:
        return True, None
    
    timeline_end = max(
        c.timeline_position + c.length for c in clips
    ) if clips else 0
    
    if timeline_end > max_duration:
        return False, (
            f"Scene duration ({timeline_end:.2f}s) exceeds "
            f"project music duration ({max_duration:.2f}s)"
        )
    
    return True, None
```

---

## 6. Cross-Cutting Concerns

### 6.1 Error Handling Consistency

#### ⚠️ Inconsistent error usage:

```python
# Some places use ValueError:
backend/services/export_service.py:
    raise ValueError("Project not found")

# Should use:
    raise ProjectNotFoundError(project_id)

# Some places use generic exceptions:
backend/services/batch_generator.py:
    raise ValueError(f"Clip {clip_id} not found")

# Should use:
    raise ClipNotFoundError(clip_id)
```

### 6.2 Input Sanitization

- **Prompt injection**: No validation of user prompts for model-specific attack patterns
- **SQL injection**: N/A (using MongoDB, NoSQL injection unlikely with Motor)
- **XSS**: No HTML escaping (should be done in frontend, but defense-in-depth suggests backend validation)

### 6.3 Rate Limiting

**Missing entirely**:
- No rate limiting on API endpoints
- No protection against batch job spam
- No limits on file uploads per time period

**Recommendation**: Add rate limiting middleware:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/generate")
@limiter.limit("10/minute")  # 10 generations per minute
async def generate_content(...):
    ...
```

### 6.4 Logging and Monitoring

#### ✅ Good practices:
- Errors logged with context in error classes
- File operations logged in file_validator
- URL validation logged in url_validator

#### ⚠️ Missing:
- No structured logging (JSON format for parsing)
- No correlation IDs for request tracing
- No metrics/monitoring hooks
- No sensitive data masking in logs

---

## 7. Priority Recommendations

### 🔴 Critical (Fix Immediately)

1. **Remove duplicate error class definitions** in `utils/errors.py`
2. **Fix SSRF vulnerability** in `utils/url_validator.py` - remove 'file' scheme, add IP validation
3. **Add MIME type verification** in `utils/file_validator.py` using magic bytes
4. **Add batch size limits** in DTOs to prevent DoS

### 🟡 High Priority (Fix Soon)

5. **Add model compatibility validation** in `generation_service.py`
6. **Add duplicate name checks** in `project_service.py`
7. **Improve filename sanitization** with unicode normalization
8. **Add audio duration extraction** in `media_service.py`
9. **Standardize error usage** across all services

### 🟢 Medium Priority (Improvement)

10. **Add rate limiting** middleware
11. **Add face detection** to face image uploads
12. **Add dimension validation** for images
13. **Add scene capacity validation** to timeline validator
14. **Add resource estimation** before generation

### 🔵 Low Priority (Enhancement)

15. **Add structured logging** with correlation IDs
16. **Add metrics/monitoring** hooks
17. **Add prompt validation** for model-specific patterns
18. **Add auth error classes** for future implementation

---

## 8. Testing Gaps

The audit did not find formal test files. Recommend creating:

1. **utils/test_errors.py** - Test all error classes, duplicate detection
2. **utils/test_file_validator.py** - Test MIME spoofing, path traversal, edge cases
3. **utils/test_url_validator.py** - Test SSRF protection, encoding variations
4. **dtos/test_validation.py** - Test all DTO validators with edge cases
5. **services/test_business_logic.py** - Test validation in service layer

---

## 9. Conclusion

The codebase demonstrates **good engineering practices** with:
- Centralized error handling
- Comprehensive DTO validation
- Security-conscious file handling
- Structured validation utilities

However, **critical security issues** need immediate attention:
- SSRF vulnerability in URL validator
- MIME type spoofing in file validator
- Missing rate limiting
- Inconsistent error handling

**Estimated effort to address**:
- Critical fixes: 2-4 hours
- High priority: 8-12 hours
- Medium priority: 16-20 hours
- Low priority: 20-30 hours

**Total: ~50-70 hours** for comprehensive error handling and validation coverage.
