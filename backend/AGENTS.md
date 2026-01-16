# Backend - Development Guide

> ⚠️ **AGENT NOTICE**: Read [../AGENT_RULES.md](../AGENT_RULES.md) first. Follow TASKS.md exactly.

## Overview

The backend is a FastAPI-based REST API server providing comprehensive functionality for AI-powered storyboarding applications. It handles project management, scene and clip editing, AI content generation through ComfyUI integration, queue management with intelligent load balancing across multiple servers, character and style template management, and export to professional video editing formats (Final Cut Pro XML, Adobe Premiere EDL, DaVinci Resolve). The architecture implements clean separation of concerns with service layer abstraction, repository pattern for data access, comprehensive DTO validation, and versioned API endpoints for future compatibility.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                         │
├─────────────────────────────────────────────────────────────────┤
│  API Layer (api/v1/)                                         │
│  ├─ projects_router.py     (7 endpoints)                     │
│  ├─ scenes_router.py       (6 endpoints)                     │
│  ├─ clips_router.py        (8 endpoints)                     │
│  ├─ generation_router.py   (4 endpoints)                     │
│  ├─ characters_router.py   (6 endpoints)                     │
│  ├─ templates_router.py    (6 endpoints)                     │
│  ├─ queue_router.py        (12 endpoints)                    │
│  ├─ comfyui_router.py      (5 endpoints)                     │
│  ├─ media_router.py        (2 endpoints)                     │
│  ├─ health_router.py       (2 endpoints)                     │
│  └─ openai_router.py      (3 endpoints)                     │
├─────────────────────────────────────────────────────────────────┤
│  Service Layer (services/)                                    │
│  ├─ project_service.py     - Project & scene operations        │
│  ├─ generation_service.py  - Generation workflows              │
│  ├─ comfyui_service.py     - ComfyUI client & integration   │
│  ├─ queue_manager.py       - Intelligent queue & load balancer  │
│  ├─ export_service.py      - Export formats (FCPXML, EDL)   │
│  ├─ batch_generator.py     - Batch generation logic            │
│  ├─ gallery_manager.py     - Generated content management       │
│  ├─ media_service.py       - File upload & validation         │
│  ├─ model_config.py       - Model presets (13+ models)       │
│  └─ openai_video_service.py - OpenAI integration            │
├─────────────────────────────────────────────────────────────────┤
│  Repository Layer (repositories/)                              │
│  ├─ base_repository.py    - Generic CRUD operations          │
│  ├─ project_repository.py - Project data access             │
│  ├─ scene_repository.py   - Scene data access              │
│  ├─ clip_repository.py    - Clip data access               │
│  └─ comfyui_repository.py - ComfyUI server data access    │
├─────────────────────────────────────────────────────────────────┤
│  Data Transfer Objects (dtos/)                                 │
│  ├─ project_dto.py       (Project CRUD DTOs)               │
│  ├─ scene_dto.py         (Scene CRUD DTOs)                 │
│  ├─ clip_dto.py          (Clip CRUD DTOs)                  │
│  ├─ generation_dto.py    (Generation & batch DTOs)          │
│  ├─ character_dto.py     (Character CRUD & apply DTOs)      │
│  ├─ template_dto.py      (Template CRUD & use DTOs)        │
│  └─ queue_dto.py         (Queue job & status DTOs)          │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                   │
│  ├─ MongoDB (Motor)     - Async NoSQL database              │
│  ├─ collections/         - Projects, scenes, clips, etc.    │
│  └─ indexes/            - Query optimization                │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Aspect | Choice | Notes |
|--------|--------|-------|
| **Language** | Python 3.8+ | Async/await support |
| **Framework** | FastAPI | High performance, automatic docs, type validation |
| **Database** | MongoDB with Motor | Flexible schema for complex nested structures |
| **Validation** | Pydantic | Request/response validation, data models |
| **HTTP Client** | aiohttp | Async HTTP requests for ComfyUI/OpenAI |
| **File Uploads** | FastAPI UploadFile | Native multipart handling |
| **API Versioning** | Custom router prefix | `/api/v1` endpoints with backward compatibility |

## Key Classes/Modules

