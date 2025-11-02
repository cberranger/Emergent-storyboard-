# Database Scripts

This directory contains scripts for database initialization, migration, and management.

## Available Scripts

### 1. `init_db.py` - Database Initialization

**Purpose:** Initialize MongoDB database with all required collections and indexes.

**Features:**
- Verifies all required collections exist
- Automatically creates missing collections
- Creates proper indexes for query optimization
- Safe to run multiple times (idempotent)

**Required Collections:**
- Core: `projects`, `scenes`, `clips`, `characters`, `style_templates`
- Generation: `comfyui_servers`, `generation_batches`
- FaceFusion: `facefusion_jobs`, `facefusion_presets`
- Models: `database_models`, `inference_configurations`, `civitai_models`
- Auth: `users`

**Usage:**
```bash
# From backend directory
python scripts/init_db.py

# Or from repo root
python backend/scripts/init_db.py
```

**Configuration:**
- Uses `MONGO_URL` environment variable (default: `mongodb://192.168.1.10:27017`)
- Uses `DB_NAME` environment variable (default: `storyboard`)
- Falls back to `backend/.env` if environment variables not set

**Output Example:**
```
============================================================
Database Initialization
============================================================
MongoDB URL: mongodb://192.168.1.10:27017
Database: storyboard

✓ MongoDB connection successful

Verifying collections...
✓ Collection exists: projects
✓ Collection exists: scenes
✓ Collection created: facefusion_jobs
...

Creating indexes...
Projects...
  Index ensured on projects: [('id', 1)] (id_1)
  Index ensured on projects: [('created_at', -1)] (created_at_-1)
...

============================================================
✓ Database initialization complete
============================================================
```

---

### 2. `migrate_characters_facefusion.py` - FaceFusion Migration

**Purpose:** Add FaceFusion fields to existing character documents.

**What it does:**
- Finds all characters without FaceFusion fields
- Adds `facefusion_processing_history` (empty array)
- Adds `facefusion_preferred_settings` (null)
- Adds `facefusion_output_gallery` (empty gallery structure)
- Verifies migration success

**Usage:**
```bash
# From backend directory
python scripts/migrate_characters_facefusion.py

# Or from repo root
python backend/scripts/migrate_characters_facefusion.py
```

**Configuration:**
- Same as `init_db.py` (uses `MONGO_URL` and `DB_NAME`)

**Output Example:**
```
============================================================
Character FaceFusion Migration
============================================================
MongoDB URL: mongodb://192.168.1.10:27017
Database: storyboard

✓ MongoDB connection successful

Starting migration...
Found 15 character(s) that need FaceFusion fields
✓ Successfully migrated 15 character(s)
✓ All characters now have FaceFusion fields

Migration Verification:
  Total characters: 15
  With processing_history: 15
  With preferred_settings: 15
  With output_gallery: 15
  ✓ All characters have complete FaceFusion schema

============================================================
✓ Migration complete
============================================================
```

**Safe to run:**
- Multiple times (only updates characters without fields)
- On production (no data loss, only adds fields)
- Before or after `init_db.py`

---

### 3. `init_inference_configurations.py` - Inference Configuration Population

**Purpose:** Populate inference configurations for active models.

**See:** `README_INFERENCE_CONFIG.md` for detailed documentation.

---

## Automatic Database Initialization

The application automatically validates and creates collections on startup via `backend/database.py`:

**DatabaseManager Features:**
- ✅ Automatic collection validation on first connection
- ✅ Creates missing collections with proper indexes
- ✅ Logs warnings for missing collections
- ✅ One-time validation per connection (cached)

**How it works:**
```python
# In DatabaseManager.connect()
if not self._collections_validated:
    await self._validate_collections()
    self._collections_validated = True
```

**When to run scripts manually:**
1. **Initial Setup:** Run `init_db.py` to pre-create all collections
2. **Migration:** Run `migrate_characters_facefusion.py` after updating to FaceFusion support
3. **Verification:** Run `init_db.py` to verify database state
4. **Index Updates:** Run `init_db.py` after schema changes

---

## Collection Schemas

See `docs/DATABASE_SCHEMA.md` for complete schema documentation including:
- Field definitions
- Index specifications
- FaceFusion integration details
- Migration notes

---

## Troubleshooting

### Connection Refused
**Error:** `Cannot connect to MongoDB at mongodb://...`

**Solutions:**
1. Verify MongoDB is running: `mongo --eval "db.version()"`
2. Check network connectivity: `ping 192.168.1.10`
3. Verify port: `telnet 192.168.1.10 27017`
4. Check firewall settings
5. Verify `MONGO_URL` in `.env` or environment

### Wrong Database
**Error:** Collections created in wrong database

**Solutions:**
1. Check `DB_NAME` environment variable
2. Verify `backend/.env` has correct `DB_NAME`
3. Drop wrong database: `mongo storyboard --eval "db.dropDatabase()"`
4. Re-run init script

### Permission Denied
**Error:** `PyMongoError: not authorized`

**Solutions:**
1. Verify MongoDB authentication is disabled for local dev
2. Or add credentials to `MONGO_URL`: `mongodb://user:pass@host:port`
3. Check MongoDB user permissions

### Index Already Exists
**Warning:** `Failed index on ... index already exists with different options`

**Solutions:**
1. Usually safe to ignore (indexes exist with correct settings)
2. To rebuild: Drop and recreate collection (development only!)
3. Or manually drop index: `db.collection.dropIndex("index_name")`

---

## Best Practices

### Development
1. Run `init_db.py` once when setting up local environment
2. Run migrations when schema changes
3. Use automatic validation during development (enabled by default)

### Production
1. Run `init_db.py` as part of deployment pipeline
2. Run migrations before deploying new code
3. Test migrations on staging first
4. Keep automatic validation enabled for safety

### Testing
1. Use separate test database: `DB_NAME=storyboard_test`
2. Run `init_db.py` in test setup
3. Clean database between test runs
4. Mock database for unit tests

---

## Related Documentation

- **Database Schema:** `docs/DATABASE_SCHEMA.md`
- **Database Audit:** `backend/DATABASE_AUDIT.md`
- **FaceFusion Integration:** `docs/FACEFUSION_INTEGRATION.md`
- **Inference Configurations:** `README_INFERENCE_CONFIG.md`
