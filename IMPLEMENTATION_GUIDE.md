# 🚀 Quick Implementation Guide
## StoryCanvas - Developer Reference

**Last Updated:** December 2024

---

## 🎯 Getting Started

### Prerequisites
- Node.js 16+
- Python 3.8+
- MongoDB (local or Atlas)

### Quick Launch
```bash
# Windows PowerShell (Recommended)
.\launch.ps1

# Windows Batch
launch.bat

# Manual Backend
cd backend && uvicorn server:app --reload

# Manual Frontend
cd frontend && npm start
```

---

## 📋 Project Structure

```
storycanvas/
├── backend/
│   ├── api/v1/                    # Versioned API routers (Phase 2)
│   │   ├── projects_router.py     # Project endpoints
│   │   ├── scenes_router.py       # Scene endpoints
│   │   ├── clips_router.py        # Clip endpoints
│   │   ├── generation_router.py   # Generation endpoints
│   │   ├── characters_router.py   # Character management
│   │   ├── templates_router.py    # Style templates
│   │   ├── queue_router.py        # Queue management
│   │   ├── comfyui_router.py      # ComfyUI servers
│   │   ├── media_router.py        # File uploads
│   │   ├── health_router.py       # Health checks
│   │   └── dependencies.py        # Shared dependencies
│   ├── services/                  # Business logic layer (Phase 2)
│   │   ├── project_service.py     # Project operations
│   │   ├── generation_service.py  # Generation logic
│   │   ├── comfyui_service.py     # ComfyUI client
│   │   ├── queue_manager.py       # Queue management
│   │   ├── export_service.py      # Export formats
│   │   ├── batch_generator.py     # Batch generation
│   │   ├── gallery_manager.py     # Content gallery
│   │   ├── media_service.py       # File handling
│   │   └── model_config.py        # Model presets
│   ├── repositories/              # Data access layer (Phase 2)
│   │   ├── base_repository.py     # Base CRUD operations
│   │   ├── project_repository.py  # Project data access
│   │   ├── scene_repository.py    # Scene data access
│   │   ├── clip_repository.py     # Clip data access
│   │   └── comfyui_repository.py  # Server data access
│   ├── dtos/                      # Data transfer objects (Phase 2)
│   │   ├── project_dto.py         # Project DTOs
│   │   ├── scene_dto.py           # Scene DTOs
│   │   ├── clip_dto.py            # Clip DTOs
│   │   └── ...                    # 42+ DTO classes
│   ├── models/                    # Pydantic models
│   │   ├── project.py
│   │   ├── scene.py
│   │   ├── clip.py
│   │   └── ...
│   ├── utils/                     # Utilities
│   │   ├── errors.py              # Custom exceptions
│   │   ├── file_validator.py     # File validation
│   │   └── timeline_validator.py # Timeline logic
│   ├── database.py                # Database manager
│   ├── config.py                  # Configuration
│   ├── server.py                  # Main application (5200+ lines)
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Environment config
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProjectView.jsx            # Project management
│   │   │   ├── ProjectTimeline.jsx        # Timeline visualization
│   │   │   ├── SceneManager.jsx           # Scene/clip editor
│   │   │   ├── CharacterManager.jsx       # Character library (Phase 2.5)
│   │   │   ├── StyleTemplateLibrary.jsx   # Template library (Phase 2.5)
│   │   │   ├── QueueDashboard.jsx         # Queue monitoring (Phase 2.5)
│   │   │   ├── ProjectDashboard.jsx       # Project details (Phase 2.5)
│   │   │   ├── GenerationPool.jsx         # Content reuse (Phase 2.7)
│   │   │   ├── EnhancedGenerationDialog.jsx
│   │   │   ├── ComfyUIManager.jsx
│   │   │   ├── PresentationMode.jsx
│   │   │   └── ui/                        # 56 Shadcn components
│   │   ├── services/                      # API service layer
│   │   ├── hooks/                         # Custom React hooks
│   │   └── App.js                         # Main application router
│   ├── package.json
│   └── .env
│
├── docs/
│   ├── archive/                   # Completed phase documentation
│   │   ├── PHASE_1_COMPLETION_SUMMARY.md
│   │   └── PHASE_2_COMPLETION.md
│   ├── CURRENT_STATUS.md          # Current state
│   ├── CHARACTER_CREATION_BEST_PRACTICES.md
│   └── FACEFUSION_INTEGRATION.md
│
├── launch.ps1
├── launch.bat
├── README.md
├── IMPLEMENTATION_GUIDE.md
└── AUDIT_REPORT.md
```

