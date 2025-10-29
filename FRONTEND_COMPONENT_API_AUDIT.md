# Frontend Component API Coverage Audit

**Generated:** 2024
**Total Components Analyzed:** 30 main components + 45 Shadcn UI components

---

## Executive Summary

### Key Findings

1. **API Abstraction Layer:** ❌ **DOES NOT EXIST**
   - All 30 main components use direct `axios` calls
   - No centralized service layer in `frontend/src/services/`
   - API calls scattered across component files

2. **API Base URL Configuration:** ✅ Centralized via `@/config`
   - Config: `frontend/src/config.js` exports `API` constant
   - Pattern: `${API}/endpoint`

3. **API Versions:**
   - `/api` - Main backend endpoints (via `api_router` in `server.py`)
   - `/api/v1` - V1 endpoints (via `api_v1_router` in `backend/api/v1/`)

4. **Coverage Gaps:**
   - Missing error handling abstraction
   - No request/response interceptors
   - Duplicated endpoint strings across components
   - No centralized retry logic

---

## Component-to-Endpoint Mapping Matrix

### 1. CharacterManager.jsx
**Purpose:** Character management with reference images, LoRAs, generation methods

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/comfyui/servers` | Fetch available ComfyUI servers |
| GET | `/api/characters?project_id={id}` | Fetch project characters |
| POST | `/api/characters` | Create new character |
| PUT | `/api/characters/{id}` | Update existing character |
| DELETE | `/api/characters/{id}` | Delete character |
| POST | `/api/characters/{id}/generate` | Generate character samples |
| POST | `/api/upload-face-image` | Upload face image for character |

**Backend Endpoints:**
- ✅ `/api/characters` (POST, GET) - Lines 4303, 4311 in server.py
- ✅ `/api/characters/{id}` (GET, PUT, DELETE) - Lines 4318, 4326, 4343 in server.py
- ✅ `/api/characters/{id}/generate` (POST) - Line 4397 in server.py
- ✅ `/api/comfyui/servers` (GET) - Line 2243 in server.py
- ✅ `/api/upload-face-image` (POST) - Line 3062 in server.py

**Abstraction:** ❌ Direct axios calls

---

### 2. StyleTemplateLibrary.jsx
**Purpose:** Style template management (presets for generation parameters)

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/style-templates` | Fetch all templates |
| POST | `/api/style-templates` | Create new template |
| PUT | `/api/style-templates/{id}` | Update template |
| DELETE | `/api/style-templates/{id}` | Delete template |
| POST | `/api/style-templates/{id}/use` | Record template usage |

**Backend Endpoints:**
- ✅ `/api/style-templates` (POST, GET) - Lines 4173, 4182 in server.py
- ✅ `/api/style-templates/{id}` (GET, PUT, DELETE) - Lines 4194, 4202, 4219 in server.py
- ✅ `/api/style-templates/{id}/use` (POST) - Line 4227 in server.py
- ✅ `/api/v1/style-templates` - templates_router.py (alternative v1 endpoints)

**Abstraction:** ❌ Direct axios calls

---

### 3. QueueDashboard.jsx
**Purpose:** Job queue monitoring and management

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/queue/jobs?status={status}` | Fetch queue jobs |
| POST | `/api/queue/jobs/{id}/retry` | Retry failed job |
| POST | `/api/queue/jobs/{id}/cancel` | Cancel pending/processing job |
| DELETE | `/api/queue/jobs/{id}` | Delete job |
| DELETE | `/api/queue/clear?status={status}` | Clear completed/failed jobs |

**Backend Endpoints:**
- ✅ `/api/queue/jobs` (POST, GET) - Lines 4804, 4848 in server.py
- ❌ `/api/queue/jobs/{id}/retry` - **NOT IMPLEMENTED**
- ❌ `/api/queue/jobs/{id}/cancel` - **NOT IMPLEMENTED**
- ❌ `/api/queue/clear` - **NOT IMPLEMENTED**
- ✅ `/api/queue/jobs/{id}/complete` (POST) - Line 4910 in server.py

**Coverage Gaps:**
- ❌ Missing retry endpoint
- ❌ Missing cancel endpoint
- ❌ Missing clear endpoint

**Abstraction:** ❌ Direct axios calls

---

### 4. ProjectDashboard.jsx
**Purpose:** Project overview with stats, music player, scenes list

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/projects/{id}` | Fetch project details |
| GET | `/api/projects/{id}/scenes` | Fetch project scenes |
| PUT | `/api/projects/{id}` | Update project settings |
| DELETE | `/api/projects/{id}` | Delete project |

