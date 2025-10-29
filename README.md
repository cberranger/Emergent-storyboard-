# 🎬 StoryCanvas - AI Storyboarding App

A professional storyboarding application with ComfyUI integration for AI-powered image and video generation.

## 🚀 Quick Start (Windows)

### Option 1: PowerShell (Recommended)
```powershell
.\launch.ps1
```

### Option 2: Batch File
```cmd
launch.bat
```

Both scripts will:
- Ask for frontend/backend ports (defaults: frontend=3000, backend=8001)
- Create proper `.env` files
- Install dependencies
- Start both frontend and backend servers

## 📋 Prerequisites

### Required:
- **Node.js** (v16+) - [Download](https://nodejs.org/)
- **Python** (3.8+) - [Download](https://python.org/downloads/)
- **MongoDB** - [Download Community Server](https://www.mongodb.com/try/download/community)

### Optional:
- **Yarn** (recommended over npm)
- **Git** (for cloning)

## 🔗 ComfyUI Integration

### Local ComfyUI
If running ComfyUI locally (e.g., Unraid Docker):
```
http://192.168.1.10:7820  # Example local IP:port
```

### RunPod Serverless
For RunPod endpoints:
```
https://api.runpod.ai/v2/your-endpoint-id
```
*Requires API key*

### Ngrok Tunnel
To expose local ComfyUI publicly:
```bash
# Install ngrok
winget install ngrok

# Expose ComfyUI (assuming port 8188)
ngrok http 8188

# Use the provided https URL in StoryCanvas
```

## 🎯 Features

### Core Functionality
- **Project Management**: Create and organize storyboard projects
- **Scene & Clip System**: Hierarchical structure for complex storyboards
- **Timeline Editor**: Professional drag-and-drop timeline with alternates support
- **ComfyUI Integration**: Support for standard ComfyUI and RunPod serverless
- **Multi-Server Support**: Connect multiple ComfyUI instances with load balancing
- **Music Upload**: Upload audio for music video projects
- **Version Control**: Multiple versions per clip with comparison

### Advanced Features
- **Character Management**: Create and apply consistent characters across clips
- **Style Templates**: Save and reuse generation parameters
- **Queue Management**: Smart queue with load balancing across servers
- **Batch Generation**: Generate multiple clips simultaneously
- **Export Formats**: Final Cut Pro XML, Adobe Premiere EDL, DaVinci Resolve
- **Generation Pool**: Shared library for reusing generated content
- **Presentation Mode**: Full-screen storyboard presentations
- **Hotkey System**: 40+ keyboard shortcuts for power users
- **Civitai Integration**: Sync models with Civitai database
- **Model Presets**: Default presets for all major model types

### Model Support
- **SDXL**: Full support with custom presets
- **Flux**: Flux Dev, Flux Schnell, Flux Pro variants
- **Pony Diffusion**: Optimized presets
- **Illustrious**: Professional anime presets
- **Wan 2.1/2.2**: Video generation presets
- **LTX-Video**: Lightning-fast video generation
- **Hunyuan Video**: Tencent's video model
- **Qwen Image**: Alibaba's image models
- **And more**: Extensible preset system for new models

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── api/v1/               # Versioned API endpoints (11 routers, 61 endpoints)
│   ├── projects_router.py      # 7 endpoints
│   ├── scenes_router.py        # 6 endpoints
│   ├── clips_router.py         # 8 endpoints
│   ├── generation_router.py    # 4 endpoints
│   ├── characters_router.py    # 6 endpoints
│   ├── templates_router.py     # 6 endpoints
│   ├── queue_router.py         # 12 endpoints
│   ├── comfyui_router.py       # 5 endpoints
│   ├── media_router.py         # 2 endpoints
│   ├── health_router.py        # 2 endpoints
│   └── openai_router.py        # 3 endpoints
├── services/             # Business logic layer (10+ services)
│   ├── project_service.py
│   ├── generation_service.py
│   ├── comfyui_service.py
│   ├── queue_manager.py
│   ├── export_service.py
│   ├── batch_generator.py
│   ├── gallery_manager.py
│   ├── media_service.py
│   ├── model_config.py
│   └── openai_video_service.py
├── repositories/         # Data access layer
│   ├── base_repository.py
│   ├── project_repository.py
│   ├── scene_repository.py
│   ├── clip_repository.py
│   └── comfyui_repository.py
├── dtos/                 # Data transfer objects (42+ classes)
│   ├── project_dto.py
│   ├── scene_dto.py
│   ├── clip_dto.py
│   ├── generation_dto.py
│   ├── character_dto.py
│   ├── template_dto.py
│   └── queue_dto.py
├── models/               # Pydantic models
└── server.py             # Main application
```

**Key Features:**
- Clean separation of concerns (routes → services → repositories)
- API Versioning: `/api/v1` endpoints with backward compatibility on `/api`
- Dependency injection for database and services
- Comprehensive error handling with standardized responses
- Smart queue management with multi-server load balancing

### Frontend (React)
```
frontend/src/
├── components/           # 76 total components
│   ├── Main Components/ (30 components)
│   │   ├── ProjectView.jsx             # Project management
│   │   ├── ProjectDashboard.jsx        # Project stats & overview
│   │   ├── ProjectTimeline.jsx         # Timeline visualization
│   │   ├── SceneManager.jsx            # Scene/clip editor
│   │   ├── CharacterManager.jsx        # Character library
│   │   ├── StyleTemplateLibrary.jsx    # Template management
│   │   ├── QueueDashboard.jsx          # Queue monitoring
│   │   ├── GenerationPool.jsx          # Content reuse library
│   │   ├── EnhancedGenerationDialog.jsx
│   │   ├── BatchGenerationDialog.jsx
│   │   ├── ComfyUIManager.jsx
│   │   ├── ModelBrowser.jsx
│   │   ├── PresentationMode.jsx
│   │   ├── Timeline.jsx                # Drag-drop timeline
│   │   ├── UnifiedTimeline.jsx
│   │   ├── ExportDialog.jsx
│   │   ├── HotkeyHelpDialog.jsx
│   │   ├── MediaViewerDialog.jsx
│   │   ├── FaceFusionProcessor.jsx
│   │   ├── AdvancedCharacterCreator.jsx
│   │   └── ... (10 more)
│   └── ui/              (46 Shadcn components)
│       ├── button.jsx, card.jsx, dialog.jsx
│       ├── dropdown-menu.jsx, select.jsx
│       ├── toast.jsx, table.jsx, tabs.jsx
│       └── ... (38 more UI primitives)
├── services/             # API client layer (8 services)
│   ├── ProjectService.js
│   ├── SceneService.js
│   ├── ClipService.js
│   ├── GenerationService.js
│   ├── CharacterService.js
│   ├── TemplateService.js
│   ├── QueueService.js
│   └── ComfyUIService.js
├── hooks/                # Custom React hooks
└── App.js                # Root component
```

**Key Features:**
- 76 professional React components (30 feature components + 46 UI components)
- Modular service layer for API communication
- Professional dark theme with accessibility
- Real-time updates with 5-second refresh
- Keyboard navigation support

## 📊 Current Status

### ✅ Completed Features
- **Phase 1**: Critical bug fixes and stability (MongoDB, CORS, validation)
- **Phase 2**: Architecture refactoring (service layer, repositories, DTOs, API versioning)
- **Phase 2.5**: Frontend-backend integration (Characters, Templates, Queue Dashboard, Project Dashboard)
- **Phase 2.6**: Timeline system with alternates
- **Phase 2.7**: Generation pool for content reuse
- All major backend APIs implemented with `/api/v1` versioning (61 endpoints)
- ComfyUI integration with multi-server support
- Export functionality for professional editors (FCPXML, EDL, DaVinci Resolve) via legacy endpoints
- Civitai model database integration
- Smart queue management with load balancing

### 🔄 In Progress
- Enhanced model presets system
- Performance optimizations
- Additional export formats

### 📋 Planned
- **Phase 3**: Security & Authentication (JWT, user management, API key encryption)
- **Phase 4**: Additional content features (advanced batch operations UI completion)
- **Phase 5**: Frontend improvements (Zustand/Redux, React Query, TypeScript)
- **Phase 6**: Data management (migrations, soft deletes, Redis caching)
- **Phase 7**: Monitoring & analytics (structured logging, metrics, health checks)
- **Phase 8**: Testing & CI/CD (unit, integration, E2E tests)

## 📡 API Structure

### API Endpoints
All endpoints are available in two versions:
- **Legacy**: `/api/<endpoint>` (deprecated, for backward compatibility)
- **Current**: `/api/v1/<endpoint>` (recommended)

**Total Endpoints**: 61 versioned endpoints + 4 legacy export endpoints = 65 total

### Available Endpoints

#### Health (`/api/v1/health`) - 2 endpoints
- `GET /` - API root status
- `GET /health` - Comprehensive health check

#### Projects (`/api/v1/projects`) - 7 endpoints
- `POST /` - Create project
- `GET /` - List all projects
- `GET /{id}` - Get project details
- `GET /{id}/with-scenes` - Get project with full scene hierarchy
- `PUT /{id}` - Update project
- `DELETE /{id}` - Delete project
- `GET /{id}/clips` - List all clips in project

#### Project Export (Legacy `/api/projects/{id}/export/`) - 4 endpoints
- `GET /fcpxml` - Export to Final Cut Pro
- `GET /edl` - Export to Adobe Premiere
- `GET /resolve` - Export to DaVinci Resolve
- `GET /json` - Export as JSON

#### Scenes (`/api/v1/scenes`) - 6 endpoints
- `POST /` - Create scene
- `GET /project/{project_id}` - List scenes in project
- `GET /{id}` - Get scene details
- `PUT /{id}` - Update scene
- `DELETE /{id}` - Delete scene
- `GET /{id}/timeline-analysis` - Analyze scene timeline

#### Clips (`/api/v1/clips`) - 8 endpoints
- `POST /` - Create clip
- `GET /scene/{scene_id}` - List clips in scene
- `GET /{id}` - Get clip details
- `GET /{id}/gallery` - Get generated content gallery
- `PUT /{id}` - Update clip
- `PUT /{id}/timeline-position` - Update timeline position
- `PUT /{id}/prompts` - Update prompts
- `DELETE /{id}` - Delete clip

#### Generation (`/api/v1/generation`) - 4 endpoints
- `POST /` - Generate image/video for clip
- `POST /batch` - Start batch generation
- `GET /batch/{id}` - Get batch status
- `GET /batches` - List all batches

#### Characters (`/api/v1/characters`) - 6 endpoints
- `POST /` - Create character
- `GET /` - List characters (with project filter)
- `GET /{id}` - Get character details
- `PUT /{id}` - Update character
- `DELETE /{id}` - Delete character
- `POST /{id}/apply/{clip_id}` - Apply character to clip

#### Style Templates (`/api/v1/templates`) - 6 endpoints
- `POST /` - Create template
- `GET /` - List all templates
- `GET /{id}` - Get template details
- `PUT /{id}` - Update template
- `DELETE /{id}` - Delete template
- `POST /{id}/use` - Increment use count

#### Queue (`/api/v1/queue`) - 12 endpoints
- `POST /jobs` - Add generation job
- `GET /jobs` - List all jobs
- `GET /jobs/{id}` - Get job status
- `GET /status` - Get queue status
- `GET /projects/{id}/jobs` - Get project jobs
- `POST /servers/{id}/register` - Register ComfyUI server
- `GET /servers/{id}/next` - Get next job for server
- `POST /jobs/{id}/complete` - Mark job complete
- `POST /jobs/{id}/cancel` - Cancel job
- `POST /jobs/{id}/retry` - Retry failed job
- `DELETE /jobs/{id}` - Delete job
- `DELETE /clear` - Clear completed/failed jobs

#### ComfyUI Servers (`/api/v1/comfyui`) - 5 endpoints
- `POST /servers` - Add server
- `GET /servers` - List servers
- `GET /servers/{id}/info` - Get server status
- `PUT /servers/{id}` - Update server
- `DELETE /servers/{id}` - Delete server

#### Media (`/api/v1/media`) - 2 endpoints
- `POST /projects/{id}/upload-music` - Upload music file
- `POST /upload-face-image` - Upload face image for reactor

#### OpenAI (`/api/v1/openai`) - 3 endpoints
- `GET /videos/{id}` - Get OpenAI video details
- `GET /videos` - List OpenAI videos
- `DELETE /videos/{id}` - Delete OpenAI video

## 🐛 Troubleshooting

### MongoDB Issues
- **Windows**: Install MongoDB Community Server or use MongoDB Atlas
- **Check if running**: Task Manager → Look for `mongod.exe`
- **Alternative**: Use MongoDB Atlas (cloud) and update MONGO_URL in backend/.env

### Port Conflicts
- Change ports in launch script when prompted
- Default ports: Frontend=3000, Backend=8001

### ComfyUI Connection Issues
- Ensure ComfyUI is accessible from your network
- For Docker/Unraid: Check port forwarding and `--listen 0.0.0.0` flag
- Use ngrok for external access

### Environment Variables
- If API calls show "undefined", restart the frontend server
- Check that `.env` files were created properly
- Verify `REACT_APP_BACKEND_URL` matches backend URL

## 📁 Project Structure

```
storycanvas/
├── backend/                  # FastAPI backend
│   ├── api/v1/               # Versioned API routers (11 routers, 61 endpoints)
│   ├── services/             # Business logic (10+ services)
│   ├── repositories/         # Data access (4 repositories)
│   ├── dtos/                 # Data transfer objects (42+ classes)
│   ├── models/               # Pydantic models
│   ├── utils/                # Utilities
│   ├── database.py           # Database manager
│   ├── server.py             # Main application
│   ├── requirements.txt
│   └── .env                  # Created by launch script
├── frontend/                 # React frontend  
│   ├── src/
│   │   ├── components/       # 76 React components (30 feature + 46 UI)
│   │   ├── services/         # API client layer (8 services)
│   │   ├── hooks/            # Custom hooks
│   │   └── App.js
│   ├── package.json
│   └── .env                  # Created by launch script
├── docs/                     # Documentation
│   ├── archive/              # Completed phase docs
│   ├── CURRENT_STATUS.md
│   ├── CHARACTER_CREATION_BEST_PRACTICES.md
│   └── FACEFUSION_INTEGRATION.md
├── launch.ps1                # PowerShell launcher
├── launch.bat                # Batch launcher
├── README.md
├── IMPLEMENTATION_GUIDE.md
├── AUDIT_REPORT.md
└── TASKS_MASTER_LIST.md
```

## 🔧 Development

- **Backend**: FastAPI + MongoDB (Motor) + aiohttp
- **Frontend**: React + Shadcn UI (46 components) + React DnD
- **ComfyUI**: Direct API integration + RunPod serverless support
- **Architecture**: Service layer + Repository pattern + DTOs + API versioning

## 📸 Screenshots

The app features a professional dark theme with:
- Modern sidebar navigation (7 main sections)
- Project cards with metadata
- Timeline editor with drag-and-drop clips
- ComfyUI server management
- Generation dialogs with parameter controls
- Character and template libraries
- Queue management dashboard
- Generation pool for content reuse
- Project dashboard with statistics
- Export functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Built for professional storyboarding and music video production workflows.*
*76 React components | 61 API endpoints | 10+ backend services | 42+ DTOs*
