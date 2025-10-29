# Database Layer Audit Report

**Generated:** 2024
**Database:** MongoDB (Motor async driver)
**Database Name:** `storyboard` (configurable via `DB_NAME` env var)

---

## Executive Summary

✅ **Strengths:**
- Robust connection management with retry logic and health checks
- Consistent repository pattern implementation across all repositories
- Well-defined indexes for query performance
- Comprehensive error handling hierarchy
- Clear data model with DTOs and validation

⚠️ **Areas for Improvement:**
- No soft delete implementation (hard deletes used throughout)
- Inconsistent data access patterns (mix of repository pattern and direct db access)
- Missing error handling in repository layer (no try-catch)
- No transaction support for multi-collection operations
- Index strategy could be expanded for common queries
- Missing database migration system

---

## 1. MongoDB Connection Handling

### Implementation: `database.py`

**Status:** ✅ **GOOD**

#### Features:
- **DatabaseManager class** with singleton pattern (`db_manager`)
- **Retry logic:** 5 attempts with 3-second delays
- **Connection timeouts:** Server selection (5s), connect (10s), socket (10s)
- **Health checks:** `health_check()` method using ping command
- **Graceful shutdown:** `disconnect()` method
- **Environment validation:** URL format checking
- **Write/read retries:** `retryWrites=True`, `retryReads=True`

#### Configuration:
```python
MONGO_URL: mongodb://localhost:27017 (default)
DB_NAME: storyboard (default)
max_retries: 5
retry_delay: 3 seconds
```

#### FastAPI Dependency:
```python
async def get_database() -> AsyncIOMotorDatabase
```
- Automatically reconnects if connection lost
- Raises `ConnectionError` if unavailable

#### Recommendations:
- ✅ Connection pooling configured via Motor defaults
- ✅ Error handling robust
- ⚠️ Consider adding connection pool size configuration
- ⚠️ Add metrics/logging for connection pool status

---

## 2. Repository Pattern Implementation

### Base Repository: `repositories/base_repository.py`

**Status:** ✅ **CONSISTENT**

#### Base CRUD Operations:

| Method | Parameters | Return Type | Notes |
|--------|-----------|-------------|-------|
| `create()` | document: Dict | Dict | Inserts document |
| `find_by_id()` | document_id: str | Optional[Dict] | Query by `id` field |
| `find_one()` | query: Dict | Optional[Dict] | Single document |
| `find_many()` | query, sort, limit | List[Dict] | Multiple documents |
| `update_by_id()` | document_id, updates | Optional[Dict] | Uses `$set` operator |
| `update_one()` | query, updates | Optional[Dict] | Uses `$set` operator |
| `delete_by_id()` | document_id: str | bool | Hard delete |
| `delete_many()` | query: Dict | int | Hard delete, returns count |

#### Key Patterns:
- All queries use custom `id` field (not MongoDB `_id`)
- `find_one_and_update` with `ReturnDocument.AFTER` for atomic updates
- `$set` operator used for all updates
- No error handling in base repository (delegated to service layer)

### Repository Implementations:

#### ✅ ProjectRepository (`repositories/project_repository.py`)
```python
Collection: db.projects
Extends: BaseRepository
Custom Methods:
  - list_projects(limit, include_scenes, scenes_collection)
  - update_project(project_id, updates)
```

#### ✅ SceneRepository (`repositories/scene_repository.py`)
```python
Collection: db.scenes
Extends: BaseRepository
Custom Methods:
  - list_by_project(project_id, include_clips, clips_collection)
  - update_scene(scene_id, updates)
```

#### ✅ ClipRepository (`repositories/clip_repository.py`)
```python
Collection: db.clips
Extends: BaseRepository
Custom Methods:
  - list_by_scene(scene_id)
  - list_by_project(project_id)
  - update_gallery(clip_id, generated_images, generated_videos, ...)
  - update_prompts(clip_id, image_prompt, video_prompt)
  - update_timeline_position(clip_id, timeline_position)
```

