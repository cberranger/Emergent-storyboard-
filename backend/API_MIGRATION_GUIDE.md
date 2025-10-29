# API Migration Guide: /api to /api/v1

## Overview
Legacy `/api` endpoints are being deprecated in favor of versioned `/api/v1` endpoints. All new development should use the v1 API.

**Sunset Date: June 1, 2025**

After this date, legacy `/api` endpoints will be removed completely.

## Migration Path

### Base URL Change
- **Old**: `http://localhost:8001/api/{endpoint}`
- **New**: `http://localhost:8001/api/v1/{endpoint}`

### Quick Migration
Simply add `/v1` after `/api` in all your API calls:
```javascript
// Old
const response = await axios.get(`${API}/projects`);

// New
const response = await axios.get(`${API}/v1/projects`);
```

## Endpoint Mapping

All legacy endpoints are 1:1 mapped to v1 equivalents:

### Projects
- `POST /api/projects` → `POST /api/v1/projects`
- `GET /api/projects` → `GET /api/v1/projects`
- `GET /api/projects/{id}` → `GET /api/v1/projects/{id}`
- `PUT /api/projects/{id}` → `PUT /api/v1/projects/{id}`
- `DELETE /api/projects/{id}` → `DELETE /api/v1/projects/{id}`
- `POST /api/projects/{id}/upload-music` → `POST /api/v1/media/upload-music/{project_id}`

### Scenes
- `POST /api/scenes` → `POST /api/v1/scenes`
- `GET /api/projects/{id}/scenes` → `GET /api/v1/projects/{id}/scenes`
- `GET /api/scenes/{id}` → `GET /api/v1/scenes/{id}`
- `PUT /api/scenes/{id}` → `PUT /api/v1/scenes/{id}`
- `DELETE /api/scenes/{id}` → `DELETE /api/v1/scenes/{id}`
- `POST /api/scenes/{id}/create-alternate` → `POST /api/v1/scenes/{id}/create-alternate`
- `GET /api/scenes/{id}/timeline-analysis` → `GET /api/v1/scenes/{id}/timeline-analysis`

### Clips
- `POST /api/clips` → `POST /api/v1/clips`
- `GET /api/scenes/{id}/clips` → `GET /api/v1/scenes/{id}/clips`
- `GET /api/clips/{id}` → `GET /api/v1/clips/{id}`
- `PUT /api/clips/{id}` → `PUT /api/v1/clips/{id}`
- `DELETE /api/clips/{id}` → `DELETE /api/v1/clips/{id}`
- `POST /api/clips/{id}/create-alternate` → `POST /api/v1/clips/{id}/create-alternate`
- `PUT /api/clips/{id}/timeline-position` → `PUT /api/v1/clips/{id}/timeline-position`
- `PUT /api/clips/{id}/prompts` → `PUT /api/v1/clips/{id}/prompts`
- `GET /api/clips/{id}/gallery` → `GET /api/v1/clips/{id}/gallery`
- `PUT /api/clips/{id}/select-content` → `PUT /api/v1/clips/{id}/select-content`

### Generation
- `POST /api/generate` → `POST /api/v1/generate`
- `POST /api/generate/batch` → `POST /api/v1/generate/batch`
- `GET /api/generate/batch/{id}` → `GET /api/v1/generate/batch/{id}`
- `GET /api/generate/batches` → `GET /api/v1/generate/batches`

### ComfyUI Servers
- `POST /api/comfyui/servers` → `POST /api/v1/comfyui/servers`
- `GET /api/comfyui/servers` → `GET /api/v1/comfyui/servers`
- `GET /api/comfyui/servers/{id}` → `GET /api/v1/comfyui/servers/{id}`
- `GET /api/comfyui/servers/{id}/info` → `GET /api/v1/comfyui/servers/{id}/info`
- `DELETE /api/comfyui/servers/{id}` → `DELETE /api/v1/comfyui/servers/{id}`
- `GET /api/comfyui/servers/{id}/workflows` → `GET /api/v1/comfyui/servers/{id}/workflows`

### Models
- `GET /api/models` → `GET /api/v1/comfyui/models`
- `PUT /api/models/{id}` → `PUT /api/v1/comfyui/models/{id}`
- `DELETE /api/models/{id}` → `DELETE /api/v1/comfyui/models/{id}`
- `POST /api/models/{id}/sync-civitai` → `POST /api/v1/comfyui/models/{id}/sync-civitai`
- `POST /api/models/{id}/search-civitai` → `POST /api/v1/comfyui/models/{id}/search-civitai`
- `POST /api/models/{id}/link-civitai` → `POST /api/v1/comfyui/models/{id}/link-civitai`
- `GET /api/active-models` → `GET /api/v1/comfyui/active-models`
- `GET /api/backends` → `GET /api/v1/comfyui/backends`
- `GET /api/backends/{id}/models` → `GET /api/v1/comfyui/backends/{id}/models`

