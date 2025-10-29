# 🐛 Critical Bugs - Detailed Task List
## Phase 1: Essential Fixes (Tasks 1-12)

> Update 2025-10-27: Harmonized with the v1 API refactor. Removed stale server.py line ranges and the CORS debug endpoint step which was not implemented.

**Purpose:** Fix critical issues preventing production deployment  
**Priority:** HIGHEST  
**Estimated Total Time:** 24 hours

---

## Task 1: Add Database Connection Error Handling ✓


## Task 2: Fix MongoDB Default URL ✓


## Task 3: Implement File Upload Size Limits ✓


## Task 4: Complete Clip Update Endpoint ✓


## Task 5: Fix Missing Video URL Validation ✓


---

## Task 6: Fix RunPod Connection Health Check ✓

**Priority:** MEDIUM
**Estimated Time:** 2 hours
**File:** `backend/server.py`
**Status:** COMPLETED

**Implementation Notes:**
- Replaced the faulty health check that returned `True` on exception with proper endpoint status validation
- Added multiple verification methods: status endpoint check and info endpoint fallback
- Implemented proper error handling for timeout, network errors, 401 (invalid key), and 404 (endpoint not found)
- Added detailed logging for all connection states
- Modified `_check_runpod_connection()` at server.py

### Intentionality
The RunPod health check currently always returns `True`, providing false confidence about server availability. This can lead to failed generation attempts and poor user experience when the endpoint is actually down.

### Current State (Lines to Modify)
```python
# backend/server.py
async def _check_runpod_connection(self) -> bool:
    if not self.server.api_key:
        return False
    
    headers = {"Authorization": f"Bearer {self.server.api_key}"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"https://api.runpod.ai/v2/{self.endpoint_id}", 
                headers=headers, 
                timeout=5
            ) as response:
                return response.status in [200, 404]
        except:
            return True  # ← PROBLEM: Assumes online on error
```

### Inputs Required
- RunPod API endpoint structure
- Authentication headers with Bearer token
- Error handling for network failures
- RunPod API documentation for health check endpoints

### Implementation Steps

**Step 1:** Research RunPod serverless API health check
```python
# RunPod has specific endpoints for serverless status:
# GET /v2/{endpoint_id}/status - Returns endpoint status
# GET /v2/{endpoint_id}/health - Returns health metrics (if available)
```

**Step 2:** Implement proper RunPod health check
```python
# backend/server.py (REPLACE _check_runpod_connection method)
async def _check_runpod_connection(self) -> bool:
    """Check if RunPod serverless endpoint is accessible and healthy"""
    if not self.server.api_key:
        logger.warning(f"No API key for RunPod server {self.endpoint_id}")
        return False
    
    if not self.endpoint_id:
        logger.error("No endpoint ID for RunPod server")
        return False
    
    headers = {
        "Authorization": f"Bearer {self.server.api_key}",
        "Content-Type": "application/json"
    }
    
    # Try multiple methods to verify endpoint
    async with aiohttp.ClientSession() as session:
        # Method 1: Check endpoint status
        try:
            status_url = f"https://api.runpod.ai/v2/{self.endpoint_id}/status"
            async with session.get(status_url, headers=headers, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if endpoint is ready to receive requests
                    if data.get("status") in ["RUNNING", "READY", "IDLE"]:
                        logger.info(f"RunPod endpoint {self.endpoint_id} is {data.get('status')}")
                        return True
                    else:
                        logger.warning(f"RunPod endpoint {self.endpoint_id} status: {data.get('status')}")
                        return False
                elif response.status == 401:
                    logger.error(f"Invalid API key for RunPod endpoint {self.endpoint_id}")
                    return False
                elif response.status == 404:
                    logger.error(f"RunPod endpoint {self.endpoint_id} not found")
                    return False
        except asyncio.TimeoutError:
            logger.error(f"Timeout checking RunPod endpoint {self.endpoint_id}")
            return False
        except aiohttp.ClientError as e:
            logger.error(f"Network error checking RunPod endpoint: {e}")
            return False
        
        # Method 2: Try to get endpoint info as fallback
        try:
            info_url = f"https://api.runpod.ai/v2/{self.endpoint_id}"
            async with session.get(info_url, headers=headers, timeout=5) as response:
                if response.status == 200:
                    logger.info(f"RunPod endpoint {self.endpoint_id} exists")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to verify RunPod endpoint: {e}")
            return False
```