| Class | Purpose | Location |
|-------|---------|----------|
| `ProjectService` | Project/scene business logic | `backend/services/project_service.py` |
| `GenerationService` | Generation workflows & coordination | `backend/services/generation_service.py` |
| `ComfyUIService` | ComfyUI client, server management | `backend/services/comfyui_service.py` |
| `QueueManager` | Intelligent queue & load balancing | `backend/services/queue_manager.py` |
| `ExportService` | FCPXML, EDL, DaVinci Resolve export | `backend/services/export_service.py` |
| `BatchGenerator` | Concurrent batch generation | `backend/services/batch_generator.py` |
| `GalleryManager` | Generated content gallery updates | `backend/services/gallery_manager.py` |
| `MediaService` | File upload validation & storage | `backend/services/media_service.py` |
| `ModelConfig` | Model presets (13+ AI models) | `backend/services/model_config.py` |
| `BaseRepository` | Generic async CRUD operations | `backend/repositories/base_repository.py` |
| `ProjectRepository` | Project-specific queries | `backend/repositories/project_repository.py` |
| `SceneRepository` | Scene retrieval with ordering | `backend/repositories/scene_repository.py` |
| `ClipRepository` | Clip operations & gallery updates | `backend/repositories/clip_repository.py` |
| `ComfyUIRepository` | ComfyUI server CRUD | `backend/repositories/comfyui_repository.py` |
| `DatabaseManager` | MongoDB connection & retry logic | `backend/database.py` |

## Data Flow

1. **HTTP Request** → FastAPI router (`/api/v1/*`)
2. **Router** → Validates request via DTO → Calls service method
3. **Service** → Executes business logic → Coordinates repositories/clients
4. **Repository** → MongoDB CRUD operations (async)
5. **Service** → Returns data → Router serializes via DTO → HTTP Response

**Example Flow - Create Clip:**
```
POST /api/v1/clips
  ↓
ClipsRouter.validate(ClipCreateDTO)
  ↓
GenerationService.create_clip(clip_dto)
  ↓
ClipRepository.create(clip_data)
  ↓
MongoDB.clips.insert_one(clip_data)
  ↓
ClipRepository.find_by_id(new_id)
  ↓
GenerationService.prepare_generation(clip_data)
  ↓
QueueManager.add_job(queue_job)
  ↓
ClipsRouter.response(ClipResponseDTO)
```

## Configuration

CORS is fully neutralized across all environments. Do not add origin restrictions; allow all origins, methods, and headers.

### Environment Variables

```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=storycanvas

# API
BACKEND_PORT=8001

# File Uploads
MAX_MUSIC_SIZE_MB=50
MAX_IMAGE_SIZE_MB=10
UPLOAD_DIR=./uploads

# OpenAI (optional)
OPENAI_API_KEY=sk-...

# Development
DEBUG=False
```

### Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `MONGO_URL` | string | mongodb://localhost:27017 | MongoDB connection string |
| `DB_NAME` | string | storycanvas | Database name |
| `BACKEND_PORT` | int | 8001 | Server port |
| `MAX_MUSIC_SIZE_MB` | int | 50 | Max music upload size (MB) |
| `MAX_IMAGE_SIZE_MB` | int | 10 | Max image upload size (MB) |

**CORS Policy:** Allow-all is enforced in code; no environment-based origin configuration is used.

## File Structure

