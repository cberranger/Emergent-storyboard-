# Database Schema Documentation

**Database:** MongoDB (Motor async driver)  
**Database Name:** `storyboard` (configurable via `DB_NAME` env var)  
**Last Updated:** 2024

---

## Table of Contents
1. [Core Collections](#core-collections)
2. [FaceFusion Collections](#facefusion-collections)
3. [Model Management Collections](#model-management-collections)
4. [Job Management Collections](#job-management-collections)
5. [Authentication Collections](#authentication-collections)
6. [Indexes](#indexes)
7. [Migration Notes](#migration-notes)

---

## Core Collections

### `projects`
Top-level container for all storyboard content.

**Fields:**
```javascript
{
  "id": "string (UUID)",               // Unique identifier (indexed)
  "name": "string",                    // Project name
  "description": "string",             // Project description
  "created_at": "datetime",            // Creation timestamp (indexed)
  "updated_at": "datetime",            // Last update timestamp
  "thumbnail_url": "string (optional)" // Project thumbnail
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ created_at: -1 }` - For recent project queries

---

### `scenes`
Scenes within a project, can be nested (parent-child relationships).

**Fields:**
```javascript
{
  "id": "string (UUID)",                 // Unique identifier (indexed)
  "project_id": "string",                // Parent project (indexed)
  "name": "string",                      // Scene name
  "description": "string",               // Scene description
  "order": "integer",                    // Display order (indexed with project_id)
  "parent_scene_id": "string (optional)",// Parent scene for nesting (indexed)
  "is_alternate": "boolean",             // Alternate timeline flag (indexed)
  "clips": "array",                      // Array of clip objects (embedded)
  "created_at": "datetime",              // Creation timestamp
  "updated_at": "datetime"               // Last update timestamp
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ project_id: 1, order: 1 }` - COMPOUND (ordered scene retrieval)
- `{ parent_scene_id: 1 }` - For hierarchical queries
- `{ is_alternate: 1 }` - For filtering alternate timelines

---

### `clips`
Individual content units within scenes (images, videos, text).

**Fields:**
```javascript
{
  "id": "string (UUID)",                   // Unique identifier (indexed)
  "scene_id": "string",                    // Parent scene (indexed)
  "project_id": "string",                  // Parent project
  "type": "string",                        // "image" | "video" | "text"
  "order": "integer",                      // Display order (indexed with scene_id)
  "timeline_position": "float",            // Position in timeline (indexed with scene_id)
  "duration": "float",                     // Duration in seconds
  "content": "string",                     // Text content (for type=text)
  "media_url": "string (optional)",        // URL to media file
  "thumbnail_url": "string (optional)",    // Thumbnail URL
  "image_prompt": "string (optional)",     // Image generation prompt
  "video_prompt": "string (optional)",     // Video generation prompt
  "generated_images": "array",             // Array of generated image URLs
  "generated_videos": "array",             // Array of generated video URLs
  "comfyui_server_id": "string (optional)",// ComfyUI server used for generation
  "character_id": "string (optional)",     // Associated character
  "style_template_id": "string (optional)",// Applied style template
  "inference_config_id": "string (optional)",// Inference configuration used
  "created_at": "datetime",                // Creation timestamp
  "updated_at": "datetime"                 // Last update timestamp
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ scene_id: 1, order: 1 }` - COMPOUND (ordered clip retrieval)
- `{ scene_id: 1, timeline_position: 1 }` - COMPOUND (timeline queries)

---

### `characters`
Character definitions with reference images and FaceFusion settings.

**Fields:**
```javascript
{
  "id": "string (UUID)",                                  // Unique identifier (indexed)
  "project_id": "string",                                 // Parent project (indexed)
  "name": "string",                                       // Character name (indexed with project_id)
  "description": "string",                                // Character description
  "reference_images": "array of strings",                 // URLs to reference images
  "lora": "string (optional)",                            // LoRA model identifier
  "trigger_words": "string (optional)",                   // LoRA trigger words
  "style_notes": "string (optional)",                     // Style/appearance notes
  "facefusion_processing_history": "array",               // FaceFusion operation history (see below)
  "facefusion_preferred_settings": "object (optional)",   // Preferred FaceFusion settings (see below)
  "facefusion_output_gallery": "object",                  // Categorized FaceFusion outputs (see below)
  "created_at": "datetime",                               // Creation timestamp
  "updated_at": "datetime"                                // Last update timestamp
}
```

**FaceFusion Processing History Entry:**
```javascript
{
  "id": "string (UUID)",                   // Entry identifier
  "operation_type": "string",              // "enhance" | "age_adjust" | "swap" | "edit" | "mask" | "detect"
  "input_image_url": "string",             // Input image URL
  "output_image_url": "string",            // Result image URL
  "parameters": "object",                  // Operation-specific parameters (see below)
  "success": "boolean",                    // Operation success status
  "error_message": "string (optional)",    // Error message if failed
  "processing_time_seconds": "float",      // Processing duration
  "created_at": "datetime"                 // Timestamp
}
```

**Operation Parameters by Type:**
```javascript
// For operation_type: "enhance"
{
  "enhancement_model": "gfpgan_1.4" | "codeformer" | "restoreformer_plus_plus",
  "face_enhancer_blend": "float (0.0-1.0)"
}

// For operation_type: "age_adjust"
{
  "target_age": "integer (0-100)",
  "age_adjustment_blend": "float (0.0-1.0)"
}

// For operation_type: "swap"
{
  "source_face_url": "string",
  "target_image_url": "string",
  "face_swapper_model": "inswapper_128" | "inswapper_256"
}

// For operation_type: "edit"
{
  "face_editor_eyebrow_direction": "integer (-100 to 100)",
  "face_editor_eye_gaze_horizontal": "integer (-100 to 100)",
  "face_editor_eye_gaze_vertical": "integer (-100 to 100)",
  "face_editor_eye_open_ratio": "integer (-100 to 100)",
  "face_editor_lip_open_ratio": "integer (-100 to 100)",
  "face_editor_mouth_grim": "integer (-100 to 100)",
  "face_editor_mouth_pout": "integer (-100 to 100)",
  "face_editor_mouth_purse": "integer (-100 to 100)",
  "face_editor_mouth_smile": "integer (-100 to 100)",
  "face_editor_mouth_position_horizontal": "integer (-100 to 100)",
  "face_editor_mouth_position_vertical": "integer (-100 to 100)",
  "face_editor_head_pitch": "integer (-100 to 100)",
  "face_editor_head_yaw": "integer (-100 to 100)",
  "face_editor_head_roll": "integer (-100 to 100)"
}
```

**FaceFusion Preferred Settings:**
```javascript
{
  "enhancement_model": "string (default: gfpgan_1.4)",
  "face_enhancer_blend": "float (0.0-1.0, default: 1.0)",
  "age_adjustment_blend": "float (0.0-1.0, default: 1.0)",
  "face_mask_types": "array of strings (default: ['box'])",
  "face_selector_mode": "one | many | all (default: one)",
  "face_selector_order": "string (default: left-right)",
  "face_detector_model": "string (default: yoloface)",
  "face_detector_size": "string (default: 640x640)",
  "face_swapper_model": "string (default: inswapper_128)",
  "face_editor_eyebrow_direction": "integer (optional, -100 to 100)",
  "face_editor_eye_gaze_horizontal": "integer (optional, -100 to 100)",
  "face_editor_eye_gaze_vertical": "integer (optional, -100 to 100)",
  "face_editor_eye_open_ratio": "integer (optional, -100 to 100)",
  "face_editor_lip_open_ratio": "integer (optional, -100 to 100)",
  "face_editor_mouth_grim": "integer (optional, -100 to 100)",
  "face_editor_mouth_pout": "integer (optional, -100 to 100)",
  "face_editor_mouth_purse": "integer (optional, -100 to 100)",
  "face_editor_mouth_smile": "integer (optional, -100 to 100)",
  "face_editor_mouth_position_horizontal": "integer (optional, -100 to 100)",
  "face_editor_mouth_position_vertical": "integer (optional, -100 to 100)",
  "face_editor_head_pitch": "integer (optional, -100 to 100)",
  "face_editor_head_yaw": "integer (optional, -100 to 100)",
  "face_editor_head_roll": "integer (optional, -100 to 100)"
}
```

**FaceFusion Output Gallery:**
```javascript
{
  "enhanced_faces": "array of strings",           // URLs to enhanced face images
  "age_variants": "object (int -> string)",       // Age -> image URL mapping (e.g., {25: "url", 45: "url"})
  "swapped_faces": "array of strings",            // URLs to face-swapped images
  "edited_expressions": "array of strings",       // URLs to expression-edited images
  "custom_outputs": "array of strings"            // URLs to other custom outputs
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ project_id: 1, name: 1 }` - COMPOUND (project-scoped character lookups)

**Association Notes:**
- Characters can be referenced by clips via `character_id` field
- FaceFusion processing history tracks all operations performed on character images
- Output gallery provides quick access to categorized results
- Preferred settings allow reusing optimal parameters for consistency

---

### `style_templates`
Reusable style templates for consistent generation.

**Fields:**
```javascript
{
  "id": "string (UUID)",                 // Unique identifier (indexed)
  "project_id": "string",                // Parent project (indexed)
  "name": "string",                      // Template name (indexed with project_id)
  "description": "string",               // Template description
  "prompt_additions": "string",          // Additional prompt text
  "negative_prompt": "string",           // Negative prompt
  "style_strength": "float",             // Style strength (0.0-1.0)
  "use_count": "integer",                // Times used (for popularity tracking)
  "created_at": "datetime",              // Creation timestamp
  "updated_at": "datetime"               // Last update timestamp
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ project_id: 1, name: 1 }` - COMPOUND (project-scoped template lookups)

---

## FaceFusion Collections

### `facefusion_jobs`
Queue for FaceFusion batch processing operations.

**Fields:**
```javascript
{
  "id": "string (UUID)",                   // Unique identifier (indexed)
  "character_id": "string (optional)",     // Associated character (indexed)
  "project_id": "string",                  // Parent project (indexed)
  "job_type": "string",                    // "enhance" | "age_adjust" | "swap" | "batch"
  "status": "string",                      // "queued" | "processing" | "completed" | "failed" (indexed)
  "priority": "integer",                   // Job priority (indexed)
  "input_data": "object",                  // Job-specific input parameters
  "output_data": "object (optional)",      // Results upon completion
  "error_message": "string (optional)",    // Error message if failed
  "progress": "float",                     // Progress percentage (0.0-100.0)
  "started_at": "datetime (optional)",     // Processing start time
  "completed_at": "datetime (optional)",   // Completion time
  "created_at": "datetime",                // Queue entry timestamp (indexed)
  "updated_at": "datetime"                 // Last update timestamp
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ status: 1, priority: -1, created_at: 1 }` - COMPOUND (job queue processing order)
- `{ character_id: 1 }` - For character-specific job queries
- `{ project_id: 1, created_at: -1 }` - For project job history

---

### `facefusion_presets`
Saved FaceFusion parameter presets for quick reuse.

**Fields:**
```javascript
{
  "id": "string (UUID)",                   // Unique identifier (indexed)
  "name": "string",                        // Preset name (indexed)
  "description": "string (optional)",      // Preset description
  "operation_type": "string",              // "enhance" | "age_adjust" | "swap" | "edit"
  "parameters": "object",                  // Operation-specific parameters
  "user_id": "string (optional)",          // Creator user ID
  "is_public": "boolean",                  // Public/private preset
  "use_count": "integer",                  // Times used
  "created_at": "datetime",                // Creation timestamp
  "updated_at": "datetime"                 // Last update timestamp
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ name: 1 }` - For preset lookup
- `{ operation_type: 1, is_public: 1 }` - For browsing public presets by type

---

## Model Management Collections

### `database_models`
Active AI models available for generation.

**Fields:**
```javascript
{
  "id": "string",                          // Model identifier (indexed)
  "name": "string",                        // Display name
  "type": "string",                        // "checkpoint" | "lora" | "embedding" | "controlnet"
  "base_model": "string",                  // "SD 1.5" | "SDXL" | "SD 2.0" | "Pony"
  "path": "string",                        // File path or identifier
  "description": "string",                 // Model description
  "trigger_words": "string (optional)",    // Required trigger words
  "is_active": "boolean",                  // Active status (indexed)
  "is_nsfw": "boolean",                    // NSFW flag
  "tags": "array of strings",              // Searchable tags
  "civitai_id": "integer (optional)",      // CivitAI model ID
  "created_at": "datetime",                // Creation timestamp
  "updated_at": "datetime"                 // Last update timestamp
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ is_active: 1, type: 1 }` - For filtering active models by type
- `{ base_model: 1, is_active: 1 }` - For base model filtering

---

### `inference_configurations`
Standardized parameter presets for active models.

**Fields:**
```javascript
{
  "model_id": "string",                    // Model ID (indexed, references database_models.id)
  "preset_type": "string",                 // "quality" | "speed"
  "parameters": {
    "steps": "integer",
    "cfg_scale": "float",
    "sampler_name": "string",
    "scheduler": "string",
    "denoise": "float"
  },
  "description": "string",                 // Preset description
  "created_at": "datetime",                // Creation timestamp
  "updated_at": "datetime"                 // Last update timestamp
}
```

**Indexes:**
- `{ model_id: 1, preset_type: 1 }` - COMPOUND UNIQUE (one quality + one speed per model)

---

### `civitai_models`
CivitAI model catalog for discovery.

**Fields:**
```javascript
{
  "id": "integer",                         // CivitAI model ID (indexed)
  "name": "string",                        // Model name
  "type": "string",                        // Model type
  "description": "string",                 // Model description
  "tags": "array of strings",              // Model tags
  "nsfw": "boolean",                       // NSFW flag
  "stats": "object",                       // Download/rating stats
  "model_versions": "array",               // Available versions
  "creator": "object",                     // Creator information
  "created_at": "datetime",                // Creation timestamp
  "updated_at": "datetime"                 // Last update timestamp
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ type: 1, nsfw: 1 }` - For filtered browsing

---

## Job Management Collections

### `generation_batches`
Batch generation job tracking.

**Fields:**
```javascript
{
  "id": "string (UUID)",                   // Unique identifier (indexed)
  "project_id": "string",                  // Parent project (indexed)
  "clip_id": "string (optional)",          // Associated clip
  "status": "string",                      // "queued" | "processing" | "completed" | "failed" (indexed)
  "total_jobs": "integer",                 // Total jobs in batch
  "completed_jobs": "integer",             // Completed job count
  "failed_jobs": "integer",                // Failed job count
  "comfyui_server_id": "string",           // Server processing the batch
  "prompt_data": "object",                 // Generation parameters
  "results": "array",                      // Generated image/video URLs
  "error_message": "string (optional)",    // Error message if failed
  "created_at": "datetime",                // Creation timestamp (indexed)
  "updated_at": "datetime"                 // Last update timestamp
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ project_id: 1, created_at: -1 }` - COMPOUND (project batch history)
- `{ status: 1 }` - For active batch filtering

---

## Authentication Collections

### `users`
User accounts and authentication.

**Fields:**
```javascript
{
  "id": "string (UUID)",                   // Unique identifier (indexed)
  "username": "string",                    // Username (indexed, unique)
  "email": "string",                       // Email address (indexed, unique)
  "hashed_password": "string",             // Bcrypt hashed password
  "is_active": "boolean",                  // Account active status
  "is_admin": "boolean",                   // Admin privileges
  "created_at": "datetime",                // Registration timestamp
  "updated_at": "datetime"                 // Last update timestamp
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ username: 1 }` - UNIQUE
- `{ email: 1 }` - UNIQUE

---

## Supporting Collections

### `comfyui_servers`
ComfyUI server configuration and status.

**Fields:**
```javascript
{
  "id": "string (UUID)",                   // Unique identifier (indexed)
  "name": "string",                        // Server name
  "url": "string",                         // Server URL (indexed, unique)
  "is_active": "boolean",                  // Active status (indexed)
  "status": "string",                      // "online" | "offline" | "error"
  "last_check": "datetime",                // Last health check timestamp
  "capabilities": "object",                // Server capabilities
  "created_at": "datetime",                // Creation timestamp
  "updated_at": "datetime"                 // Last update timestamp
}
```

**Indexes:**
- `{ id: 1 }` - UNIQUE
- `{ url: 1 }` - UNIQUE
- `{ is_active: 1 }` - For active server filtering

---

## Indexes

### Complete Index Listing

```javascript
// Core Collections
db.projects.createIndex({ id: 1 }, { unique: true })
db.projects.createIndex({ created_at: -1 })

db.scenes.createIndex({ id: 1 }, { unique: true })
db.scenes.createIndex({ project_id: 1, order: 1 })
db.scenes.createIndex({ parent_scene_id: 1 })
db.scenes.createIndex({ is_alternate: 1 })

db.clips.createIndex({ id: 1 }, { unique: true })
db.clips.createIndex({ scene_id: 1, order: 1 })
db.clips.createIndex({ scene_id: 1, timeline_position: 1 })

db.characters.createIndex({ id: 1 }, { unique: true })
db.characters.createIndex({ project_id: 1, name: 1 })

db.style_templates.createIndex({ id: 1 }, { unique: true })
db.style_templates.createIndex({ project_id: 1, name: 1 })

// FaceFusion Collections
db.facefusion_jobs.createIndex({ id: 1 }, { unique: true })
db.facefusion_jobs.createIndex({ status: 1, priority: -1, created_at: 1 })
db.facefusion_jobs.createIndex({ character_id: 1 })
db.facefusion_jobs.createIndex({ project_id: 1, created_at: -1 })

db.facefusion_presets.createIndex({ id: 1 }, { unique: true })
db.facefusion_presets.createIndex({ name: 1 })
db.facefusion_presets.createIndex({ operation_type: 1, is_public: 1 })

// Model Management Collections
db.database_models.createIndex({ id: 1 }, { unique: true })
db.database_models.createIndex({ is_active: 1, type: 1 })
db.database_models.createIndex({ base_model: 1, is_active: 1 })

db.inference_configurations.createIndex({ model_id: 1, preset_type: 1 }, { unique: true })

db.civitai_models.createIndex({ id: 1 }, { unique: true })
db.civitai_models.createIndex({ type: 1, nsfw: 1 })

// Job Management Collections
db.generation_batches.createIndex({ id: 1 }, { unique: true })
db.generation_batches.createIndex({ project_id: 1, created_at: -1 })
db.generation_batches.createIndex({ status: 1 })

// Authentication Collections
db.users.createIndex({ id: 1 }, { unique: true })
db.users.createIndex({ username: 1 }, { unique: true })
db.users.createIndex({ email: 1 }, { unique: true })

// Supporting Collections
db.comfyui_servers.createIndex({ id: 1 }, { unique: true })
db.comfyui_servers.createIndex({ url: 1 }, { unique: true })
db.comfyui_servers.createIndex({ is_active: 1 })
```

---

## Migration Notes

### Adding FaceFusion Support to Existing Characters

If your database has existing character documents without FaceFusion fields, they will need to be migrated. The application handles this gracefully by providing default values, but you can explicitly migrate using the following script:

```javascript
// MongoDB Shell Migration Script
db.characters.updateMany(
  { facefusion_processing_history: { $exists: false } },
  {
    $set: {
      facefusion_processing_history: [],
      facefusion_preferred_settings: null,
      facefusion_output_gallery: {
        enhanced_faces: [],
        age_variants: {},
        swapped_faces: [],
        edited_expressions: [],
        custom_outputs: []
      }
    }
  }
)
```

### Character Collection Schema Updates

**Previous Schema (Pre-FaceFusion):**
```javascript
{
  "id": "string",
  "project_id": "string",
  "name": "string",
  "description": "string",
  "reference_images": "array",
  "lora": "string",
  "trigger_words": "string",
  "style_notes": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**New Schema (With FaceFusion):**
```javascript
{
  "id": "string",
  "project_id": "string",
  "name": "string",
  "description": "string",
  "reference_images": "array",
  "lora": "string",
  "trigger_words": "string",
  "style_notes": "string",
  // NEW FIELDS BELOW
  "facefusion_processing_history": "array",      // Processing history
  "facefusion_preferred_settings": "object",     // Preferred settings
  "facefusion_output_gallery": "object",         // Categorized outputs
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Migration Impact:**
- ✅ No breaking changes - new fields are optional with defaults
- ✅ Existing character queries continue to work
- ✅ Frontend components handle missing fields gracefully
- ⚠️ Recommended to run migration script to ensure consistent data structure

### New Collections Required

The following collections must be created when deploying FaceFusion support:

1. **facefusion_jobs** - Required for batch processing queue
2. **facefusion_presets** - Optional, for saved parameter presets

These are created automatically by the updated `init_db.py` script.

### Backward Compatibility

- All existing queries remain compatible
- Character DTOs provide default values for missing FaceFusion fields
- No data loss occurs if FaceFusion features are not used
- Applications can detect FaceFusion support by checking for field existence

---

## Related Documentation

- **FaceFusion Integration:** See `docs/FACEFUSION_INTEGRATION.md`
- **FaceFusion API Catalog:** See `docs/FACEFUSION_API_CATALOG.md`
- **Database Initialization:** See `backend/scripts/init_db.py`
- **Character DTOs:** See `backend/dtos/character_dtos.py`
- **Repository Pattern:** See `backend/DATABASE_AUDIT.md`