**Backend Endpoints:**
- ✅ `/api/projects` (POST, GET) - Lines 3006, 3013 in server.py
- ✅ `/api/projects/{id}` (GET) - Line 3018 in server.py
- ⚠️ `/api/projects/{id}` (PUT, DELETE) - Not in /api, exists in /api/v1
- ✅ `/api/projects/{id}/scenes` (GET) - Line 3373 in server.py
- ✅ `/api/v1/projects/{id}` (PUT, DELETE) - projects_router.py lines 51, 70

**Coverage Gaps:**
- ⚠️ PUT/DELETE missing in /api but exist in /api/v1

**Abstraction:** ❌ Direct axios calls

---

### 5. GenerationPool.jsx
**Purpose:** Generated content pool management

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/pool/{project_id}` | Fetch pool items for project |
| DELETE | `/api/pool/item/{item_id}` | Delete pool item |

**Backend Endpoints:**
- ✅ `/api/pool` (POST) - Line 3759 in server.py
- ✅ `/api/pool/{project_id}` (GET) - Line 3767 in server.py
- ✅ `/api/pool/item/{id}` (GET, PUT, DELETE) - Lines 3782, 3790, 3814 in server.py

**Abstraction:** ❌ Direct axios calls

---

### 6. Timeline.jsx
**Purpose:** Main timeline editor with clips and scenes

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/projects/{id}/scenes` | Fetch scenes |
| GET | `/api/scenes/{id}/clips` | Fetch clips for scene |
| GET | `/api/scenes/{id}/timeline-analysis` | Get timeline analysis |
| PUT | `/api/clips/{id}/timeline-position` | Update clip position |
| PUT | `/api/scenes/{id}` | Update scene |
| POST | `/api/projects/{id}/upload-music` | Upload music file |

**Backend Endpoints:**
- ✅ `/api/projects/{id}/scenes` (GET) - Line 3373 in server.py
- ✅ `/api/scenes/{id}/clips` (GET) - Line 3462 in server.py
- ✅ `/api/scenes/{id}/timeline-analysis` (GET) - Line 3630 in server.py
- ✅ `/api/clips/{id}/timeline-position` (PUT) - Line 3504 in server.py
- ✅ `/api/scenes/{id}` (GET, PUT) - Lines 3383, 3390 in server.py
- ✅ `/api/projects/{id}/upload-music` (POST) - Line 3027 in server.py

**Abstraction:** ❌ Direct axios calls

---

### 7. ProjectTimeline.jsx
**Purpose:** Timeline view with scene creation

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/projects/{id}/timeline` | Fetch timeline data |
| POST | `/api/scenes/{id}/create-alternate` | Create scene alternate |
| POST | `/api/scenes` | Create new scene |
| POST | `/api/clips` | Create new clip |

**Backend Endpoints:**
- ✅ `/api/projects/{id}/timeline` (GET) - Line 3330 in server.py
- ✅ `/api/scenes/{id}/create-alternate` (POST) - Line 3405 in server.py
- ✅ `/api/scenes` (POST) - Line 3323 in server.py
- ✅ `/api/clips` (POST) - Line 3455 in server.py

**Abstraction:** ❌ Direct axios calls

---

### 8. GenerationStudio.jsx
**Purpose:** AI generation studio for clips

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/projects/{id}/scenes` | Fetch scenes |
| GET | `/api/projects/{id}/clips` | Fetch clips |

**Backend Endpoints:**
- ✅ `/api/projects/{id}/scenes` (GET) - Line 3373 in server.py
- ✅ `/api/projects/{id}/clips` (GET) - Line 3378 in server.py

**Abstraction:** ❌ Direct axios calls

---

