# 🚀 Quick Implementation Guide
## Emergent Storyboard - Developer Reference

**Last Updated:** 2025-10-10

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

# Linux/Mac
./launch.sh

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
│   ├── server.py (1654 lines) - All API logic
│   ├── requirements.txt - Python dependencies
│   ├── .env - Configuration (auto-generated)
│   └── uploads/ - User uploaded files
│
├── frontend/
│   ├── src/
│   │   ├── App.js - Main application
│   │   ├── components/
│   │   │   ├── ProjectView.jsx - Project management
│   │   │   ├── Timeline.jsx - Timeline editor
│   │   │   ├── SceneManager.jsx - Scene/clip management
│   │   │   ├── EnhancedGenerationDialog.jsx - AI generation
│   │   │   ├── ComfyUIManager.jsx - Server management
│   │   │   └── ui/ - 56 Shadcn components
│   │   └── hooks/ - Custom React hooks
│   ├── package.json - Dependencies
│   └── .env - Configuration (auto-generated)
│
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

---

## 🔌 Essential API Endpoints

### Projects
```
POST   /api/projects              # Create
GET    /api/projects              # List all
GET    /api/projects/{id}         # Get one
POST   /api/projects/{id}/upload-music  # Upload audio
```

### Scenes
```
POST   /api/scenes                # Create
GET    /api/projects/{id}/scenes  # List by project
PUT    /api/scenes/{id}           # Update
```

### Clips
```
POST   /api/clips                 # Create
GET    /api/scenes/{id}/clips     # List by scene
PUT    /api/clips/{id}/timeline-position  # Move on timeline
GET    /api/clips/{id}/gallery    # Get generated content
```

### Generation
```
POST   /api/generate              # Generate image/video
POST   /api/upload-face-image     # Upload for face swap
GET    /api/models/presets/{model}  # Get model presets
```

### ComfyUI
```
POST   /api/comfyui/servers       # Add server
GET    /api/comfyui/servers/{id}/info  # Get server status
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

## 🐛 Critical Bugs to Fix

### Priority 1 (High Impact)
1. **MongoDB URL:** Change default from `192.168.1.10` to `localhost` (Line 22)
2. **CORS:** Remove wildcard `*` in production (Line 1640)
3. **Database Connection:** Add error handling (Line 26)
4. **File Upload Limits:** Add size validation (Line 1177)
5. **Timeline Position:** Add Pydantic model validation (Line 1282)

### Priority 2 (Medium Impact)
6. **Clip Update:** Implement missing endpoint (SceneManager.jsx:101)
7. **RunPod Health Check:** Fix false positives (Line 536)
8. **Environment Fallback:** Require explicit production config (App.js:16)

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