#### ✅ ComfyUIRepository (`repositories/comfyui_repository.py`)
```python
Collection: db.comfyui_servers
Extends: BaseRepository
Custom Methods:
  - find_by_url(url)
  - set_active(server_id, is_active)
```

### Pattern Compliance:

✅ **Strengths:**
- All repositories extend BaseRepository
- Consistent method signatures
- Separation of concerns (repos handle data access, services handle business logic)
- Type hints throughout

⚠️ **Issues:**
- **No error handling in repository layer** - no try-catch blocks
- **Mixed access patterns** - many services bypass repositories and use `db.collection` directly
- **No transaction support** - multi-collection operations not atomic
- **Inconsistent datetime handling** - some repos add timestamps, others don't

---

## 3. Error Handling Assessment

### Error Hierarchy: `utils/errors.py`

**Status:** ✅ **COMPREHENSIVE**

#### Base Class:
```python
class APIError(HTTPException)
  - Standardized error formatting
  - Error codes (e.g., "VALIDATION_ERROR")
  - Automatic logging
  - Structured details dict
```

#### Error Categories:

**400 Bad Request:**
- `ValidationError` - Request validation failed
- `InvalidParameterError` - Invalid parameter provided

**404 Not Found:**
- `ResourceNotFoundError` (base)
- `ProjectNotFoundError`
- `SceneNotFoundError`
- `ClipNotFoundError`
- `ServerNotFoundError`

**409 Conflict:**
- `ConflictError` - Resource conflict
- `DuplicateResourceError` - Resource already exists

**413 Payload Too Large:**
- `FileTooLargeError`

**422 Unprocessable Entity:**
- `InvalidFileTypeError`

**500 Internal Server Error:**
- `InternalServerError`
- `DatabaseError`
- `ExternalServiceError`
- `ServerError`
- `GenerationError`

**503 Service Unavailable:**
- `ServiceUnavailableError`
- `DatabaseUnavailableError`

**507 Insufficient Storage:**
- `InsufficientStorageError`

#### Helper Functions:
```python
handle_db_error(operation, error) - Raises DatabaseError
require_resource(resource, type, id) - Raises ResourceNotFoundError if None
```

### Error Handling in Practice:

✅ **Service Layer:**
- Validates resources exist before operations
- Raises appropriate domain errors
- Example: `ProjectService.get_project()` raises `ProjectNotFoundError`

⚠️ **Repository Layer:**
- **NO error handling** - no try-catch blocks
- Database exceptions bubble up to service layer
- Could cause unclear error messages for users

⚠️ **Connection Layer:**
- Good error handling in `database.py`
- Catches `ConnectionFailure`, `ServerSelectionTimeoutError`
- Could improve error propagation to API layer

#### Recommendations:
1. Add try-catch in repository methods to wrap MongoDB exceptions
2. Create database-specific error types for common failures
3. Add timeout handling for long-running queries
4. Implement retry logic for transient failures in repositories

---

## 4. Index Strategy Analysis

### Current Implementation: `scripts/init_db.py` and `scripts/init_db.js`

**Status:** ✅ **ADEQUATE** but can be improved

### Indexes by Collection:

#### **projects**
```javascript
{ id: 1 } - UNIQUE
{ created_at: -1 }
```
✅ Good for lookups and listing recent projects
⚠️ Missing: No index on `name` for search

#### **scenes**
```javascript
{ id: 1 } - UNIQUE
{ project_id: 1, order: 1 } - COMPOUND
{ parent_scene_id: 1 }
{ is_alternate: 1 }
```
✅ Excellent coverage for hierarchical queries
✅ Compound index supports ordered scene retrieval