### 9. ExportDialog.jsx
**Purpose:** Export project to various formats (FCPXML, EDL, Resolve, JSON)

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/projects/{id}/export/fcpxml` | Export Final Cut Pro XML |
| GET | `/api/projects/{id}/export/edl` | Export Premiere Pro EDL |
| GET | `/api/projects/{id}/export/resolve` | Export DaVinci Resolve XML |
| GET | `/api/projects/{id}/export/json` | Export JSON format |

**Backend Endpoints:**
- ✅ `/api/projects/{id}/export/fcpxml` (GET) - Line 4239 in server.py
- ✅ `/api/projects/{id}/export/edl` (GET) - Line 4256 in server.py
- ✅ `/api/projects/{id}/export/resolve` (GET) - Line 4273 in server.py
- ✅ `/api/projects/{id}/export/json` (GET) - Line 4290 in server.py

**Abstraction:** ❌ Direct axios calls

---

### 10. EnhancedGenerationDialog.jsx
**Purpose:** Advanced generation interface with workflow selection

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/comfyui/servers/{id}/info` | Get server info |
| GET | `/api/comfyui/servers/{id}/workflows` | Get available workflows |
| GET | `/api/models/presets/{modelName}` | Get model presets |
| GET | `/api/models/parameters/{modelName}` | Get model parameters |
| GET | `/api/clips/{id}/gallery` | Get clip gallery |
| POST | `/api/generate` or `/api/v1/generate` | Generate content |
| PUT | `/api/clips/{id}/prompts` | Update clip prompts |
| PUT | `/api/clips/{id}/select-content` | Select content version |
| POST | `/api/upload-face-image` | Upload face image |
| GET | `/api/clips/{id}` | Get clip data |
| GET | `/api/scenes/{id}` | Get scene data |
| POST | `/api/pool` | Add to generation pool |

**Backend Endpoints:**
- ✅ All endpoints implemented and matched

**Abstraction:** ❌ Direct axios calls

---

### 11. GenerationDialog.jsx
**Purpose:** Basic generation dialog

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/comfyui/servers/{id}/info` | Get server info |
| POST | `/api/v1/generate` | Generate with OpenAI Sora |
| POST | `/api/generate` | Generate with ComfyUI |

**Backend Endpoints:**
- ✅ All endpoints implemented

**Abstraction:** ❌ Direct axios calls

---

### 12. FaceFusionProcessor.jsx
**Purpose:** Face enhancement, age adjustment, face swapping

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/facefusion/status` | Check FaceFusion status |
| POST | `/api/facefusion/enhance-face` | Enhance face quality |
| POST | `/api/facefusion/adjust-face-age` | Adjust face age |
| POST | `/api/facefusion/swap-face` | Swap faces |
| POST | `/api/facefusion/batch-process` | Batch process faces |

**Backend Endpoints:**
- ✅ All endpoints implemented (Lines 4518-4691 in server.py)

**Abstraction:** ❌ Direct axios calls

---

### 13. ComfyUIManager.jsx
**Purpose:** ComfyUI server management

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| POST | `/api/comfyui/servers` | Register new server |
| GET | `/api/comfyui/servers/{id}/info` | Get server info |
| DELETE | `/api/comfyui/servers/{id}` | Delete server |

**Backend Endpoints:**
- ✅ All endpoints implemented

**Abstraction:** ❌ Direct axios calls

---

### 14. BatchGenerationDialog.jsx
**Purpose:** Batch generation for multiple clips

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/comfyui/servers/{id}` | Get server details |
| POST | `/api/generate/batch` | Create batch generation |

**Backend Endpoints:**
- ⚠️ `/api/comfyui/servers/{id}` (GET) - Should use `/info` endpoint
- ✅ `/api/generate/batch` (POST) - Line 4115 in server.py

**Coverage Gaps:**
- ⚠️ Component calls GET on `/api/comfyui/servers/{id}` but backend only has `/api/comfyui/servers/{id}/info`

**Abstraction:** ❌ Direct axios calls

---

### 15. AdvancedCharacterCreator.jsx
**Purpose:** Advanced character creation with multiple images

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| POST | `/api/upload-character-images` | Upload multiple character images |
| POST | `/api/characters` | Create character |
| POST | `/api/generate-character-profiles` | Generate character profiles |

**Backend Endpoints:**
- ✅ All endpoints implemented (Lines 3099, 3152, 4303 in server.py)

**Abstraction:** ❌ Direct axios calls

---

### 16. ModelBrowser.jsx
**Purpose:** Browse and manage AI models

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/models` | Fetch models with filters |
| POST | `/api/servers/{id}/sync-models` | Sync models from server |

