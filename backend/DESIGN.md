# Backend - Design Document

## 1. Overview

The backend provides a FastAPI-based REST API server for AI-powered storyboarding applications. It manages projects, scenes, clips, characters, templates, generation jobs, and ComfyUI server connections. The architecture follows clean separation of concerns with service layer abstraction, repository pattern for data access, comprehensive DTO validation, and versioned API endpoints for backward compatibility.

## 2. Design Principles

1. **Clean Architecture**: HTTP Layer → Service Layer → Repository Layer → Database
2. **API Versioning**: All new endpoints under `/api/v1`, legacy endpoints maintained
3. **Type Safety**: Comprehensive Pydantic models for request/response validation
4. **Async-First**: Async/await throughout for non-blocking operations
5. **Error Handling**: Standardized error responses with custom exception classes
6. **Dependency Injection**: Proper service management throughout backend

## 3. Architecture

### 3.1 Component Diagram

```
FastAPI Application
├── API Layer (api/v1/)
│   ├── Routers: projects, scenes, clips, generation, characters, templates, queue, comfyui, media, health, openai
│   ├── Dependencies: database, services
│   └── DTOs: Request/Response validation
├── Service Layer (services/)
│   ├── Business Logic: project_service, generation_service, comfyui_service, queue_manager, export_service
│   ├── Coordination: batch_generator, gallery_manager, media_service
│   └── Configuration: model_config, openai_video_service
├── Repository Layer (repositories/)
│   ├── Base Repository: Generic CRUD operations
│   └── Entity Repositories: project_repository, scene_repository, clip_repository, comfyui_repository
└── Data Layer
    ├── MongoDB (Motor): Async NoSQL database
    └── Collections: projects, scenes, clips, characters, templates, queue_jobs, comfyui_servers
```

### 3.2 Data Flow

```
HTTP Request
  ↓
Router (validation via DTO)
  ↓
Service (business logic)
  ↓
Repository (data access)
  ↓
MongoDB (async operation)
  ↓
Repository (result)
  ↓
Service (transform)
  ↓
Router (serialize via DTO)
  ↓
HTTP Response
```

## 4. Core Components

### 4.1 FastAPI Router Layer

**Purpose**: Handle HTTP concerns, map DTOs to service calls, marshal responses

**Responsibilities**:
- Route definition and HTTP method handling
- Request validation via Pydantic DTOs
- Dependency injection for services
- Response serialization via DTOs
- Error handling and HTTP status codes

**Key Routers**:
- `projects_router.py` - 7 endpoints
- `scenes_router.py` - 6 endpoints
- `clips_router.py` - 8 endpoints
- `generation_router.py` - 4 endpoints
- `characters_router.py` - 6 endpoints
- `templates_router.py` - 6 endpoints
- `queue_router.py` - 12 endpoints
- `comfyui_router.py` - 5 endpoints
- `media_router.py` - 2 endpoints
- `health_router.py` - 2 endpoints
- `openai_router.py` - 3 endpoints

**Interface Definition**:
```python
from fastapi import APIRouter, Depends
from .dependencies import get_database, get_service

router = APIRouter(prefix="/projects")

@router.post("/", response_model=ProjectResponseDTO)
async def create_project(
    project: ProjectCreateDTO,
    db = Depends(get_database),
    service = Depends(get_project_service)
):
    result = await service.create_project(project)
    return result
```

### 4.2 Service Layer

**Purpose**: Encapsulate business workflows, coordinate repositories and third-party clients

**Key Services**:

1. **ProjectService**
   - Manage projects and scene hierarchy
   - File: `backend/services/project_service.py`

2. **GenerationService**
   - Coordinate generation workflows
   - Integrate with queue_manager, batch_generator, gallery_manager
   - File: `backend/services/generation_service.py`

3. **ComfyUIService**
   - ComfyUI client, server management, model catalog
   - File: `backend/services/comfyui_service.py`

4. **QueueManager**
   - Intelligent queue management with load balancing
   - Track job lifecycles, server assignment, retries
   - File: `backend/services/queue_manager.py`