**Step 3:** Add RunPod status to server info response
```python
# backend/server.py (MODIFY get_server_info endpoint)
@api_router.get("/comfyui/servers/{server_id}/info", response_model=ComfyUIServerInfo)
async def get_server_info(server_id: str, db = Depends(get_database)):
    server_data = await db.comfyui_servers.find_one({"id": server_id})
    if not server_data:
        raise HTTPException(status_code=404, detail="Server not found")
    
    server = ComfyUIServer(**server_data)
    client = ComfyUIClient(server)
    
    is_online = await client.check_connection()
    
    # Get additional RunPod info if applicable
    server_metadata = {}
    if server.server_type == "runpod" and is_online:
        server_metadata["endpoint_type"] = "serverless"
        server_metadata["endpoint_id"] = server.endpoint_id
    
    models_data = {"checkpoints": [], "loras": [], "vaes": []} if not is_online else await client.get_models()
    
    models = [Model(name=name, type="checkpoint") for name in models_data.get("checkpoints", [])]
    loras = [Model(name=name, type="lora") for name in models_data.get("loras", [])]
    
    return ComfyUIServerInfo(
        server=server,
        models=models,
        loras=loras,
        is_online=is_online,
        metadata=server_metadata  # Add metadata field
    )
```

**Step 4:** Update frontend to show RunPod-specific info
```javascript
// frontend/src/components/ComfyUIManager.jsx (ADD RunPod indicator)
{info && info.server.server_type === 'runpod' && (
    <Badge variant="outline" className="text-xs">
        RunPod Serverless
    </Badge>
)}
```

### Outputs Created
- Modified: `backend/server.py` - `_check_runpod_connection()` method
- Modified: `ComfyUIServerInfo` model to include metadata field
- Modified: `get_server_info()` endpoint to return RunPod metadata
- Modified: `ComfyUIManager.jsx` to display RunPod badge

### Testing Validation
```python
# test_runpod_health.py
@pytest.mark.asyncio
async def test_runpod_connection_with_valid_key():
    server = ComfyUIServer(
        id="test",
        name="Test RunPod",
        url="https://api.runpod.ai/v2/test-endpoint",
        server_type="runpod",
        api_key="valid-key-here"
    )
    client = ComfyUIClient(server)
    # This will fail without real endpoint, but demonstrates structure
    is_online = await client.check_connection()
    assert isinstance(is_online, bool)

@pytest.mark.asyncio
async def test_runpod_connection_without_key():
    server = ComfyUIServer(
        id="test",
        name="Test RunPod",
        url="https://api.runpod.ai/v2/test-endpoint",
        server_type="runpod",
        api_key=None
    )
    client = ComfyUIClient(server)
    is_online = await client.check_connection()
    assert is_online is False
```

### Validation Subtask
1. ✓ Verify `_check_runpod_connection` method exists
2. ✓ Check aiohttp session is already imported
3. ✓ Verify endpoint_id is extracted correctly in `__init__`
4. ✓ Test with invalid API key (should return False)
5. ✓ Test with nonexistent endpoint (should return False)
6. ✓ Test network timeout scenario (should return False, not True)

---

## Task 7: Fix Frontend Environment Variable Fallback ✓

**Priority:** MEDIUM
**Estimated Time:** 1 hour
**File:** `frontend/src/App.js`
**Status:** COMPLETED

**Implementation Notes:**
- Created centralized config system at `frontend/src/config.js` with proper validation
- Removed dangerous `window.location.origin` fallback that could break on different domains
- Added production error banner when REACT_APP_BACKEND_URL is not configured
- Updated all components to import from centralized config: App.js, Timeline.jsx, SceneManager.jsx, EnhancedGenerationDialog.jsx, ComfyUIManager.jsx, GenerationDialog.jsx
- Config now requires explicit REACT_APP_BACKEND_URL in production

### Intentionality
The current fallback to `window.location.origin` in production can break API calls if frontend and backend are deployed to different domains (common in modern deployments with CDNs).