**Backend Endpoints:**
- ✅ All endpoints implemented

**Abstraction:** ❌ Direct axios calls

---

### 17. ModelCard.jsx
**Purpose:** Individual model card with Civitai integration

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| POST | `/api/models/{id}/sync-civitai` | Sync with Civitai |
| POST | `/api/models/{id}/search-civitai` | Search Civitai |
| POST | `/api/models/{id}/link-civitai` | Link to Civitai model |

**Backend Endpoints:**
- ✅ All endpoints implemented

**Abstraction:** ❌ Direct axios calls

---

### 18. SceneManager.jsx
**Purpose:** Scene and clip creation

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| POST | `/api/scenes` | Create new scene |
| POST | `/api/clips` | Create new clip |

**Backend Endpoints:**
- ✅ All endpoints implemented

**Abstraction:** ❌ Direct axios calls

---

### 19. UnifiedTimeline.jsx
**Purpose:** Unified timeline view

**API Calls:**
| Method | Endpoint | Purpose |
|--------|----------|----------|
| GET | `/api/projects/{id}/scenes` | Fetch scenes |
| GET | `/api/scenes/{id}/clips` | Fetch clips |
| POST | `/api/scenes/{id}/create-alternate` | Create scene alternate |
| POST | `/api/clips/{id}/create-alternate` | Create clip alternate |
| POST | `/api/clips` | Create clip |

**Backend Endpoints:**
- ✅ All endpoints implemented

**Abstraction:** ❌ Direct axios calls

---

### 20-30. Supporting Components

**QueueJobCard.jsx, TimelineClipCard.jsx, TimelineClipSimple.jsx, SceneActionButtons.jsx, MetadataItem.jsx, MediaViewerDialog.jsx, HotkeyHelpDialog.jsx, PresentationMode.jsx, ProjectView.jsx, ModelCardComponents.jsx, Sidebar.jsx**

- These components primarily render UI and receive data via props
- No direct API calls identified
- Rely on parent components for data

---

## Complete Backend API Endpoint Reference

### `/api` Endpoints (server.py - api_router)

#### Health & Info
- `GET /api/` - API root status
- `GET /api/health` - Health check

#### ComfyUI Servers
- `POST /api/comfyui/servers` - Register server
- `GET /api/comfyui/servers` - List servers
- `DELETE /api/comfyui/servers/{id}` - Delete server
- `GET /api/comfyui/servers/{id}/info` - Get server info
- `GET /api/comfyui/servers/{id}/workflows` - Get workflows

#### Models
- `GET /api/models` - List models with filters
- `PUT /api/models/{id}` - Update model
- `DELETE /api/models/{id}` - Delete model
- `POST /api/models/{id}/sync-civitai` - Sync with Civitai
- `POST /api/models/{id}/search-civitai` - Search Civitai
- `POST /api/models/{id}/link-civitai` - Link to Civitai
- `POST /api/models/{id}/presets` - Create preset
- `GET /api/models/presets/{name}` - Get presets
- `PUT /api/models/{id}/presets/{preset_id}` - Update preset
- `DELETE /api/models/{id}/presets/{preset_id}` - Delete preset
- `GET /api/models/defaults/{name}` - Get defaults
- `GET /api/models/parameters/{name}` - Get parameters
- `GET /api/models/types` - List model types
- `GET /api/active-models` - Get active models
- `GET /api/backends` - Get backends
- `GET /api/backends/{id}/models` - Get backend models
- `POST /api/servers/{id}/sync-models` - Sync server models

#### Projects
- `POST /api/projects` - Create project
- `GET /api/projects` - List projects
- `GET /api/projects/{id}` - Get project
- `GET /api/projects/{id}/timeline` - Get timeline
- `GET /api/projects/{id}/scenes` - Get scenes
- `GET /api/projects/{id}/clips` - Get clips
- `POST /api/projects/{id}/upload-music` - Upload music
- `GET /api/projects/{id}/export/fcpxml` - Export FCPXML
- `GET /api/projects/{id}/export/edl` - Export EDL
- `GET /api/projects/{id}/export/resolve` - Export Resolve XML
- `GET /api/projects/{id}/export/json` - Export JSON

