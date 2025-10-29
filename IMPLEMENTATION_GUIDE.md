# 🚀 Quick Implementation Guide
## Emergent Storyboard - Developer Reference

**Last Updated:** 2025-10-29

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

## 📋 Project Structure Quick Reference

```
emergent-storyboard/
├── backend/
│   ├── server.py (5212 lines) - Main API server
│   ├── services/ - Business logic layer
│   │   ├── project_service.py
│   │   ├── generation_service.py
│   │   ├── comfyui_service.py
│   │   └── media_service.py
│   ├── repositories/ - Data access layer
│   │   ├── base_repository.py
│   │   ├── project_repository.py
│   │   ├── scene_repository.py
│   │   └── clip_repository.py
│   ├── models/ - Pydantic models
│   ├── utils/ - Utilities and helpers
│   ├── requirements.txt - Python dependencies
│   ├── .env - Configuration (auto-generated)
│   └── uploads/ - User uploaded files
│
├── frontend/
│   ├── src/
│   │   ├── App.js - Main application router
│   │   ├── components/
│   │   │   ├── ProjectView.jsx - Project management
│   │   │   ├── Timeline.jsx - Timeline editor
│   │   │   ├── ProjectTimeline.jsx - Project-level timeline
│   │   │   ├── SceneManager.jsx - Scene/clip management
│   │   │   ├── EnhancedGenerationDialog.jsx - AI generation
│   │   │   ├── ComfyUIManager.jsx - Server management
│   │   │   ├── CharacterManager.jsx - Character library
│   │   │   ├── StyleTemplateLibrary.jsx - Template library
│   │   │   ├── QueueDashboard.jsx - Queue monitoring
│   │   │   ├── ProjectDashboard.jsx - Project details
│   │   │   ├── GenerationPool.jsx - Content reuse library
│   │   │   ├── PresentationMode.jsx - Full-screen presentations
│   │   │   └── ui/ - 56 Shadcn components
│   │   ├── services/ - API service layer
│   │   ├── hooks/ - Custom React hooks
│   │   └── utils/ - Frontend utilities
│   ├── package.json - Node dependencies
│   └── .env - Frontend configuration
│
├── docs/
│   ├── archive/ - Completed phase documentation
│   ├── CURRENT_STATUS.md - Current application state
│   ├── CHARACTER_CREATION_BEST_PRACTICES.md
│   └── FACEFUSION_INTEGRATION.md
│
├── launch.ps1 - PowerShell launcher
├── launch.bat - Batch launcher
└── README.md - Project documentation
└── launch.ps1/sh/bat - Launch scripts
```

---

## 🔑 Key Files & Their Purpose

### Backend - server.py
| Lines | Purpose |
|-------|---------|
| 1-40 | Configuration & setup |
| 41-173 | Pydantic data models |
| 174-447 | AI model presets (9 model types) |
| 491-1105 | ComfyUI client (API communication) |
| 1107-1631 | API route handlers (25 endpoints) |

### Frontend Components
| File | Lines | Purpose |
|------|-------|---------|
| App.js | 138 | Root component, routing |
| ProjectView.jsx | 188 | Project CRUD interface |
| Timeline.jsx | 559 | Drag-drop timeline editor |
| SceneManager.jsx | 417 | Scene/clip management |
| EnhancedGenerationDialog.jsx | 1190 | AI generation interface |
| ComfyUIManager.jsx | 341 | Server configuration |

---

## 🗄️ Data Models