### Characters
- `POST /api/characters` → `POST /api/v1/characters`
- `GET /api/characters` → `GET /api/v1/characters`
- `GET /api/characters/{id}` → `GET /api/v1/characters/{id}`
- `PUT /api/characters/{id}` → `PUT /api/v1/characters/{id}`
- `DELETE /api/characters/{id}` → `DELETE /api/v1/characters/{id}`
- `POST /api/characters/{id}/apply/{clip_id}` → `POST /api/v1/characters/{id}/apply/{clip_id}`
- `POST /api/characters/{id}/generate` → `POST /api/v1/characters/{id}/generate`
- `POST /api/characters/train-lora` → `POST /api/v1/characters/train-lora`

### Style Templates
- `POST /api/style-templates` → `POST /api/v1/style-templates`
- `GET /api/style-templates` → `GET /api/v1/style-templates`
- `GET /api/style-templates/{id}` → `GET /api/v1/style-templates/{id}`
- `PUT /api/style-templates/{id}` → `PUT /api/v1/style-templates/{id}`
- `DELETE /api/style-templates/{id}` → `DELETE /api/v1/style-templates/{id}`
- `POST /api/style-templates/{id}/use` → `POST /api/v1/style-templates/{id}/use`

### Media Uploads
- `POST /api/upload-face-image` → `POST /api/v1/media/upload-face-image`
- `POST /api/upload-character-images` → `POST /api/v1/media/upload-character-images`

### Generation Pool
- `POST /api/pool` → `POST /api/v1/generation/pool`
- `GET /api/pool/{project_id}` → `GET /api/v1/generation/pool/{project_id}`
- `GET /api/pool/item/{id}` → `GET /api/v1/generation/pool/item/{id}`
- `PUT /api/pool/item/{id}` → `PUT /api/v1/generation/pool/item/{id}`
- `DELETE /api/pool/item/{id}` → `DELETE /api/v1/generation/pool/item/{id}`
- `POST /api/pool/item/{id}/apply-to-clip/{clip_id}` → `POST /api/v1/generation/pool/item/{id}/apply-to-clip/{clip_id}`

### Queue
- `POST /api/queue/jobs` → `POST /api/v1/queue/jobs`
- `GET /api/queue/status` → `GET /api/v1/queue/status`
- `GET /api/queue/jobs` → `GET /api/v1/queue/jobs`
- `GET /api/queue/jobs/{id}` → `GET /api/v1/queue/jobs/{id}`
- `GET /api/queue/projects/{id}/jobs` → `GET /api/v1/queue/projects/{id}/jobs`
- `POST /api/queue/servers/{id}/register` → `POST /api/v1/queue/servers/{id}/register`
- `GET /api/queue/servers/{id}/next` → `GET /api/v1/queue/servers/{id}/next`
- `POST /api/queue/jobs/{id}/complete` → `POST /api/v1/queue/jobs/{id}/complete`

### Export
- `GET /api/projects/{id}/export/fcpxml` → `GET /api/v1/projects/{id}/export/fcpxml`
- `GET /api/projects/{id}/export/edl` → `GET /api/v1/projects/{id}/export/edl`
- `GET /api/projects/{id}/export/resolve` → `GET /api/v1/projects/{id}/export/resolve`
- `GET /api/projects/{id}/export/json` → `GET /api/v1/projects/{id}/export/json`

### FaceFusion
- `POST /api/facefusion/enhance-face` → `POST /api/v1/facefusion/enhance-face` (if added to v1)
- `POST /api/facefusion/adjust-face-age` → `POST /api/v1/facefusion/adjust-face-age` (if added to v1)
- `POST /api/facefusion/swap-face` → `POST /api/v1/facefusion/swap-face` (if added to v1)
- `GET /api/facefusion/status` → `GET /api/v1/facefusion/status` (if added to v1)
- `POST /api/facefusion/batch-process` → `POST /api/v1/facefusion/batch-process` (if added to v1)

### Health & Info
- `GET /api/health` → `GET /api/v1/health`
- `GET /api/` → `GET /api/v1/` (root endpoint)

## Breaking Changes
None. The v1 API is functionally identical to the legacy API at this time. Future versions (v2, v3) may introduce breaking changes, but v1 maintains backward compatibility.

## Response Headers
All API responses include:
- `X-API-Version: v1` - Indicates the API version being used
- Legacy endpoints also include: `Deprecated: true` and `Sunset: 2025-06-01`

## Testing Your Migration
1. Update your API base URL to include `/v1`
2. Run your application and check for:
   - Console warnings about deprecated endpoints
   - `Deprecated` headers in network responses
3. Verify all functionality works as expected
4. Remove any references to legacy `/api` endpoints

## Support
For migration assistance or questions, contact the development team or file an issue in the repository.