5. **ExportService**
   - Export formats (FCPXML, EDL, DaVinci Resolve, JSON)
   - File: `backend/services/export_service.py`

6. **BatchGenerator**
   - Concurrent batch generation
   - File: `backend/services/batch_generator.py`

7. **GalleryManager**
   - Generated content gallery updates
   - File: `backend/services/gallery_manager.py`

8. **MediaService**
   - File upload validation and storage
   - File: `backend/services/media_service.py`

9. **ModelConfig**
   - Model presets (13+ AI models)
   - File: `backend/services/model_config.py`

10. **OpenAIVideoService**
    - OpenAI video integration
    - File: `backend/services/openai_video_service.py`

### 4.3 Repository Layer

**Purpose**: Provide CRUD abstraction over Motor collections with reusable helpers

**Base Repository**:
```python
class BaseRepository:
    """Generic async CRUD operations"""
    
    async def create(self, data: dict) -> str:
        """Create document, return ObjectId as string"""
        pass
    
    async def find_by_id(self, id: str) -> Optional[dict]:
        """Find document by ObjectId"""
        pass
    
    async def update(self, id: str, data: dict) -> bool:
        """Update document by ObjectId"""
        pass
    
    async def delete(self, id: str) -> bool:
        """Delete document by ObjectId"""
        pass
    
    async def list(self, filter: dict = None, skip: int = 0, limit: int = 100) -> List[dict]:
        """List documents with pagination"""
        pass
```

**Entity Repositories**:
1. `ProjectRepository` - Project-specific queries
2. `SceneRepository` - Scene retrieval with ordering
3. `ClipRepository` - Clip operations, gallery updates
4. `ComfyUIRepository` - ComfyUI server CRUD

## 5. Data Models

### 5.1 Project Model

```python
@dataclass
class Project:
    id: str
    name: str
    description: Optional[str]
    music_file: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### 5.2 Scene Model

```python
@dataclass
class Scene:
    id: str
    project_id: str
    name: str
    description: Optional[str]
    order: int
    parent_scene_id: Optional[str]
    alternate_number: int
    is_alternate: bool
    created_at: datetime
    updated_at: datetime
```

### 5.3 Clip Model

```python
@dataclass
class Clip:
    id: str
    scene_id: str
    name: str
    lyrics: Optional[str]
    image_prompt: str
    video_prompt: str
    timeline_position: float
    length: float
    character_id: Optional[str]
    parent_clip_id: Optional[str]
    alternate_number: int
    is_alternate: bool
    generated_images: List[GeneratedContent]
    generated_videos: List[GeneratedContent]
    created_at: datetime
    updated_at: datetime
```

### 5.4 Character Model

```python
@dataclass
class Character:
    id: str
    name: str
    description: str
    reference_images: List[str]
    lora: Optional[str]
    trigger_words: List[str]
    style_notes: str
    project_id: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### 5.5 QueueJob Model