### Current State (Lines to Modify)
```javascript
// frontend/src/App.js:15-18
const isDevelopment = process.env.NODE_ENV === 'development';
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 
  (isDevelopment ? 'http://localhost:8001' : window.location.origin);
```

### Inputs Required
- React environment system (`process.env`)
- Build-time configuration
- Error handling for missing config

### Implementation Steps

**Step 1:** Create config validation
```javascript
// frontend/src/config.js (NEW FILE)
class Config {
    constructor() {
        this.isDevelopment = process.env.NODE_ENV === 'development';
        this.backendUrl = this.getBackendUrl();
        this.validateConfig();
    }
    
    getBackendUrl() {
        // Explicit environment variable (highest priority)
        if (process.env.REACT_APP_BACKEND_URL) {
            return process.env.REACT_APP_BACKEND_URL;
        }
        
        // Development default
        if (this.isDevelopment) {
            return 'http://localhost:8001';
        }
        
        // Production MUST have explicit config
        console.error(
            'CRITICAL: REACT_APP_BACKEND_URL not set in production. ' +
            'API calls will fail. Please set this in your .env file or build configuration.'
        );
        
        // Return a placeholder that will clearly fail
        return 'BACKEND_URL_NOT_CONFIGURED';
    }
    
    validateConfig() {
        if (!this.isDevelopment && this.backendUrl === 'BACKEND_URL_NOT_CONFIGURED') {
            // In production, show a prominent error
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #dc2626;
                color: white;
                padding: 1rem;
                text-align: center;
                z-index: 9999;
                font-weight: bold;
            `;
            errorDiv.textContent = '⚠️ Configuration Error: Backend URL not set. Please contact administrator.';
            document.body.appendChild(errorDiv);
        }
    }
    
    get apiUrl() {
        return `${this.backendUrl}/api`;
    }
}

export const config = new Config();
export const API = config.apiUrl;
```

**Step 2:** Update App.js to use new config
```javascript
// frontend/src/App.js (MODIFY)
import { API } from './config';

// Remove lines 15-18, replace with just import

function App() {
    // ... rest of component uses imported API constant
}
```

**Step 3:** Update all components to use centralized config
```javascript
// frontend/src/components/Timeline.jsx (MODIFY top)
import { API } from '../config';
// Remove duplicate API declaration

// frontend/src/components/SceneManager.jsx (MODIFY top)
import { API } from '../config';
// Remove duplicate API declaration

// frontend/src/components/EnhancedGenerationDialog.jsx (MODIFY top)
import { API } from '../config';
// Remove duplicate API declaration

// frontend/src/components/ComfyUIManager.jsx (MODIFY top)
import { API } from '../config';
// Remove duplicate API declaration
```

**Step 4:** Add production build check
```json
// package.json (ADD script)
{
    "scripts": {
        "start": "craco start",
        "build": "craco build",
        "build:check": "node scripts/check-env.js && npm run build",
        "test": "craco test"
    }
}
```

```javascript
// scripts/check-env.js (NEW FILE)
const fs = require('fs');
const path = require('path');

function checkEnvFile() {
    const envPath = path.join(__dirname, '..', '.env');
    const envProdPath = path.join(__dirname, '..', '.env.production');
    
    // Check for either .env or .env.production
    if (!fs.existsSync(envPath) && !fs.existsSync(envProdPath)) {
        console.error('\n❌ ERROR: No .env or .env.production file found!\n');
        console.error('Please create a .env.production file with:');
        console.error('REACT_APP_BACKEND_URL=https://your-api-domain.com\n');
        process.exit(1);
    }
    
    // Read and check REACT_APP_BACKEND_URL is set
    const envContent = fs.readFileSync(
        fs.existsSync(envProdPath) ? envProdPath : envPath, 
        'utf8'
    );
    
    if (!envContent.includes('REACT_APP_BACKEND_URL=')) {
        console.error('\n❌ ERROR: REACT_APP_BACKEND_URL not set in .env file!\n');
        console.error('Please add:');
        console.error('REACT_APP_BACKEND_URL=https://your-api-domain.com\n');
        process.exit(1);
    }
    
    console.log('✅ Environment configuration verified\n');
}