#### **clips**
```javascript
{ id: 1 } - UNIQUE
{ scene_id: 1, order: 1 } - COMPOUND
{ scene_id: 1, timeline_position: 1 } - COMPOUND
```
✅ Good for scene-based queries
✅ Timeline position indexed for temporal queries
⚠️ Missing: No index on `project_id` (used in some queries)
⚠️ Missing: No index on `character_id` (used for character-clip relationships)

#### **characters**
```javascript
{ id: 1 } - UNIQUE
{ project_id: 1, name: 1 } - COMPOUND
```
✅ Good for project-scoped character lookups

#### **style_templates**
```javascript
{ id: 1 } - UNIQUE
{ project_id: 1, name: 1 } - COMPOUND
```
✅ Good for project-scoped template lookups
⚠️ Missing: No index on `use_count` (queries sort by use_count)

#### **comfyui_servers**
```javascript
{ id: 1 } - UNIQUE
{ url: 1 } - UNIQUE
```
✅ Prevents duplicate server URLs
⚠️ Missing: No index on `is_active` (commonly filtered)

#### **generation_batches**
```javascript
{ id: 1 } - UNIQUE
{ project_id: 1, created_at: -1 } - COMPOUND
```
✅ Good for project batch history
⚠️ Missing: No index on `status` (commonly filtered)

### Collections Without Defined Indexes:

⚠️ **Missing Index Definitions:**
- `active_backend_models` - Used in `active_models_service.py`
- `backends` - Used in `active_models_service.py`
- `model_sync_status` - Used in `active_models_service.py`
- `generation_pool` - Used extensively in `server.py`
- `civitai_models` - Large collection, needs indexes for search
- `model_profiles` - Used in import scripts
- `database_models` - Used in import scripts

### Recommended Additional Indexes:

```javascript
// clips - add project_id for direct project queries
db.clips.createIndex({ project_id: 1, created_at: -1 });
db.clips.createIndex({ character_id: 1 });

// style_templates - add use_count for sorting
db.style_templates.createIndex({ use_count: -1 });

// comfyui_servers - add is_active for filtering
db.comfyui_servers.createIndex({ is_active: 1 });

// generation_batches - add status for filtering
db.generation_batches.createIndex({ status: 1, created_at: -1 });

// generation_pool - critical for performance
db.generation_pool.createIndex({ id: 1 }, { unique: true });
db.generation_pool.createIndex({ clip_id: 1 });
db.generation_pool.createIndex({ status: 1, created_at: -1 });

// active_backend_models
db.active_backend_models.createIndex({ id: 1 }, { unique: true });
db.active_backend_models.createIndex({ backend_id: 1, model_type: 1 });
db.active_backend_models.createIndex({ model_id: 1 });
db.active_backend_models.createIndex({ is_active: 1, last_seen: -1 });

// backends
db.backends.createIndex({ id: 1 }, { unique: true });
db.backends.createIndex({ is_online: 1, last_check: -1 });

// model_sync_status
db.model_sync_status.createIndex({ model_id: 1 }, { unique: true });
db.model_sync_status.createIndex({ sync_status: 1, last_sync_attempt: -1 });
db.model_sync_status.createIndex({ civitai_model_id: 1 });

// civitai_models - for search and filtering
db.civitai_models.createIndex({ name: "text" });
db.civitai_models.createIndex({ baseModel: 1, type: 1 });
db.civitai_models.createIndex({ type: 1 });
```

---

## 5. Soft Delete Implementation

### Current Status: ❌ **NOT IMPLEMENTED**

**Finding:** All delete operations are **hard deletes**.

### Evidence:
```python
# BaseRepository uses delete_one/delete_many
async def delete_by_id(self, document_id: str) -> bool:
    result = await self._collection.delete_one({"id": document_id})
    return result.deleted_count == 1

# Services call repository delete methods directly
await db.characters.delete_one({"id": character_id})
await db.style_templates.delete_one({"id": template_id})
```