---

## 🔑 Architecture Overview

### Backend Architecture (Phase 2 Complete)

```
HTTP Request
    ↓
API Router (/api/v1/*)
    ↓
Service Layer (business logic)
    ↓
Repository Layer (data access)
    ↓
MongoDB Database
```

**Key Principles:**
- **Separation of Concerns**: Routes handle HTTP, services handle logic, repositories handle data
- **Dependency Injection**: Database and services injected via FastAPI dependencies
- **API Versioning**: `/api/v1` for current API, `/api` for legacy (backward compatibility)
- **DTOs**: Request/Response data transfer objects for API contracts
- **Error Handling**: Standardized error responses with custom exceptions

### Frontend Architecture

```
React Component
    ↓
API Service (axios)
    ↓
Backend API (/api/v1/*)
```

**Key Features:**
- Component-based architecture
- Service layer for API communication
- Custom hooks for reusable logic
- Shadcn UI components
- Real-time updates with polling

---

## 🗄️ Data Models

### Core Entities
```
Project (1) ──> (N) Scene (1) ──> (N) Clip
                                      │
                                      └──> GeneratedContent[]
Character (N) <──> (N) Clip (via references)
StyleTemplate (N) <──> (N) Clip (via application)
GenerationPool (shared content library)
QueueJob (generation queue)
```

### MongoDB Collections
- `projects` - Top-level containers
- `scenes` - Sections within projects
- `clips` - Individual video segments
- `comfyui_servers` - AI generation servers
- `characters` - Character definitions
- `style_templates` - Reusable generation settings
- `generation_pool` - Shared content library
- `model_presets` - Model-specific presets
- `queue_jobs` - Generation queue
- `database_models` - Synced model information

---

## 🔌 API Endpoints Reference

### API Versioning
- **Current**: `/api/v1/*` (recommended)
- **Legacy**: `/api/*` (deprecated, backward compatibility only)

### Projects (`/api/v1/projects`)
```
POST   /                           # Create project
GET    /                           # List all projects
GET    /{id}                       # Get project details
GET    /{id}/with-scenes           # Get project with full hierarchy
PUT    /{id}                       # Update project
DELETE /{id}                       # Delete project
GET    /{id}/clips                 # List all clips in project
GET    /{id}/export/fcpxml         # Export to Final Cut Pro XML
GET    /{id}/export/edl            # Export to Adobe Premiere EDL
GET    /{id}/export/resolve        # Export to DaVinci Resolve
GET    /{id}/export/json           # Export as JSON
```

### Scenes (`/api/v1/scenes`)
```
POST   /                           # Create scene
GET    /project/{project_id}       # List scenes in project
GET    /{id}                       # Get scene details
PUT    /{id}                       # Update scene
DELETE /{id}                       # Delete scene
GET    /{id}/timeline-analysis     # Analyze scene timeline
```

### Clips (`/api/v1/clips`)
```
POST   /                           # Create clip
GET    /scene/{scene_id}           # List clips in scene
GET    /{id}                       # Get clip details
GET    /{id}/gallery               # Get generated content gallery
PUT    /{id}                       # Update clip
PUT    /{id}/timeline-position     # Update timeline position
PUT    /{id}/prompts               # Update prompts
DELETE /{id}                       # Delete clip
```