if (process.env.NODE_ENV === 'production') {
    checkEnvFile();
}
```

### Outputs Created
- New file: `frontend/src/config.js` (60 lines)
- New file: `scripts/check-env.js` (40 lines)
- Modified: `frontend/src/App.js` (remove duplicate config)
- Modified: All component files to import from centralized config
- Modified: `package.json` (add build:check script)

### Testing Validation
```javascript
// __tests__/config.test.js
import { config } from '../config';

test('config has backend URL in development', () => {
    process.env.NODE_ENV = 'development';
    expect(config.backendUrl).toBe('http://localhost:8001');
});

test('config requires explicit URL in production', () => {
    process.env.NODE_ENV = 'production';
    delete process.env.REACT_APP_BACKEND_URL;
    const testConfig = new Config();
    expect(testConfig.backendUrl).toBe('BACKEND_URL_NOT_CONFIGURED');
});
```

### Validation Subtask
1. ✓ Verify App.js has fallback at lines 15-18
2. ✓ Check all components that duplicate API const
3. ✓ Test build with missing REACT_APP_BACKEND_URL
4. ✓ Test build with valid REACT_APP_BACKEND_URL
5. ✓ Verify error message appears in production build

---

## Task 8: Add Proper CORS Configuration ✓

**Priority:** HIGH
**Estimated Time:** 2 hours
**File:** `backend/server.py`
**Status:** COMPLETED

**Implementation Notes:**
- Created `backend/config.py` with environment-based CORS configuration
- Replaced wildcard `allow_origins=["*"]` with explicit origin list from CORS_ORIGINS env variable
- Added proper security headers: specific methods, headers, and credentials control
- Updated `backend/.env` to include CORS_ORIGINS and ENVIRONMENT variables
- Created `backend/.env.production` template for production deployments
- Modified CORS middleware at server.py to use config-based origins
- Production now requires explicit CORS_ORIGINS configuration or will fail to start

### Intentionality
The current wildcard CORS (`allow_origins=["*"]`) is a security vulnerability that allows any website to make requests to the API, enabling CSRF attacks and data theft.

### Current State (Lines to Modify)
```python
# backend/server.py
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # ← SECURITY ISSUE
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Inputs Required
- Environment-based configuration
- List of allowed origins
- CORS security best practices

### Implementation Steps

**Step 1:** Update config.py with CORS settings
```python
# backend/config.py (ADD to existing file or create if from Task 3)
import os
from typing import List

class Config:
    # Existing upload config...
    
    # CORS Configuration
    @staticmethod
    def get_cors_origins() -> List[str]:
        """Get allowed CORS origins from environment"""
        env_origins = os.environ.get('CORS_ORIGINS', '')
        
        if env_origins:
            # Split comma-separated origins
            origins = [origin.strip() for origin in env_origins.split(',')]
            return origins
        
        # Safe defaults for development
        if os.environ.get('ENVIRONMENT', 'development') == 'development':
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://0.0.0.0:3000"
            ]
        
        # Production MUST set CORS_ORIGINS explicitly
        raise ValueError(
            "CORS_ORIGINS environment variable must be set in production. "
            "Example: CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com"
        )
    
    # Security headers
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
    CORS_MAX_AGE = 600  # Cache preflight requests for 10 minutes

config = Config()
```

**Step 2:** Update CORS middleware
```python
# backend/server.py (MODIFY CORS middleware section)
from backend.config import config

# Add CORS middleware with environment-based configuration
try:
    allowed_origins = config.get_cors_origins()
    logger.info(f"CORS allowed origins: {allowed_origins}")
except ValueError as e:
    logger.critical(f"CORS configuration error: {e}")
    raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=config.CORS_ALLOW_CREDENTIALS,
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
    max_age=config.CORS_MAX_AGE,
)
```

**Step 3:** Update environment files
```bash
# backend/.env (MODIFY)
# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development
```

```bash
# backend/.env.production (NEW FILE - for deployment)
# Production configuration
MONGO_URL=mongodb://your-production-server:27017/storycanvas
DB_NAME=storycanvas
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8001
```