### Core Entities
```
Project (1) ──> (N) Scene (1) ──> (N) Clip
                                      │
                                      └──> GeneratedContent[]
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

## 🔌 Essential API Endpoints

### Projects
```
POST   /api/projects              # Create
GET    /api/projects              # List all
GET    /api/projects/{id}         # Get one
PUT    /api/projects/{id}         # Update
DELETE /api/projects/{id}         # Delete
POST   /api/projects/{id}/upload-music  # Upload audio
GET    /api/projects/{id}/export/fcpxml   # Export FCPXML
GET    /api/projects/{id}/export/edl     # Export EDL
GET    /api/projects/{id}/export/resolve # Export DaVinci
GET    /api/projects/{id}/export/json    # Export JSON
```

### Scenes
```
POST   /api/scenes                # Create
GET    /api/projects/{id}/scenes  # List by project
GET    /api/scenes/{id}           # Get one
PUT    /api/scenes/{id}           # Update
POST   /api/scenes/{id}/create-alternate # Create alternate
```

### Clips
```
POST   /api/clips                 # Create
GET    /api/scenes/{id}/clips     # List by scene
GET    /api/clips/{id}            # Get one
PUT    /api/clips/{id}            # Update
PUT    /api/clips/{id}/timeline-position  # Move on timeline
PUT    /api/clips/{id}/prompts    # Update prompts
GET    /api/clips/{id}/gallery    # Get generated content
PUT    /api/clips/{id}/select-content    # Select image/video
POST   /api/clips/{id}/create-alternate  # Create alternate
```

### Generation
```
POST   /api/generate              # Generate image/video
POST   /api/generate/batch        # Batch generation
GET    /api/generate/batch/{id}   # Get batch status
GET    /api/generate/batches      # List batches
POST   /api/upload-face-image     # Upload for face swap
GET    /api/models/presets/{model}  # Get model presets
GET    /api/models/parameters/{model}  # Get model parameters
```

### Characters
```
POST   /api/characters            # Create
GET    /api/characters            # List (with project filter)
GET    /api/characters/{id}       # Get one
PUT    /api/characters/{id}       # Update
DELETE /api/characters/{id}       # Delete
POST   /api/characters/{id}/apply/{clip_id}  # Apply to clip
```

### Style Templates
```
POST   /api/style-templates       # Create
GET    /api/style-templates       # List
GET    /api/style-templates/{id}  # Get one
PUT    /api/style-templates/{id}  # Update
DELETE /api/style-templates/{id}  # Delete
POST   /api/style-templates/{id}/use  # Increment use count
```

### Queue Management
```
POST   /api/queue/jobs             # Add job
GET    /api/queue/status          # Queue status
GET    /api/queue/jobs/{id}       # Job status
GET    /api/queue/jobs            # All jobs
GET    /api/queue/projects/{id}/jobs  # Project jobs
POST   /api/queue/servers/{id}/register  # Register server
GET    /api/queue/servers/{id}/next  # Get next job
POST   /api/queue/jobs/{id}/complete  # Mark complete
```

### Generation Pool
```
POST   /api/pool                  # Create pool item
GET    /api/pool/{project_id}     # List project pool
GET    /api/pool/item/{id}        # Get pool item
PUT    /api/pool/item/{id}        # Update pool item
DELETE /api/pool/item/{id}        # Delete pool item
POST   /api/pool/item/{id}/apply-to-clip/{clip_id}  # Apply to clip
```

### ComfyUI
```
POST   /api/comfyui/servers       # Add server
GET    /api/comfyui/servers       # List servers
GET    /api/comfyui/servers/{id}/info  # Get server status
DELETE /api/comfyui/servers/{id}  # Delete server
POST   /api/servers/{id}/sync-models  # Sync models
```

### Health
```
GET    /api/health                # Health check
GET    /api/v1/health             # Health check (v1)
```

---

## 🎨 Supported AI Models

| Model Type | Fast Steps | Quality Steps | Special Features |
|------------|------------|---------------|------------------|
| flux_dev | 8 | 28 | LoRA (max 3) |
| flux_krea | 4 | 8 | Ultra-fast |
| sdxl | 15 | 35 | Refiner, LoRA (max 5) |
| pony | 12 | 28 | Style-focused |
| wan_2_1 | 15 | 25 | 512x512, special VAE |
| wan_2_2 | 8 | 20 | 768x768, dual models |
| hidream | 12 | 25 | Balanced |
| qwen_image | 10 | 20 | Text rendering |
| qwen_edit | 8 | 15 | Image editing |

---

## 🛠️ Common Development Tasks

### 1. Add New API Endpoint

**Backend:**
```python
# server.py
@api_router.post("/my-endpoint")
async def my_handler(data: MyModel):
    result = await db.collection.insert_one(data.dict())
    return {"success": True}
```

**Frontend:**
```javascript
const response = await axios.post(`${API}/my-endpoint`, data)
```

### 2. Add New Component

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
# server.py - Add to MODEL_DEFAULTS
"new_model": {
    "fast": {
        "steps": 10,
        "cfg": 5.0,
        "width": 1024,
        "height": 1024,
        "sampler": "euler",
        "scheduler": "normal"
    },
    "quality": {/* higher values */}
}

# Update detect_model_type()
if "newmodel" in model_name.lower():
    return "new_model"
```

---

## 🐛 Recently Fixed Issues (October 29, 2025)

### ✅ Fixed Critical Bugs
1. **MongoDB URL:** Changed default from `192.168.1.10` to `localhost`
2. **CORS:** Configured proper environment-based origins
3. **Database Connection:** Added retry logic and error handling
4. **File Upload Limits:** Added size validation (50MB music, 10MB images)
5. **Timeline Position:** Added Pydantic model validation with overlap detection
6. **Clip Update:** Implemented complete PUT endpoint
7. **RunPod Health Check:** Fixed endpoint status checking
8. **Environment Variables:** Removed fallback, require explicit config
9. **DialogContent Accessibility:** Added proper descriptions for dialogs
10. **handleRefreshServer Error:** Fixed undefined function reference

### Current Status
- No critical bugs remaining
- All major functionality operational
- Frontend and backend stable

---

## 🔒 Security Checklist