### No Soft Delete Patterns Found:
- ❌ No `deleted_at` timestamp field in any DTOs
- ❌ No `is_deleted` boolean field in any DTOs
- ❌ No soft delete methods in repositories
- ❌ No queries filtering out deleted records

### Impact:
- **Data loss risk:** Accidental deletions cannot be recovered
- **No audit trail:** Cannot track when/why items were deleted
- **No "recycle bin" functionality:** Users cannot restore deleted items
- **Referential integrity issues:** Deleting projects/scenes/clips can orphan related data

### Recommended Implementation:

#### 1. Add Soft Delete Fields to DTOs:
```python
class ProjectResponseDTO(BaseModel):
    # ... existing fields ...
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None  # user ID if auth implemented
```

#### 2. Add Soft Delete Methods to BaseRepository:
```python
async def soft_delete_by_id(self, document_id: str, deleted_by: Optional[str] = None) -> Optional[Dict[str, Any]]:
    updates = {
        "deleted_at": datetime.now(timezone.utc),
        "deleted_by": deleted_by
    }
    return await self._collection.find_one_and_update(
        {"id": document_id, "deleted_at": None},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )

async def restore_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
    return await self._collection.find_one_and_update(
        {"id": document_id, "deleted_at": {"$ne": None}},
        {"$set": {"deleted_at": None, "deleted_by": None}},
        return_document=ReturnDocument.AFTER,
    )

async def find_with_deleted(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Include deleted items
    return await self._collection.find(query).to_list(None)
```

#### 3. Update Default Queries to Exclude Deleted:
```python
async def find_many(self, query: Dict[str, Any], ...) -> List[Dict[str, Any]]:
    # Add deleted_at: None to all queries by default
    query = {**query, "deleted_at": None}
    cursor = self._collection.find(query)
    # ... rest of implementation
```

#### 4. Add Indexes for Soft Delete:
```javascript
// Add to all collections with soft delete
db.projects.createIndex({ deleted_at: 1 });
db.scenes.createIndex({ deleted_at: 1 });
db.clips.createIndex({ deleted_at: 1 });
```

#### 5. Collections Requiring Soft Delete:
- ✅ `projects` - High priority (contains scenes/clips)
- ✅ `scenes` - High priority (contains clips)
- ✅ `clips` - High priority (contains generated content)
- ✅ `characters` - Medium priority (referenced by clips)
- ✅ `style_templates` - Medium priority (referenced by clips)
- ⚠️ `comfyui_servers` - Low priority (system config)
- ⚠️ `generation_batches` - Low priority (historical data)

---

## 6. Data Model Relationships

### Collection Catalog (14+ Collections)

#### **Core Content Collections (3)**

##### 1. **projects**
```
Primary Key: id (UUID string)
Indexes: id (unique), created_at
Relationships:
  ├─→ scenes (1:many) via project_id
  ├─→ characters (1:many) via project_id
  ├─→ style_templates (1:many) via project_id
  └─→ generation_batches (1:many) via project_id

Fields:
  - id, name, description
  - music_file_path, music_duration
  - created_at, updated_at
```

##### 2. **scenes**
```
Primary Key: id (UUID string)
Indexes: id (unique), (project_id, order), parent_scene_id, is_alternate
Relationships:
  ├─← projects (many:1) via project_id [FK]
  ├─→ clips (1:many) via scene_id
  └─→ scenes (1:many) via parent_scene_id [SELF-REF: alternates]

Fields:
  - id, project_id [FK], name, description, lyrics
  - order, parent_scene_id, is_alternate
  - created_at, updated_at
```

##### 3. **clips**
```
Primary Key: id (UUID string)
Indexes: id (unique), (scene_id, order), (scene_id, timeline_position)
Relationships:
  ├─← scenes (many:1) via scene_id [FK]
  ├─← characters (many:1) via character_id [FK, optional]
  └─→ generated_images/videos [EMBEDDED arrays]

Fields:
  - id, scene_id [FK], name, lyrics
  - length, timeline_position, order
  - image_prompt, video_prompt
  - generated_images, generated_videos [EMBEDDED]
  - selected_image_id, selected_video_id
  - character_id [FK], versions, active_version
  - created_at, updated_at
```