#### Scenes
- `POST /api/scenes` - Create scene
- `GET /api/scenes/{id}` - Get scene
- `PUT /api/scenes/{id}` - Update scene
- `POST /api/scenes/{id}/create-alternate` - Create alternate
- `GET /api/scenes/{id}/clips` - Get scene clips
- `GET /api/scenes/{id}/timeline-analysis` - Timeline analysis

#### Clips
- `POST /api/clips` - Create clip
- `GET /api/clips/{id}` - Get clip
- `PUT /api/clips/{id}` - Update clip
- `PUT /api/clips/{id}/timeline-position` - Update position
- `POST /api/clips/{id}/create-alternate` - Create alternate
- `PUT /api/clips/{id}/prompts` - Update prompts
- `GET /api/clips/{id}/gallery` - Get gallery
- `PUT /api/clips/{id}/select-content` - Select content

#### Generation Pool
- `POST /api/pool` - Add to pool
- `GET /api/pool/{project_id}` - Get pool items
- `GET /api/pool/item/{id}` - Get pool item
- `PUT /api/pool/item/{id}` - Update pool item
- `DELETE /api/pool/item/{id}` - Delete pool item
- `POST /api/pool/item/{id}/apply-to-clip/{clip_id}` - Apply to clip

#### Generation
- `POST /api/generate` - Generate content
- `POST /api/generate/batch` - Batch generate
- `GET /api/generate/batch/{id}` - Get batch status
- `GET /api/generate/batches` - List batches

#### Style Templates
- `POST /api/style-templates` - Create template
- `GET /api/style-templates` - List templates
- `GET /api/style-templates/{id}` - Get template
- `PUT /api/style-templates/{id}` - Update template
- `DELETE /api/style-templates/{id}` - Delete template
- `POST /api/style-templates/{id}/use` - Record template usage

#### Characters
- `POST /api/characters` - Create character
- `GET /api/characters` - List characters
- `GET /api/characters/{id}` - Get character
- `PUT /api/characters/{id}` - Update character
- `DELETE /api/characters/{id}` - Delete character
- `POST /api/characters/{id}/apply/{clip_id}` - Apply to clip
- `POST /api/characters/{id}/generate` - Generate samples
- `POST /api/characters/train-lora` - Train LoRA

#### Media Upload
- `POST /api/upload-face-image` - Upload face image
- `POST /api/upload-character-images` - Upload character images
- `POST /api/generate-character-profiles` - Generate profiles

#### FaceFusion
- `GET /api/facefusion/status` - Check status
- `POST /api/facefusion/enhance-face` - Enhance face
- `POST /api/facefusion/adjust-face-age` - Adjust age
- `POST /api/facefusion/swap-face` - Swap faces
- `POST /api/facefusion/batch-process` - Batch process

#### Queue
- `POST /api/queue/jobs` - Create job
- `GET /api/queue/jobs` - List jobs
- `GET /api/queue/status` - Queue status
- `GET /api/queue/jobs/{id}` - Get job
- `GET /api/queue/projects/{project_id}/jobs` - Project jobs
- `POST /api/queue/servers/{server_id}/register` - Register worker
- `GET /api/queue/servers/{server_id}/next` - Get next job
- `POST /api/queue/jobs/{id}/complete` - Complete job

### `/api/v1` Endpoints (backend/api/v1/)

#### Health
- `GET /api/v1/` - API root
- `GET /api/v1/health` - Health check

#### Characters (characters_router.py)
- `POST /api/v1/characters` - Create
- `GET /api/v1/characters` - List
- `GET /api/v1/characters/{id}` - Get
- `PUT /api/v1/characters/{id}` - Update
- `DELETE /api/v1/characters/{id}` - Delete
- `POST /api/v1/characters/{id}/apply/{clip_id}` - Apply

#### Clips (clips_router.py)
- `POST /api/v1/clips` - Create
- `GET /api/v1/clips/scene/{scene_id}` - List by scene
- `GET /api/v1/clips/{id}` - Get
- `GET /api/v1/clips/{id}/gallery` - Gallery
- `PUT /api/v1/clips/{id}` - Update
- `PUT /api/v1/clips/{id}/timeline-position` - Update position
- `PUT /api/v1/clips/{id}/prompts` - Update prompts
- `DELETE /api/v1/clips/{id}` - Delete

