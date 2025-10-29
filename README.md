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

## 🛠️ Manual Setup

If you prefer manual setup:

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create backend/.env
MONGO_URL=mongodb://localhost:27017/storycanvas
DB_NAME=storycanvas
CORS_ORIGINS=http://localhost:3000
HOST=localhost
PORT=8001

# Start server
uvicorn server:app --host localhost --port 8001 --reload
```

### Frontend
```bash
cd frontend
npm install  # or yarn install

# Create frontend/.env  
REACT_APP_BACKEND_URL=http://localhost:8001
PORT=3000
HOST=localhost

# Start development server
npm start  # or yarn start
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
├── api/v1/               # Versioned API endpoints
│   ├── projects_router.py
│   ├── scenes_router.py
│   ├── clips_router.py
│   ├── generation_router.py
│   ├── characters_router.py
│   ├── templates_router.py
│   ├── queue_router.py
│   ├── comfyui_router.py
│   └── media_router.py
├── services/             # Business logic layer
│   ├── project_service.py
│   ├── generation_service.py
│   ├── comfyui_service.py
│   ├── queue_manager.py
│   └── export_service.py
├── repositories/         # Data access layer
│   ├── project_repository.py
│   ├── scene_repository.py
│   └── clip_repository.py
├── dtos/                 # Data transfer objects
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
├── components/
│   ├── ProjectView.jsx         # Project management
│   ├── ProjectTimeline.jsx     # Timeline visualization
│   ├── SceneManager.jsx        # Scene/clip editor
│   ├── CharacterManager.jsx    # Character library
│   ├── StyleTemplateLibrary.jsx
│   ├── QueueDashboard.jsx      # Real-time queue
│   ├── GenerationPool.jsx      # Content reuse
│   └── ui/                     # 56 Shadcn components
├── services/             # API client layer
├── hooks/                # Custom React hooks
└── App.js                # Root component
```

**Key Features:**
- Modular component architecture
- Professional dark theme
- Real-time updates with 5-second refresh
- Accessibility with ARIA labels
- Keyboard navigation support

## 📊 Current Status

### ✅ Completed Features
- **Phase 1**: Critical bug fixes and stability (MongoDB, CORS, validation)
- **Phase 2**: Architecture refactoring (service layer, repositories, DTOs, API versioning)
- **Phase 2.5**: Frontend-backend integration (Characters, Templates, Queue Dashboard)
- **Phase 2.6**: Timeline system with alternates
- **Phase 2.7**: Generation pool for content reuse
- All major backend APIs implemented with `/api/v1` versioning
- ComfyUI integration with multi-server support
- Export functionality for professional editors (FCPXML, EDL, DaVinci Resolve)
- Civitai model database integration
- Smart queue management with load balancing

### 🔄 In Progress
- Enhanced model presets system
- Performance optimizations
- Additional export formats

### 📋 Planned
- **Phase 3**: Security & Authentication (JWT, user management, API key encryption)
- **Phase 4**: Additional content features (advanced batch operations)
- **Phase 5**: Frontend improvements (Zustand/Redux, React Query, TypeScript)
- **Phase 6**: Data management (migrations, soft deletes, Redis caching)
- **Phase 7**: Monitoring & analytics (structured logging, metrics, health checks)
- **Phase 8**: Testing & CI/CD (unit, integration, E2E tests)

## 📡 API Structure

### API Endpoints
All endpoints are available in two versions:
- **Legacy**: `/api/<endpoint>` (deprecated, for backward compatibility)
- **Current**: `/api/v1/<endpoint>` (recommended)

### Available Endpoints

#### Projects (`/api/v1/projects`)
- `POST /` - Create project
- `GET /` - List all projects
- `GET /{id}` - Get project details
- `GET /{id}/with-scenes` - Get project with full scene hierarchy
- `PUT /{id}` - Update project
- `DELETE /{id}` - Delete project
- `GET /{id}/clips` - List all clips in project
- `GET /{id}/export/fcpxml` - Export to Final Cut Pro
- `GET /{id}/export/edl` - Export to Adobe Premiere
- `GET /{id}/export/resolve` - Export to DaVinci Resolve
- `GET /{id}/export/json` - Export as JSON

#### Scenes (`/api/v1/scenes`)
- `POST /` - Create scene
- `GET /project/{project_id}` - List scenes in project
- `GET /{id}` - Get scene details
- `PUT /{id}` - Update scene
- `DELETE /{id}` - Delete scene
- `GET /{id}/timeline-analysis` - Analyze scene timeline

#### Clips (`/api/v1/clips`)
- `POST /` - Create clip
- `GET /scene/{scene_id}` - List clips in scene
- `GET /{id}` - Get clip details
- `GET /{id}/gallery` - Get generated content gallery
- `PUT /{id}` - Update clip
- `PUT /{id}/timeline-position` - Update timeline position
- `PUT /{id}/prompts` - Update prompts
- `DELETE /{id}` - Delete clip

#### Generation (`/api/v1/generation`)
- `POST /` - Generate image/video for clip
- `POST /batch` - Start batch generation
- `GET /batch/{id}` - Get batch status
- `GET /batches` - List all batches

#### Characters (`/api/v1/characters`)
- `POST /` - Create character
- `GET /` - List characters (with project filter)
- `GET /{id}` - Get character details
- `PUT /{id}` - Update character
- `DELETE /{id}` - Delete character
- `POST /{id}/apply/{clip_id}` - Apply character to clip

#### Style Templates (`/api/v1/templates`)
- `POST /` - Create template
- `GET /` - List all templates
- `GET /{id}` - Get template details
- `PUT /{id}` - Update template
- `DELETE /{id}` - Delete template
- `POST /{id}/use` - Increment use count

#### Queue (`/api/v1/queue`)
- `POST /jobs` - Add generation job
- `GET /jobs` - List all jobs
- `GET /jobs/{id}` - Get job status
- `GET /status` - Get queue status
- `GET /projects/{id}/jobs` - Get project jobs
- `POST /servers/{id}/register` - Register ComfyUI server
- `GET /servers/{id}/next` - Get next job for server
- `POST /jobs/{id}/complete` - Mark job complete

#### ComfyUI Servers (`/api/v1/comfyui`)
- `POST /servers` - Add server
- `GET /servers` - List servers
- `GET /servers/{id}/info` - Get server status
- `PUT /servers/{id}` - Update server
- `DELETE /servers/{id}` - Delete server

#### Media (`/api/v1/media`)
- `POST /projects/{id}/upload-music` - Upload music file
- `POST /upload-face-image` - Upload face image for reactor

#### Health (`/api/v1/health`)
- `GET /` - API root status
- `GET /health` - Comprehensive health check

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
│   ├── api/v1/               # Versioned API routers
│   ├── services/             # Business logic
│   ├── repositories/         # Data access
│   ├── dtos/                 # Data transfer objects
│   ├── models/               # Pydantic models
│   ├── utils/                # Utilities
│   ├── database.py           # Database manager
│   ├── server.py             # Main application
│   ├── requirements.txt
│   └── .env                  # Created by launch script
├── frontend/                 # React frontend  
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client layer
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
└── AUDIT_REPORT.md
```

## 🔧 Development

- **Backend**: FastAPI + MongoDB (Motor) + aiohttp
- **Frontend**: React + Shadcn UI + React DnD
- **ComfyUI**: Direct API integration + RunPod serverless support
- **Architecture**: Service layer + Repository pattern + DTOs + API versioning

## 📸 Screenshots

The app features a professional dark theme with:
- Modern sidebar navigation
- Project cards with metadata
- Timeline editor with drag-and-drop clips
- ComfyUI server management
- Generation dialogs with parameter controls
- Character and template libraries
- Queue management dashboard
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