#### **Asset Collections (2)**

##### 4. **characters**
```
Primary Key: id (UUID string)
Indexes: id (unique), (project_id, name)
Relationships:
  ├─← projects (many:1) via project_id [FK]
  └─→ clips (1:many) [REVERSE REF]

Fields:
  - id, project_id [FK], name, description
  - reference_images, lora, trigger_words, style_notes
  - created_at, updated_at
```

##### 5. **style_templates**
```
Primary Key: id (UUID string)
Indexes: id (unique), (project_id, name)
Relationships:
  └─← projects (many:1) via project_id [FK, optional]

Fields:
  - id, project_id [FK, optional], name, description
  - prompt_template, negative_prompt_template
  - default_params, use_count, is_global
  - created_at, updated_at
```

#### **Generation Infrastructure (3)**

##### 6. **comfyui_servers**
```
Primary Key: id (UUID string)
Indexes: id (unique), url (unique)
Relationships:
  └─→ active_backend_models (1:many) [REVERSE REF]

Fields:
  - id, name, url, server_type
  - api_key, endpoint_id, is_active
  - created_at
```

##### 7. **generation_batches**
```
Primary Key: id (UUID string)
Indexes: id (unique), (project_id, created_at)
Relationships:
  └─← projects (many:1) via project_id [FK]

Fields:
  - id, project_id [FK], status
  - total, completed, failed
  - results [EMBEDDED array with clip_id refs]
  - started_at, updated_at
```

##### 8. **generation_pool** ⚠️
```
Primary Key: id (UUID string)
Indexes: ⚠️ NONE DEFINED
Relationships:
  └─← clips (many:1) via clip_id [FK]

Fields:
  - id, clip_id [FK], prompt, negative_prompt
  - model, generation_type, params, status
  - server_id, created_at
```

#### **Model Management Collections (6)**

##### 9. **active_backend_models** ⚠️
```
Primary Key: id (string)
Indexes: ⚠️ NONE DEFINED
Relationships:
  ├─← backends (many:1) via backend_id [FK]
  └─← civitai_models (many:1) via civitai_model_id [FK, optional]

Fields:
  - id, backend_id [FK], backend_name, backend_url
  - model_id, model_name, model_type, model_path, model_size
  - civitai_model_id [FK], civitai_model_name, civitai_match_quality
  - is_active, last_seen, first_seen, model_metadata
```

##### 10. **backends** ⚠️
```
Primary Key: id (string)
Indexes: ⚠️ NONE DEFINED
Relationships:
  └─→ active_backend_models (1:many) [REVERSE REF]

Fields:
  - id, name, url
  - is_online, last_check, model_count
```

##### 11. **model_sync_status** ⚠️
```
Primary Key: model_id (string)
Indexes: ⚠️ NONE DEFINED
Relationships:
  └─← civitai_models (many:1) via civitai_model_id [FK, optional]

Fields:
  - model_id, civitai_model_id [FK], sync_status
  - last_sync_attempt, last_sync_success, sync_error
```

##### 12. **civitai_models** ⚠️
```
Primary Key: id (inferred)
Indexes: ⚠️ NONE DEFINED
Relationships:
  └─→ active_backend_models (1:many) [REVERSE REF]

Fields:
  - id, name, baseModel, type, description
  - [additional Civitai metadata]
```

##### 13. **model_profiles** ⚠️
```
Primary Key: id (inferred)
Indexes: ⚠️ NONE DEFINED

Fields:
  - name, linked_base_models
  - [additional profile metadata]
```

##### 14. **database_models** ⚠️
```
Primary Key: id (inferred)
Indexes: ⚠️ NONE DEFINED

Fields: [model data from imports]
```