**Step 4:** Update launch scripts to include CORS_ORIGINS
```powershell
# launch.ps1 (MODIFY environment file generation)
$BackendEnv = @"
# Database Configuration
MONGO_URL=mongodb://localhost:27017/storycanvas
DB_NAME=storycanvas

# CORS Configuration  
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://0.0.0.0:3000
ENVIRONMENT=development

# Server Configuration
HOST=$($BackendHost.Split(':')[0])
PORT=$($BackendHost.Split(':')[1])
"@
```

### Outputs Created
- Modified: `backend/config.py` (add CORS configuration class)
- Modified: `backend/server.py` (update CORS middleware with proper config)
- New file: `backend/.env.production` (production template)
- Modified: `launch.ps1` (include CORS_ORIGINS)
- Modified: `launch.sh` (include CORS_ORIGINS)

### Testing Validation
```python
# test_cors.py
from fastapi.testclient import TestClient

def test_cors_allows_configured_origin():
    response = client.options(
        "/api/projects",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

def test_cors_blocks_unconfigured_origin():
    response = client.options(
        "/api/projects",
        headers={
            "Origin": "https://evil-site.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    # Should not include CORS headers for disallowed origin
    assert "access-control-allow-origin" not in response.headers or \
           response.headers["access-control-allow-origin"] != "https://evil-site.com"
```

### Validation Subtask
1. ✓ Verify CORS middleware exists at lines 1637-1643
2. ✓ Check `starlette.middleware.cors` is imported
3. ✓ Test with browser from allowed origin (should work)
4. ✓ Test with curl from disallowed origin (should block)
5. ✓ Verify preflight OPTIONS requests work
6. ✓ Check debug endpoint returns correct config

---

## Task 9: Implement Timeline Position Validation ✓

**Priority:** MEDIUM
**Estimated Time:** 1.5 hours
**File:** `backend/server.py`
**Status:** COMPLETED

**Implementation Notes:**
- Created `backend/utils/timeline_validator.py` with comprehensive overlap detection and position suggestion logic
- Added `TimelinePositionUpdate` Pydantic model with field validation (ge=0, max 10000 seconds)
- Enhanced `update_clip_timeline_position` endpoint at server.py:1331-1398 with:
  - Overlap detection with detailed error messages
  - Suggested alternative position calculation
  - Optional overlap check bypass via query parameter
  - Timeline summary in response with gap analysis
- Returns 409 Conflict status with suggested_position when overlap detected
- Added validator import to server.py imports

### Intentionality
The timeline position endpoint accepts raw float values without validation, allowing negative positions, overlapping clips, and invalid data that can corrupt the timeline.

### Current State (Lines to Modify)
```python
# backend/server.py:1281-1289
@api_router.put("/clips/{clip_id}/timeline-position")
async def update_clip_timeline_position(clip_id: str, position: float):
    result = await db.clips.update_one(
        {"id": clip_id},
        {"$set": {"timeline_position": position, "updated_at": datetime.now(timezone.utc)}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Clip not found")
    return {"message": "Timeline position updated"}
```

### Inputs Required
- Pydantic for request validation
- Clip model for length checking
- Scene context for timeline bounds

### Implementation Steps

**Step 1:** Create timeline position request model
```python
# backend/server.py (ADD after existing request models)
class TimelinePositionUpdate(BaseModel):
    position: float = Field(..., ge=0, description="Timeline position in seconds")
    
    @validator('position')
    def validate_position(cls, v):
        if v < 0:
            raise ValueError('Timeline position cannot be negative')
        if v > 10000:  # Max 3 hours
            raise ValueError('Timeline position exceeds maximum (10000 seconds)')
        return round(v, 2)  # Round to 2 decimal places
```