- [ ] Add authentication system (JWT recommended)
- [ ] Encrypt API keys at rest
- [ ] Implement rate limiting
- [ ] Add input sanitization
- [ ] Configure proper CORS
- [ ] Add request validation
- [ ] Implement HTTPS in production
- [ ] Add security headers

---

## 📊 Performance Optimization Tips

1. **Backend:**
   - Add database indexes on `id`, `project_id`, `scene_id`
   - Implement caching for model presets
   - Use connection pooling for MongoDB
   - Add request timeout limits

2. **Frontend:**
   - Implement React.lazy() for code splitting
   - Use React Query for data fetching
   - Add Zustand/Redux for state management
   - Optimize re-renders with useMemo/useCallback

---

## 🧪 Testing Strategy

### Backend Tests
```python
# tests/test_api.py
def test_create_project():
    response = client.post("/api/projects", json={
        "name": "Test",
        "description": "Test"
    })
    assert response.status_code == 200
```

### Frontend Tests
```javascript
// __tests__/Timeline.test.js
test('renders timeline', () => {
    render(<Timeline project={mockProject} />)
    expect(screen.getByTestId('timeline-track')).toBeInTheDocument()
})
```

### E2E Tests
```javascript
// e2e/workflow.spec.js
test('complete project workflow', async ({ page }) => {
    await page.goto('http://localhost:3000')
    await page.click('[data-testid="create-project-btn"]')
    // ... test complete workflow
})
```

---

## 📈 Monitoring & Logging

### Add Health Endpoint
```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "db": await check_db(),
        "timestamp": datetime.now()
    }
```

### Structured Logging
```python
import structlog
logger = structlog.get_logger()
logger.info("generation.started", clip_id=clip_id)
```

---

## 🚀 Deployment Checklist

### Backend
- [ ] Set production MongoDB URL
- [ ] Configure proper CORS origins
- [ ] Set environment to production
- [ ] Add error tracking (Sentry)
- [ ] Configure logging
- [ ] Set up backups
- [ ] Add health checks
- [ ] Configure SSL

### Frontend
- [ ] Build production bundle: `npm run build`
- [ ] Set REACT_APP_BACKEND_URL
- [ ] Configure CDN for static assets
- [ ] Add error boundaries
- [ ] Enable source maps
- [ ] Configure analytics

---

## 💡 Feature Ideas (Quick Reference)

### High Impact, Low Effort
1. Batch generation (generate multiple clips at once)
2. Template library (save/reuse generation settings)
3. Keyboard shortcuts
4. Undo/redo system
5. Export to video editor formats

### High Impact, Medium Effort
6. Real-time collaboration (WebSockets)
7. Version control for generations (Git-like)
8. AI prompt enhancement (GPT-4 integration)
9. Asset library (shared characters/LoRAs)
10. Mobile companion app

### High Impact, High Effort
11. Auto lip-sync with audio
12. AI scene analyzer (music → scene breakdown)
13. Visual style consistency across clips
14. Custom workflow builder
15. Plugin system for extensions

---

## 🔗 Important Links

- **Main Audit:** [`AUDIT_REPORT.md`](AUDIT_REPORT.md)
- **API Reference:** All endpoints in server.py lines 1107-1631
- **Component Docs:** [`frontend/src/components/`](frontend/src/components/)
- **Model Configs:** [`backend/server.py:175-446`](backend/server.py:175-446)

---

## 🆘 Troubleshooting

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
1. Check REACT_APP_BACKEND_URL in frontend/.env
2. Verify backend is running on correct port
3. Check CORS configuration
4. Clear browser cache

### Generation Fails
1. Verify ComfyUI server is accessible
2. Check model name matches exactly
3. Ensure LoRA files exist on server
4. Review generation parameters for model type

---

## 📚 Code Examples

### Complete Workflow Example
```javascript
// 1. Create Project
const project = await axios.post(`${API}/projects`, {
    name: "Music Video",
    description: "My awesome video"
})

// 2. Create Scene
const scene = await axios.post(`${API}/scenes`, {
    project_id: project.data.id,
    name: "Intro",
    lyrics: "First verse..."
})

// 3. Create Clip
const clip = await axios.post(`${API}/clips`, {
    scene_id: scene.data.id,
    name: "Opening shot",
    length: 5.0,
    image_prompt: "cinematic sunrise"
})

// 4. Generate Content
await axios.post(`${API}/generate`, {
    clip_id: clip.data.id,
    server_id: "server-uuid",
    prompt: "cinematic sunrise, golden hour",
    model: "flux_dev.safetensors",
    generation_type: "image",
    params: { steps: 28, cfg: 3.5 }
})
```

---

**End of Implementation Guide**  
**For detailed audit:** See [`AUDIT_REPORT.md`](AUDIT_REPORT.md)  
**Generated:** 2025-10-10