### Data Access Patterns:

#### ✅ **Via Repositories:**
- `projects`, `scenes`, `clips`, `comfyui_servers`
- Clean abstraction through repository pattern

#### ⚠️ **Direct Database Access:**
Many services bypass repositories:
```python
# project_service.py
await db.characters.insert_one(character_data)
await db.style_templates.find(query).to_list(None)

# generation_service.py
await db.comfyui_servers.find_one({"id": server_id})
await db.generation_batches.find().sort("created_at", -1)

# gallery_manager.py
await db.clips.update_one({"id": clip_id}, ...)

# export_service.py
await db.projects.find_one({"id": project_id})
await db.scenes.find({"project_id": project_id})
```

### Referential Integrity:

⚠️ **No Foreign Key Constraints:**
- MongoDB doesn't enforce foreign keys
- Application-level integrity only
- Risk of orphaned records if deletes cascade incorrectly

⚠️ **No Cascade Delete Logic:**
- Deleting a project doesn't auto-delete scenes/clips
- Deleting a scene doesn't auto-delete clips
- Must be handled in application code

⚠️ **Denormalized Data:**
- `clips` contains `project_id` (denormalized from scene)
- `active_backend_models` duplicates backend name/URL
- Risk of data inconsistency if parent updates

---

## 7. Recommendations

### High Priority:

1. **Implement Soft Deletes**
   - Add `deleted_at` to core collections (projects, scenes, clips, characters, style_templates)
   - Update BaseRepository with soft delete methods
   - Add indexes on `deleted_at`

2. **Add Missing Indexes**
   - `generation_pool`, `active_backend_models`, `backends`, `model_sync_status`
   - Performance critical collections

3. **Standardize Data Access**
   - Create repositories for `characters`, `style_templates`, `generation_pool`
   - Remove direct `db.collection` access from services
   - Enforce repository pattern throughout

4. **Add Repository Error Handling**
   - Wrap MongoDB exceptions in try-catch
   - Raise domain-specific errors
   - Log database errors appropriately

### Medium Priority:

5. **Transaction Support**
   - Use MongoDB transactions for multi-collection operations
   - Ensure atomicity for cascade operations

6. **Database Migration System**
   - Track schema versions
   - Handle data migrations
   - Support rollbacks

7. **Expand Index Coverage**
   - Add text indexes for search (project name, scene description)
   - Add compound indexes for common query patterns
   - Monitor slow queries and add indexes accordingly

### Low Priority:

8. **Connection Pool Configuration**
   - Make pool size configurable
   - Add metrics/monitoring

9. **Cascade Delete Implementation**
   - Add service methods for safe cascade deletes
   - Prevent orphaned records

10. **Denormalization Strategy**
    - Document which fields are denormalized
    - Add update triggers to maintain consistency

---

## 8. Summary

### Architecture Score: **7/10**

**What Works:**
- ✅ Solid connection management
- ✅ Consistent repository pattern for core collections
- ✅ Good error handling hierarchy
- ✅ Adequate indexes for primary use cases

**What Needs Work:**
- ⚠️ Soft delete implementation required
- ⚠️ Mixed data access patterns (repository vs direct)
- ⚠️ Missing indexes on model management collections
- ⚠️ No transaction support
- ⚠️ Repository layer lacks error handling

**Risk Assessment:**
- **Data Loss Risk:** HIGH (no soft deletes)
- **Performance Risk:** MEDIUM (missing indexes on some collections)
- **Maintainability Risk:** MEDIUM (inconsistent patterns)
- **Scalability Risk:** LOW (good foundation)

**Action Items:**
1. Implement soft deletes (1-2 days)
2. Add missing indexes (1 day)
3. Create missing repositories (2-3 days)
4. Add repository error handling (1 day)
5. Implement transactions for critical operations (2-3 days)

**Total Estimated Effort:** 7-11 days