#### ComfyUI (comfyui_router.py)
- `POST /api/v1/comfyui/servers` - Create
- `GET /api/v1/comfyui/servers` - List
- `GET /api/v1/comfyui/servers/{id}/info` - Info
- `PUT /api/v1/comfyui/servers/{id}` - Update
- `DELETE /api/v1/comfyui/servers/{id}` - Delete

#### Generation (generation_router.py)
- `POST /api/v1/generate` - Generate (OpenAI Sora)
- `POST /api/v1/generate/batch` - Batch generate
- `GET /api/v1/generate/batch/{id}` - Batch status
- `GET /api/v1/generate/batches` - List batches

#### Projects (projects_router.py)
- `POST /api/v1/projects` - Create
- `GET /api/v1/projects` - List
- `GET /api/v1/projects/{id}` - Get
- `GET /api/v1/projects/{id}/with-scenes` - Get with scenes
- `PUT /api/v1/projects/{id}` - Update
- `GET /api/v1/projects/{id}/clips` - List clips
- `DELETE /api/v1/projects/{id}` - Delete

#### Scenes (scenes_router.py)
- `POST /api/v1/scenes` - Create
- `GET /api/v1/scenes/project/{project_id}` - List by project
- `GET /api/v1/scenes/{id}` - Get
- `PUT /api/v1/scenes/{id}` - Update
- `DELETE /api/v1/scenes/{id}` - Delete
- `GET /api/v1/scenes/{id}/timeline-analysis` - Analysis

#### Templates (templates_router.py)
- `POST /api/v1/style-templates` - Create
- `GET /api/v1/style-templates` - List
- `GET /api/v1/style-templates/{id}` - Get
- `PUT /api/v1/style-templates/{id}` - Update
- `DELETE /api/v1/style-templates/{id}` - Delete
- `POST /api/v1/style-templates/{id}/use` - Use

#### Queue (queue_router.py)
- `POST /api/v1/queue/jobs` - Create job
- `GET /api/v1/queue/jobs` - List jobs
- `GET /api/v1/queue/status` - Status
- `GET /api/v1/queue/jobs/{id}` - Get job
- `GET /api/v1/queue/projects/{project_id}/jobs` - Project jobs
- `POST /api/v1/queue/servers/{server_id}/register` - Register worker
- `GET /api/v1/queue/servers/{server_id}/next` - Get next job
- `POST /api/v1/queue/jobs/{id}/complete` - Complete job

#### Media (media_router.py)
- `POST /api/v1/projects/{project_id}/upload-music` - Upload music
- `POST /api/v1/upload-face-image` - Upload face image

#### OpenAI (openai_router.py)
- `GET /api/v1/videos/{video_id}` - Get video
- `GET /api/v1/videos` - List videos
- `DELETE /api/v1/videos/{video_id}` - Delete video

---

## Summary of Coverage Gaps

### Missing Backend Endpoints (Frontend calls but backend doesn't implement)

1. **QueueDashboard.jsx**
   - ❌ `POST /api/queue/jobs/{id}/retry`
   - ❌ `POST /api/queue/jobs/{id}/cancel`
   - ❌ `DELETE /api/queue/clear?status={status}`

2. **ProjectDashboard.jsx**
   - ⚠️ `PUT /api/projects/{id}` - Exists in /api/v1 but not /api
   - ⚠️ `DELETE /api/projects/{id}` - Exists in /api/v1 but not /api

3. **BatchGenerationDialog.jsx**
   - ⚠️ `GET /api/comfyui/servers/{id}` - Should use `/info` endpoint instead

### Recommendations

1. **Create Service Abstraction Layer**
   - Create `frontend/src/services/` directory
   - Implement service modules: `projectsService.js`, `scenesService.js`, `clipsService.js`, etc.
   - Centralize all axios calls
   - Add error handling and retry logic

2. **Fix Missing Endpoints**
   - Implement queue retry/cancel/clear endpoints in backend
   - Add PUT/DELETE for projects in /api or update frontend to use /api/v1

3. **Standardize API Version Usage**
   - Decide on /api vs /api/v1 strategy
   - Update all components to use consistent version
   - Document version differences

4. **Add Request/Response Interceptors**
   - Implement axios interceptors for authentication
   - Add global error handling
   - Implement request/response logging

5. **Type Safety**
   - Consider adding TypeScript
   - Define API response types
   - Add validation for API responses
