# Inference Configuration Scripts

This directory contains scripts for managing the `inference_configurations` MongoDB collection.

## Scripts Overview

### 1. populate_inference_configurations.py
**Purpose**: Populate the database with standard quality and speed presets for all active models.

**Requirements**: 
- MongoDB must be running
- Environment variables must be set (MONGO_URL, DB_NAME)
- Active models must exist in `database_models` collection

**Usage**:
```bash
cd backend
python scripts/populate_inference_configurations.py
```

**What it does**:
- Connects to MongoDB
- Creates indexes on `inference_configurations` collection
- Fetches all models with `is_active: true`
- Determines base model type (sdxl, flux_dev, pony, etc.)
- Creates quality and speed configurations for each model
- Skips configurations that already exist

**Output**:
```
Connected to database successfully
Creating indexes...
Indexes created
Fetching active models...
Found 24 active models

Processing: Juggernaut XL (base_model: sdxl)
  - quality: created
  - speed: created

============================================================
Population complete!
  Created: 48 configurations
  Skipped: 0 (already exist or no presets)
============================================================
```

---

### 2. validate_inference_config_structure.py
**Purpose**: Validate the repository structure without requiring database connection.

**Requirements**: None (no database needed)

**Usage**:
```bash
python backend/scripts/validate_inference_config_structure.py
```

**What it checks**:
- Repository module imports correctly
- Inherits from BaseRepository
- All required methods are present
- INFERENCE_PRESETS are properly defined for all base models
- Documentation file exists
- Repository is properly exported

**Output**:
```
[PASS] InferenceConfigurationRepository imported successfully
[PASS] InferenceConfigurationRepository extends BaseRepository
[PASS] All 5 required methods present
[PASS] populate_inference_configurations.py exists
[PASS] INFERENCE_CONFIGURATION_STANDARDS.md exists
[PASS] Found presets for 9 base models
[PASS] InferenceConfigurationRepository exported from repositories package

All validation checks passed!
```

---

### 3. test_inference_config_repo.py
**Purpose**: Test repository operations with a live database connection.

**Requirements**:
- MongoDB must be running
- Environment variables must be set

**Usage**:
```bash
cd backend
python scripts/test_inference_config_repo.py
```

**What it tests**:
- Database connection
- Index creation
- Creating configurations
- Finding by model_id
- Finding by model_id and type
- Finding by base_model
- Finding by base_model and type
- Deleting configurations

**Output**:
```
Test 1: Creating indexes...
[PASS] Indexes created successfully

Test 2: Creating test configuration...
[PASS] Created configuration: abc-123

Test 3: Finding by model_id...
[PASS] Found 1 configuration(s) for model_id

...

All tests passed!
```

---

### 4. test_dto_import.py
**Purpose**: Verify DTO imports are working correctly.

**Requirements**: None

**Usage**:
```bash
python backend/scripts/test_dto_import.py
```

**Output**:
```
Testing DTO imports...
[PASS] All inference configuration DTOs imported successfully

All DTO tests passed!
```

---

## Quick Start

To set up inference configurations for the first time:

1. **Validate structure** (optional but recommended):
   ```bash
   python backend/scripts/validate_inference_config_structure.py
   ```

2. **Ensure MongoDB is running**:
   ```bash
   # Windows
   net start MongoDB
   
   # macOS
   brew services start mongodb-community
   
   # Linux
   sudo systemctl start mongod
   ```

3. **Populate the database**:
   ```bash
   cd backend
   python scripts/populate_inference_configurations.py
   ```

4. **Test the repository** (optional):
   ```bash
   python scripts/test_inference_config_repo.py
   ```

## Troubleshooting

### "Failed to connect to database"
- Ensure MongoDB is running
- Check `backend/.env` for correct `MONGO_URL` and `DB_NAME`
- Verify network connectivity to MongoDB server

### "No active models found"
- The `database_models` collection must have documents with `is_active: true`
- Run model sync/import scripts first
- Check MongoDB to verify models exist:
  ```javascript
  use storycanvas
  db.database_models.find({ is_active: true }).count()
  ```

### "Configuration already exists"
- This is expected behavior if you run the script multiple times
- The script skips existing configurations to prevent duplicates
- To recreate, manually delete from MongoDB:
  ```javascript
  db.inference_configurations.deleteMany({})
  ```

### Import Errors
- Ensure you're in the `backend` directory or parent directory
- Check that all dependencies are installed:
  ```bash
  pip install -r backend/requirements.txt
  ```

## Additional Resources

- **Documentation**: `docs/INFERENCE_CONFIGURATION_STANDARDS.md`
- **Implementation Summary**: `docs/IMPLEMENTATION_SUMMARY_INFERENCE_CONFIG.md`
- **Repository Code**: `backend/repositories/inference_configuration_repository.py`
- **DTOs**: `backend/dtos/inference_config_dtos.py`