### Generation (`/api/v1/generation`)
```
POST   /                           # Generate image/video for clip
POST   /batch                      # Start batch generation
GET    /batch/{id}                 # Get batch status
GET    /batches                    # List all batches
```

### Characters (`/api/v1/characters`)
```
POST   /                           # Create character
GET    /                           # List characters (with project filter)
GET    /{id}                       # Get character details
PUT    /{id}                       # Update character
DELETE /{id}                       # Delete character
POST   /{id}/apply/{clip_id}       # Apply character to clip
```

### Style Templates (`/api/v1/templates`)
```
POST   /                           # Create template
GET    /                           # List all templates
GET    /{id}                       # Get template details
PUT    /{id}                       # Update template
DELETE /{id}                       # Delete template
POST   /{id}/use                   # Increment use count
```

### Queue (`/api/v1/queue`)
```
POST   /jobs                       # Add generation job
GET    /jobs                       # List all jobs
GET    /jobs/{id}                  # Get job status
GET    /status                     # Get queue status
GET    /projects/{id}/jobs         # Get project jobs
POST   /servers/{id}/register      # Register ComfyUI server
GET    /servers/{id}/next          # Get next job for server
POST   /jobs/{id}/complete         # Mark job complete
```

### ComfyUI Servers (`/api/v1/comfyui`)
```
POST   /servers                    # Add server
GET    /servers                    # List servers
GET    /servers/{id}/info          # Get server status
PUT    /servers/{id}               # Update server
DELETE /{id}                       # Delete server
```

### Media (`/api/v1/media`)
```
POST   /projects/{id}/upload-music # Upload music file
POST   /upload-face-image          # Upload face image for reactor
```

### Health (`/api/v1/health`)
```
GET    /                           # API root status
GET    /health                     # Comprehensive health check
```

---

## 🎨 Supported AI Models

| Model Type | Fast Steps | Quality Steps | Special Features |
|------------|------------|---------------|------------------|
| flux_dev | 8 | 28 | LoRA (max 3) |
| flux_krea | 4 | 8 | Ultra-fast |
| flux_pro | 12 | 35 | Highest quality |
| sdxl | 15 | 35 | Refiner, LoRA (max 5) |
| pony | 12 | 28 | Style-focused |
| illustrious | 15 | 30 | Anime presets |
| wan_2_1 | 15 | 25 | 512x512 video, special VAE |
| wan_2_2 | 8 | 20 | 768x768 video, dual models |
| ltx_video | 10 | 30 | Lightning-fast video |
| hunyuan_video | 20 | 40 | Tencent's video model |
| hidream | 12 | 25 | Balanced generation |
| qwen_image | 10 | 20 | Text rendering |
| qwen_edit | 8 | 15 | Image editing |

---

## 🛠️ Common Development Tasks

### 1. Add New API Endpoint (Phase 2 Pattern)

**Step 1: Create DTO**
```python
# backend/dtos/my_feature_dto.py
from pydantic import BaseModel

class MyFeatureRequestDTO(BaseModel):
    name: str
    value: int

class MyFeatureResponseDTO(BaseModel):
    id: str
    name: str
    value: int
```

**Step 2: Create Service**
```python
# backend/services/my_feature_service.py
class MyFeatureService:
    def __init__(self, repository):
        self.repository = repository
    
    async def create(self, data: dict):
        return await self.repository.create(data)
```

**Step 3: Create Router**
```python
# backend/api/v1/my_feature_router.py
from fastapi import APIRouter, Depends
from dtos.my_feature_dto import MyFeatureRequestDTO, MyFeatureResponseDTO

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

@router.post("", response_model=MyFeatureResponseDTO)
async def create_feature(
    request: MyFeatureRequestDTO,
    service = Depends(get_my_feature_service)
):
    return await service.create(request.dict())
```

**Step 4: Register Router**
```python
# backend/api/v1/__init__.py
from .my_feature_router import router as my_feature_router

api_v1_router.include_router(my_feature_router)
```

### 2. Add New Frontend Component