```python
@dataclass
class QueueJob:
    id: str
    project_id: str
    clip_id: str
    job_type: str  # "image" or "video"
    status: str  # "pending", "processing", "completed", "failed", "cancelled"
    priority: int
    server_id: Optional[str]
    generation_params: dict
    result_url: Optional[str]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

## 6. API / Interfaces

### 6.1 REST Endpoints

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| GET | /api/v1/health | - | HealthStatus |
| GET | /api/v1/projects | - | ProjectListResponse |
| POST | /api/v1/projects | ProjectCreateDTO | ProjectResponse |
| GET | /api/v1/projects/{id} | - | ProjectResponse |
| GET | /api/v1/projects/{id}/with-scenes | - | ProjectWithScenesResponse |
| PUT | /api/v1/projects/{id} | ProjectUpdateDTO | ProjectResponse |
| DELETE | /api/v1/projects/{id} | - | SuccessResponse |
| POST | /api/v1/scenes | SceneCreateDTO | SceneResponse |
| GET | /api/v1/scenes/project/{project_id} | - | SceneListResponse |
| POST | /api/v1/clips | ClipCreateDTO | ClipResponse |
| GET | /api/v1/clips/scene/{scene_id} | - | ClipListResponse |
| POST | /api/v1/generation | GenerationRequestDTO | GenerationResponse |
| POST | /api/v1/generation/batch | BatchGenerationRequestDTO | BatchResponse |
| POST | /api/v1/queue/jobs | QueueJobRequestDTO | QueueJobResponse |
| GET | /api/v1/queue/status | - | QueueStatusResponse |
| POST | /api/v1/characters | CharacterCreateDTO | CharacterResponse |
| POST | /api/v1/templates | TemplateCreateDTO | TemplateResponse |
| POST | /api/v1/comfyui/servers | ComfyUIServerCreateDTO | ComfyUIServerResponse |
| POST | /api/v1/media/projects/{id}/upload-music | UploadFile | UploadMusicResponse |

**Total Endpoints**: 61 versioned + 4 legacy export = 65 total

### 6.2 WebSocket Messages (Planned)

**Client → Server:**
```json
{
  "type": "subscribe_queue",
  "data": {"project_id": "string"}
}
```

**Server → Client:**
```json
{
  "type": "queue_update",
  "data": {
    "job_id": "string",
    "status": "processing",
    "progress": 50
  }
}
```

## 7. Configuration

### 7.1 Environment Variables

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

### 7.2 Configuration Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `MONGO_URL` | string | mongodb://localhost:27017 | MongoDB connection string |
| `DB_NAME` | string | storycanvas | Database name |
| `BACKEND_PORT` | int | 8001 | Server port |
| `MAX_MUSIC_SIZE_MB` | int | 50 | Max music upload size (MB) |
| `MAX_IMAGE_SIZE_MB` | int | 10 | Max image upload size (MB) |

**CORS Policy:** Allow-all is enforced in code; no origin restrictions or environment overrides.

## 8. Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| `ResourceNotFoundError` | Entity not found by ID | 404 with error message |
| `ValidationError` | Invalid request data | 400 with validation details |
| `ConflictError` | Duplicate or conflicting data | 409 with conflict details |
| `AuthenticationError` | Invalid or missing credentials | 401 with error message |
| `RateLimitError` | Too many requests | 429 with retry-after header |

**Standard Error Response:**
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Project with id 'abc123' not found",
    "details": {}
  }
}
```

## 9. Performance Considerations

- **Async Operations**: All database and HTTP operations are async for non-blocking I/O
- **Database Indexing**: Add indexes on frequently queried fields (id, project_id, scene_id)
- **Queue Optimization**: Intelligent server selection to minimize job wait times
- **File Upload Limits**: Enforce size limits to prevent disk exhaustion
- **Response Caching**: Planned Redis cache for frequent queries (Phase 6)
- **Connection Pooling**: Motor manages connection pool automatically

## 10. Security Considerations

- **CORS Configuration**: Fully neutralized (allow-all) with no origin restrictions
- **File Upload Validation**: Type validation, size limits, path traversal prevention
- **Input Validation**: Pydantic DTOs validate all request data
- **Error Messages**: Don't expose sensitive information in error responses
- **Planned**: JWT authentication (Phase 3), API key encryption (Phase 3), rate limiting (Phase 3)

## 11. Testing Strategy

### Unit Tests (Planned - Phase 8)
- Service layer business logic
- Repository CRUD operations
- DTO validation
- Utility functions

### Integration Tests (Planned - Phase 8)
- API endpoint testing
- Database operations
- External service mocking

### E2E Tests (Planned - Phase 8)
- Complete workflows via Playwright

## 12. Future Considerations

- **Authentication**: JWT-based user authentication with role-based access control
- **Rate Limiting**: SlowAPI integration for API abuse prevention
- **WebSockets**: Real-time updates for queue status, generation progress
- **Caching**: Redis caching layer for frequent queries
- **Monitoring**: Structured logging, Prometheus metrics, Sentry error tracking
- **Testing**: Comprehensive test suite with >80% coverage

---

*Last Updated: December 2024*
*Status: Production-ready with clean architecture*