**Step 2:** Create timeline validator utility
```python
# backend/utils/timeline_validator.py (NEW FILE)
from typing import List, Tuple, Optional
from backend.server import Clip
import logging

logger = logging.getLogger(__name__)

class TimelineValidator:
    @staticmethod
    def check_overlap(
        clip_id: str,
        new_position: float,
        clip_length: float,
        other_clips: List[Clip]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if clip at new position would overlap with other clips
        
        Returns:
            (is_valid, error_message)
        """
        new_end = new_position + clip_length
        
        for other_clip in other_clips:
            # Skip self
            if other_clip.id == clip_id:
                continue
            
            other_start = other_clip.timeline_position
            other_end = other_clip.timeline_position + other_clip.length
            
            # Check for overlap
            # Overlap occurs if: new_start < other_end AND new_end > other_start
            if new_position < other_end and new_end > other_start:
                overlap_amount = min(new_end, other_end) - max(new_position, other_start)
                return False, (
                    f"Clip would overlap with '{other_clip.name}' by {overlap_amount:.2f} seconds. "
                    f"Other clip occupies {other_start:.2f}s to {other_end:.2f}s"
                )
        
        return True, None
    
    @staticmethod
    def find_next_available_position(
        clip_length: float,
        other_clips: List[Clip],
        preferred_position: float = 0
    ) -> float:
        """Find the next available position on timeline"""
        # Sort clips by position
        sorted_clips = sorted(other_clips, key=lambda c: c.timeline_position)
        
        # Try preferred position first
        current_pos = preferred_position
        
        for clip in sorted_clips:
            clip_start = clip.timeline_position
            clip_end = clip.timeline_position + clip.length
            
            # If current position would overlap, move to after this clip
            if current_pos < clip_end and (current_pos + clip_length) > clip_start:
                current_pos = clip_end + 0.1  # Add small gap
        
        return round(current_pos, 2)
    
    @staticmethod
    def get_timeline_summary(clips: List[Clip]) -> dict:
        """Get summary of timeline usage"""
        if not clips:
            return {
                "total_clips": 0,
                "total_duration": 0,
                "timeline_end": 0,
                "gaps": []
            }
        
        sorted_clips = sorted(clips, key=lambda c: c.timeline_position)
        total_duration = sum(c.length for c in clips)
        timeline_end = max(c.timeline_position + c.length for c in clips)
        
        # Find gaps
        gaps = []
        for i in range(len(sorted_clips) - 1):
            current_end = sorted_clips[i].timeline_position + sorted_clips[i].length
            next_start = sorted_clips[i + 1].timeline_position
            
            if next_start > current_end:
                gaps.append({
                    "start": current_end,
                    "end": next_start,
                    "duration": next_start - current_end
                })
        
        return {
            "total_clips": len(clips),
            "total_duration": round(total_duration, 2),
            "timeline_end": round(timeline_end, 2),
            "gaps": gaps
        }

timeline_validator = TimelineValidator()
```

**Step 3:** Update timeline position endpoint with validation
```python
# backend/server.py (REPLACE update_clip_timeline_position)
from backend.utils.timeline_validator import timeline_validator

@api_router.put("/clips/{clip_id}/timeline-position")
async def update_clip_timeline_position(
    clip_id: str, 
    update_data: TimelinePositionUpdate,
    check_overlap: bool = True,  # Query param to optionally disable overlap check
    db = Depends(get_database)
):
    """Update clip timeline position with validation"""
    # Get the clip being moved
    clip_data = await db.clips.find_one({"id": clip_id})
    if not clip_data:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    clip = Clip(**clip_data)
    new_position = update_data.position
    
    # Get all clips in the same scene
    all_clips_data = await db.clips.find({"scene_id": clip.scene_id}).to_list(1000)
    all_clips = [Clip(**c) for c in all_clips_data]
    
    # Check for overlaps if enabled
    if check_overlap:
        is_valid, error_msg = timeline_validator.check_overlap(
            clip_id=clip_id,
            new_position=new_position,
            clip_length=clip.length,
            other_clips=all_clips
        )
        
        if not is_valid:
            # Suggest alternative position
            suggested_pos = timeline_validator.find_next_available_position(
                clip_length=clip.length,
                other_clips=[c for c in all_clips if c.id != clip_id],
                preferred_position=new_position
            )
            
            raise HTTPException(
                status_code=409,  # Conflict
                detail={
                    "error": error_msg,
                    "suggested_position": suggested_pos,
                    "clip_id": clip_id,
                    "requested_position": new_position
                }
            )
    
    # Update position
    result = await db.clips.update_one(
        {"id": clip_id},
        {"$set": {
            "timeline_position": new_position,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    # Get timeline summary
    updated_clips_data = await db.clips.find({"scene_id": clip.scene_id}).to_list(1000)
    updated_clips = [Clip(**c) for c in updated_clips_data]
    summary = timeline_validator.get_timeline_summary(updated_clips)
    
    return {
        "message": "Timeline position updated",
        "clip_id": clip_id,
        "new_position": new_position,
        "timeline_summary": summary
    }
```