```javascript
// components/MyComponent.jsx
import React from 'react'
import { Button } from '@/components/ui/button'

export default function MyComponent({ prop }) {
    return <Button>{prop}</Button>
}
```

### 3. Add New Model Type

```python
# backend/services/model_config.py
MODEL_DEFAULTS = {
    "new_model": {
        "fast": {
            "steps": 10,
            "cfg": 5.0,
            "width": 1024,
            "height": 1024,
            "sampler": "euler",
            "scheduler": "normal"
        },
        "quality": {
            "steps": 30,
            "cfg": 7.0,
            # ... higher quality settings
        }
    }
}

# Update detect_model_type()
def detect_model_type(model_name: str) -> str:
    model_lower = model_name.lower()
    if "newmodel" in model_lower:
        return "new_model"
    # ... existing checks
```

---

## ✅ Phase Completion Status

### Phase 1: Critical Bug Fixes ✅
- [x] MongoDB URL configuration fixes
- [x] Database connection error handling with retry logic
- [x] File upload size limits and validation
- [x] Complete CRUD operations for all entities
- [x] CORS configuration with environment-based origins
- [x] Timeline position validation
- [x] Standardized error messages
- [x] Frontend parameter validation

### Phase 2: Architecture Improvements ✅
- [x] Service Layer Pattern implemented
- [x] Repository Pattern for data access
- [x] Request/Response DTOs (42+ classes)
- [x] API Versioning (`/api/v1` with backward compatibility)
- [x] Dependency injection throughout
- [x] Proper separation of concerns

### Phase 2.5: Frontend-Backend Integration ✅
- [x] Character Management UI
- [x] Style Templates Library
- [x] Queue Management Dashboard
- [x] Project Details Dashboard
- [x] Real-time updates (5-second refresh)

### Phase 2.6: Timeline System ✅
- [x] Project Timeline API
- [x] Alternates System (A/B versions)
- [x] ProjectTimeline Component
- [x] ObjectId serialization fixes

### Phase 2.7: Generation Pool ✅
- [x] Pool Management API
- [x] GenerationPool Component
- [x] Gallery Integration ("Send to Pool")

### Phase 3: Security & Authentication 📋
- [ ] JWT authentication system
- [ ] User management
- [ ] Password hashing
- [ ] API key encryption at rest
- [ ] Rate limiting
- [ ] Protected routes

### Phase 4: Content Features 🔄
- [x] Batch Generation
- [x] Style Transfer Templates
- [x] Export Formats (FCPXML, EDL, Resolve)
- [x] Character Manager
- [x] Presentation Mode
- [x] Hotkey System
- [ ] AI-powered prompt enhancement
- [ ] Auto lip-sync with audio
- [ ] Visual style consistency analyzer

### Phase 5: Frontend Improvements 📋
- [ ] State management (Zustand/Redux)
- [ ] React Query for data fetching
- [ ] Error boundaries
- [ ] Code splitting and lazy loading
- [ ] TypeScript migration
- [ ] Performance optimizations

### Phase 6: Data Management 📋
- [ ] Database migrations (Alembic)
- [ ] Soft deletes
- [ ] Backup strategy
- [ ] Redis caching layer
- [ ] Data archiving

### Phase 7: Monitoring & Observability 📋
- [ ] Structured logging
- [ ] Comprehensive health checks
- [ ] Performance metrics (Prometheus)
- [ ] Error tracking (Sentry)
- [ ] Request tracing

### Phase 8: Testing & CI/CD 📋
- [ ] Unit tests (backend)
- [ ] Unit tests (frontend)
- [ ] Integration tests
- [ ] E2E tests (Playwright)
- [ ] CI/CD pipeline
- [ ] Automated deployments

---

## 🐛 Troubleshooting

