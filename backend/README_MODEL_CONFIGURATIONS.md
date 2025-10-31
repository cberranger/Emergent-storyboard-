# Model Configurations API

This document describes the model configurations feature that replaces the legacy model_profiles system.

## Overview

The model configurations system provides a flexible way to store and manage inference parameters for AI models. Configurations can be:
- **Model-specific**: Associated with a particular model ID
- **Base model type**: Global configurations for model families (e.g., SDXL, Flux Dev, Pony)

## Database Collection

**Collection Name**: `model_configurations`

**Schema**:
- `id` (string): Unique identifier
- `model_id` (string, optional): Specific model this config applies to (null for global configs)
- `base_model` (string): Base model type (sdxl, flux_dev, pony, etc.)
- `name` (string): Configuration name
- `description` (string, optional): Configuration description
- `is_default` (bool): Whether this is the default configuration
- `steps` (int): Number of inference steps
- `cfg_scale` (float): Classifier-free guidance scale
- `sampler` (string): Sampler name (euler, dpmpp_2m, etc.)
- `scheduler` (string): Scheduler type (normal, karras, simple)
- `clip_skip` (int): CLIP skip layers (-1 for none)
- `resolution_width` (int): Default width in pixels
- `resolution_height` (int): Default height in pixels
- `batch_size` (int): Batch size
- `seed` (int): Seed value (-1 for random)
- `additional_params` (object): Additional model-specific parameters
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

## API Endpoints

All endpoints are under `/api/v1/models/`

### Model-Specific Configurations

**Create configuration for a model**
```
POST /api/v1/models/{model_id}/configurations
```

**Get all configurations for a model**
```
GET /api/v1/models/{model_id}/configurations
```

**Get default configuration for a model**
```
GET /api/v1/models/{model_id}/configurations/default
```

### Base Model Type Configurations

**Create global configuration for a base model type**
```
POST /api/v1/models/configurations/base/{base_model_type}
```

**Get all global configurations for a base model type**
```
GET /api/v1/models/configurations/base/{base_model_type}
```

### Configuration Management

**Get specific configuration**
```
GET /api/v1/models/configurations/{config_id}
```

**Update configuration**
```
PUT /api/v1/models/configurations/{config_id}
```

**Delete configuration**
```
DELETE /api/v1/models/configurations/{config_id}
```

## Usage Examples

### Creating a Model Configuration

```javascript
const config = await modelService.createModelConfiguration('model_123', {
  base_model: 'sdxl',
  name: 'High Quality',
  description: 'High quality settings for SDXL',
  is_default: true,
  steps: 35,
  cfg_scale: 7.5,
  sampler: 'dpmpp_2m',
  scheduler: 'karras',
  clip_skip: -1,
  resolution_width: 1024,
  resolution_height: 1024,
  batch_size: 1,
  seed: -1,
  additional_params: { refiner_steps: 5 }
});
```

### Creating a Base Model Configuration

```javascript
const config = await modelService.createBaseModelConfiguration('flux_dev', {
  base_model: 'flux_dev',
  name: 'Flux Fast',
  description: 'Fast settings for Flux Dev',
  steps: 8,
  cfg_scale: 2.0,
  sampler: 'euler',
  scheduler: 'simple',
  resolution_width: 1024,
  resolution_height: 1024
});
```

### Fetching Configurations in Frontend

```javascript
// Get configurations for a specific model
const configs = await modelService.getModelConfigurations(modelId);

// Get global configurations for a base model type
const baseConfigs = await modelService.getBaseModelConfigurations('sdxl');

// Get default configuration for a model
const defaultConfig = await modelService.getDefaultConfiguration(modelId);
```

## Frontend Integration

The Model Library popup (`ModelCard.jsx`) automatically fetches and displays configurations:

1. When the details dialog opens, configurations are fetched
2. Configurations are displayed in the "Configuration Presets" tab
3. Each configuration shows:
   - Name and description
   - Base model type
   - Default badge (if applicable)
   - All parameter values
   - Additional parameters (if any)

## Backend Architecture

### Layers

1. **DTOs** (`dtos/inference_config_dtos.py`):
   - `ModelConfigurationDTO`: Full configuration data
   - `ModelConfigurationCreateDTO`: For creating configurations
   - `ModelConfigurationUpdateDTO`: For updating configurations

2. **Repository** (`repositories/inference_configuration_repository.py`):
   - `ModelConfigurationRepository`: Database operations
   - Indexes on `model_id`, `base_model`, and compound keys

3. **Service** (`services/model_config.py`):
   - `ModelConfigurationService`: Business logic
   - CRUD operations
   - Default configuration lookup

4. **Router** (`api/v1/models_router.py`):
   - REST endpoints
   - Request/response handling
   - Dependency injection

## Migration from model_presets

The new system replaces the embedded `configuration_presets` array in the `DatabaseModel` schema. Key differences:

1. **Separate collection**: Configurations are now in their own collection
2. **Base model support**: Can create global configurations for model types
3. **Better indexing**: Optimized for querying by model or base model type
4. **More fields**: Includes scheduler, clip_skip, and additional_params
5. **Default flag**: Can mark configurations as default

## Best Practices

1. **Always set base_model**: Required for fallback lookups
2. **Use is_default wisely**: Only one default per model/base model
3. **Document additional_params**: Use for model-specific requirements
4. **Keep descriptions clear**: Help users understand preset purposes
5. **Test resolution values**: Ensure they match model capabilities