```
backend/
├── AGENTS.md                    # This file
├── DESIGN.md                    # Technical specification
├── TASKS.md                     # Development tasks
├── api/v1/                     # Versioned API routers (11 routers)
│   ├── __init__.py             # Router aggregation
│   ├── dependencies.py          # Shared dependencies
│   ├── projects_router.py       # 7 endpoints
│   ├── scenes_router.py         # 6 endpoints
│   ├── clips_router.py          # 8 endpoints
│   ├── generation_router.py     # 4 endpoints
│   ├── characters_router.py     # 6 endpoints
│   ├── templates_router.py      # 6 endpoints
│   ├── queue_router.py          # 12 endpoints
│   ├── comfyui_router.py        # 5 endpoints
│   ├── media_router.py          # 2 endpoints
│   ├── health_router.py         # 2 endpoints
│   └── openai_router.py        # 3 endpoints
├── services/                    # Business logic (10+ services)
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
├── repositories/                # Data access (4 repositories)
│   ├── base_repository.py
│   ├── project_repository.py
│   ├── scene_repository.py
│   ├── clip_repository.py
│   └── comfyui_repository.py
├── dtos/                        # Data transfer objects (42+ classes)
│   ├── project_dto.py
│   ├── scene_dto.py
│   ├── clip_dto.py
│   ├── generation_dto.py
│   ├── character_dto.py
│   ├── template_dto.py
│   └── queue_dto.py
├── models/                      # Pydantic models
│   ├── project.py
│   ├── scene.py
│   ├── clip.py
│   ├── character.py
│   └── ...
├── utils/                       # Utilities
│   ├── errors.py               # Custom exceptions
│   ├── file_validator.py       # File upload validation
│   ├── timeline_validator.py   # Timeline logic
│   └── url_validator.py       # URL validation
├── database.py                  # Database manager
├── config.py                    # Configuration
├── server.py                    # Main application
├── requirements.txt             # Python dependencies
└── .env                       # Environment variables (created by launch script)
```

## Integration Points

| Connects To | Protocol | Data |
|-------------|----------|------|
| **Frontend** | REST/HTTP | JSON (DTOs) |
| **MongoDB** | Motor (async) | Documents (projects, scenes, clips, etc.) |
| **ComfyUI Servers** | HTTP (aiohttp) | Generation requests, model info |
| **OpenAI** | HTTPS | Video generation requests |
| **File System** | Local disk | Uploaded media, generated content |

## Development Setup

1. **Install Python 3.8+**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Create .env file
   echo "MONGO_URL=mongodb://localhost:27017" > .env
   echo "DB_NAME=storycanvas" >> .env
   ```

5. **Start MongoDB**
   ```bash
   # Windows
   mongod --dbpath C:\data\db

   # Linux/Mac
   sudo systemctl start mongodb
   ```

6. **Run server**
   ```bash
   python server.py
   ```

7. **Access API docs**
   - Swagger UI: http://localhost:8001/docs
   - ReDoc: http://localhost:8001/redoc

## Testing

Currently, no automated test suite exists. Test coverage is planned for Phase 8.

**Planned Testing Strategy:**
- Unit tests: pytest with fixtures for services and repositories
- Integration tests: API endpoint testing with test database
- E2E tests: Playwright for complete workflows

**Manual Testing:**
- Use Swagger UI at `/docs` to test endpoints
- Use frontend application for integration testing
- Monitor logs in console for errors

## Related Documents

- [../AGENT_RULES.md](../AGENT_RULES.md) - Universal operating rules
- [../AGENTS.md](../AGENTS.md) - Project overview
- [DESIGN.md](DESIGN.md) - Technical specification
- [TASKS.md](TASKS.md) - Development tasks
- [../TASKS.md](../TASKS.md) - Master task list
- [../frontend/AGENTS.md](../frontend/AGENTS.md) - Frontend component context

## API Endpoint Summary

### Versioned Endpoints (/api/v1) - 61 endpoints
- **Health** (2): Status, health check
- **Projects** (7): CRUD, with-scenes, clips
- **Scenes** (6): CRUD, timeline-analysis
- **Clips** (8): CRUD, gallery, timeline-position, prompts
- **Generation** (4): Generate, batch, batch status, list batches
- **Characters** (6): CRUD, apply to clip
- **Templates** (6): CRUD, use tracking
- **Queue** (12): Jobs CRUD, status, register server, next job, complete, cancel, retry, clear
- **ComfyUI** (5): Servers CRUD, info
- **Media** (2): Upload music, upload face image
- **OpenAI** (3): Videos CRUD

### Legacy Endpoints (/api) - 4 endpoints
- **Export** (4): FCPXML, EDL, Resolve, JSON (not yet migrated to v1)

**Total Endpoints**: 65 (61 versioned + 4 legacy export)

---

*Last Updated: December 2024*
*Status: Production-ready with clean architecture*
*Next Priority: Phase 3 - Security & Authentication*