### MongoDB Connection Failed
```bash
# Check if MongoDB is running
# Windows: Check Task Manager for mongod.exe
# Linux/Mac: ps aux | grep mongod

# Start MongoDB (Windows)
net start MongoDB

# Or use MongoDB Atlas (cloud)
```

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8001 | xargs kill -9
```

### Frontend Not Connecting to Backend
1. Check `REACT_APP_BACKEND_URL` in `frontend/.env`
2. Verify backend is running on correct port
3. Check CORS configuration in `backend/.env`
4. Clear browser cache and restart frontend

### Generation Fails
1. Verify ComfyUI server is accessible
2. Check model name matches exactly
3. Ensure LoRA files exist on server
4. Review generation parameters for model type
5. Check queue dashboard for error messages

### API Returns 404 on /api/v1/*
1. Ensure you're using the correct endpoint path
2. Check that routers are properly mounted in `server.py`
3. Verify backend has restarted after code changes

---

## 📚 Code Examples

### Complete Workflow Example
```javascript
// 1. Create Project
const project = await axios.post(`${API}/api/v1/projects`, {
    name: "Music Video",
    description: "My awesome video"
})

// 2. Create Scene
const scene = await axios.post(`${API}/api/v1/scenes`, {
    project_id: project.data.id,
    name: "Intro",
    lyrics: "First verse..."
})

// 3. Create Clip
const clip = await axios.post(`${API}/api/v1/clips`, {
    scene_id: scene.data.id,
    name: "Opening shot",
    length: 5.0,
    image_prompt: "cinematic sunrise"
})

// 4. Generate Content
await axios.post(`${API}/api/v1/generation`, {
    clip_id: clip.data.id,
    server_id: "server-uuid",
    prompt: "cinematic sunrise, golden hour",
    model: "flux_dev.safetensors",
    generation_type: "image",
    params: { steps: 28, cfg: 3.5 }
})
```

### Using Character System
```javascript
// Create character
const character = await axios.post(`${API}/api/v1/characters`, {
    name: "Hero",
    description: "Main character",
    reference_images: ["url1", "url2"],
    lora_path: "/models/lora/hero.safetensors"
})

// Apply to clip
await axios.post(
    `${API}/api/v1/characters/${character.id}/apply/${clip.id}`
)
```

### Using Style Templates
```javascript
// Create template
const template = await axios.post(`${API}/api/v1/templates`, {
    name: "Cinematic Look",
    model: "flux_dev.safetensors",
    params: {
        steps: 28,
        cfg: 3.5,
        sampler: "euler"
    }
})

// Use template (increments use count)
await axios.post(`${API}/api/v1/templates/${template.id}/use`)
```

---

## 🔒 Security Best Practices

### Current Implementation
- Environment-based CORS origins
- File upload size limits (50MB music, 10MB images)
- Input validation with Pydantic
- Path traversal prevention
- MongoDB injection prevention

### Recommended Additions (Phase 3)
1. **Authentication**: JWT-based auth
2. **Authorization**: Role-based access control
3. **Rate Limiting**: Request throttling per IP
4. **API Key Encryption**: Encrypt sensitive data at rest
5. **HTTPS**: SSL/TLS in production
6. **Security Headers**: Add security middleware

---

## 📈 Performance Tips

### Backend
1. Add database indexes on frequently queried fields
2. Implement Redis caching for model presets
3. Use connection pooling for MongoDB
4. Add request timeouts
5. Optimize query projections

### Frontend
1. Implement `React.lazy()` for code splitting
2. Use `React Query` for data fetching and caching
3. Add `Zustand` for global state management
4. Optimize re-renders with `useMemo`/`useCallback`
5. Implement virtual scrolling for large lists

---

## 🔗 Important Resources

- **Main Documentation**: [`README.md`](README.md)
- **API Audit**: [`AUDIT_REPORT.md`](AUDIT_REPORT.md)
- **Current Status**: [`docs/CURRENT_STATUS.md`](docs/CURRENT_STATUS.md)
- **Phase Completion**: [`docs/archive/`](docs/archive/)

---

**End of Implementation Guide**  
**Last Updated:** December 2024