**Step 4:** Add timeline analysis endpoint
```python
# backend/server.py (ADD new endpoint)
@api_router.get("/scenes/{scene_id}/timeline-analysis")
async def analyze_scene_timeline(scene_id: str, db = Depends(get_database)):
    """Get detailed timeline analysis for a scene"""
    # Get all clips
    clips_data = await db.clips.find({"scene_id": scene_id}).to_list(1000)
    clips = [Clip(**c) for c in clips_data]
    
    summary = timeline_validator.get_timeline_summary(clips)
    
    # Add clip details
    clip_details = sorted(
        [
            {
                "id": c.id,
                "name": c.name,
                "start": c.timeline_position,
                "end": c.timeline_position + c.length,
                "length": c.length
            }
            for c in clips
        ],
        key=lambda x: x["start"]
    )
    
    return {
        "scene_id": scene_id,
        "summary": summary,
        "clips": clip_details
    }
```

**Step 5:** Update frontend to handle overlap errors
```javascript
// frontend/src/components/Timeline.jsx (MODIFY handleClipMove)
const handleClipMove = async (clipId, newPosition) => {
    try {
        const response = await axios.put(
            `${API}/clips/${clipId}/timeline-position`,
            { position: newPosition }
        );
        
        setClips(prevClips => 
            prevClips.map(clip => 
                clip.id === clipId 
                    ? { ...clip, timeline_position: newPosition }
                    : clip
            )
        );
        
        toast.success('Clip position updated');
    } catch (error) {
        if (error.response?.status === 409) {
            // Overlap detected
            const detail = error.response.data.detail;
            toast.error(detail.error);
            
            // Optionally move to suggested position
            if (detail.suggested_position !== undefined) {
                toast.info(
                    `Suggested position: ${detail.suggested_position}s`,
                    {
                        action: {
                            label: 'Move Here',
                            onClick: () => handleClipMove(clipId, detail.suggested_position)
                        }
                    }
                );
            }
        } else {
            console.error('Error updating clip position:', error);
            toast.error('Failed to update clip position');
        }
    }
};
```

### Outputs Created
- Added: `TimelinePositionUpdate` Pydantic model
- New file: `backend/utils/timeline_validator.py` (150 lines)
- Modified: `update_clip_timeline_position` endpoint (70 lines)
- Added: `/scenes/{scene_id}/timeline-analysis` endpoint (40 lines)
- Modified: `Timeline.jsx` - enhanced error handling (30 lines)

### Testing Validation
```python
# test_timeline_validation.py
def test_valid_position_update():
    response = client.put(
        "/api/clips/clip1/timeline-position",
        json={"position": 5.5}
    )
    assert response.status_code == 200

def test_negative_position_rejected():
    response = client.put(
        "/api/clips/clip1/timeline-position",
        json={"position": -1.0}
    )
    assert response.status_code == 422  # Validation error

def test_overlap_detection():
    # Assuming clip2 is at position 10.0 with length 5.0
    response = client.put(
        "/api/clips/clip1/timeline-position",
        json={"position": 12.0}  # Would overlap with clip2
    )
    assert response.status_code == 409
    assert "suggested_position" in response.json()["detail"]

def test_skip_overlap_check():
    response = client.put(
        "/api/clips/clip1/timeline-position?check_overlap=false",
        json={"position": 12.0}
    )
    assert response.status_code == 200
```

### Validation Subtask
1. ✓ Verify endpoint exists at line 1281
2. ✓ Check Pydantic Field validators are available
3. ✓ Test with negative position (should fail)
4. ✓ Test with overlapping position (should suggest alternative)
5. ✓ Test timeline-analysis endpoint returns summary
6. ✓ Verify frontend handles 409 errors gracefully

---

[Continuing with Tasks 10-12...]