# Inference Configuration Standards

## Overview

The `inference_configurations` collection provides standardized parameter presets for all active AI models in the system. This allows developers to quickly apply optimized settings for either **quality-focused** or **speed-focused** inference without manually tuning parameters for each model architecture.

## Schema Design

### Collection: `inference_configurations`

Each document in this collection represents a specific configuration preset for a model.

```javascript
{
  "id": "uuid",                          // Unique configuration ID
  "model_id": "string",                  // Model ID (indexed, references database_models.id)
  "base_model": "string",                // Base architecture type for secondary grouping
  "configuration_type": "quality|speed", // Configuration category (enum)
  "steps": 20,                           // Number of diffusion/inference steps
  "cfg_scale": 7.5,                      // Classifier-free guidance scale
  "sampler": "euler_a",                  // Sampling algorithm
  "scheduler": "normal",                 // Noise scheduler type
  "model_specific_params": {             // Additional architecture-specific parameters
    "width": 1024,
    "height": 1024,
    "clip_skip": -1,
    "guidance": 3.5,
    "video_fps": 24,
    "requires_vae": "filename.safetensors"
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Indexes

The collection has the following indexes for optimal query performance:

- **Single field index** on `model_id` - fast lookups by model
- **Single field index** on `base_model` - grouping by architecture
- **Compound unique index** on `(model_id, configuration_type)` - ensures one quality and one speed preset per model

## Base Model Types

The `base_model` field categorizes models by their underlying architecture:

| Base Model | Description | Example Models |
|------------|-------------|----------------|
| `sdxl` | Stable Diffusion XL | SDXL 1.0, Juggernaut XL, etc. |
| `flux_dev` | Flux.1 Development | Flux.1-dev |
| `flux_schnell` | Flux.1 Schnell (fast) | Flux.1-schnell |
| `flux_krea` | Flux with Krea enhancements | Flux-Krea |
| `pony` | Pony Diffusion | Pony Diffusion XL |
| `wan_2_1` | Wanx Animator v2.1 | Wanx 2.1 |
| `wan_2_2` | Wanx Animator v2.2 | Wanx 2.2 |
| `hidream` | HiDream | HiDream v1 |
| `sd_1_5` | Stable Diffusion 1.5 | SD 1.5, Realistic Vision, etc. |

## Configuration Types

### Quality Preset

**Purpose**: Maximum image/video quality with detailed outputs

**Characteristics**:
- Higher step counts (25-30 steps for most models)
- More sophisticated samplers (dpmpp_2m, karras scheduler)
- Higher CFG scales for stronger prompt adherence
- Larger output resolutions where applicable
- Longer video frame counts for animation models
- Better detail preservation and coherence

**Use Cases**:
- Final production renders
- High-quality promotional materials
- Detailed character close-ups
- Complex scenes requiring fine details
- Professional deliverables

**Trade-offs**:
- Slower generation time (2-4x longer than speed preset)
- Higher computational cost
- More VRAM usage

### Speed Preset

**Purpose**: Fast iteration and previewing with acceptable quality

**Characteristics**:
- Lower step counts (8-15 steps typically)
- Faster samplers (euler, euler_a)
- Slightly lower CFG scales
- Standard resolutions
- Reduced frame counts for video
- Lightning LoRAs where applicable

**Use Cases**:
- Rapid prototyping and concept exploration
- Draft generations for review
- Testing prompts and compositions
- Batch generation for selection
- Real-time or near-real-time applications

**Trade-offs**:
- Reduced fine detail quality
- May have minor artifacts
- Less precise prompt adherence
- Simpler compositions work best

## Usage Guidelines

### Querying Configurations

**By Model ID** (recommended for most use cases):
```python
# Get all configurations for a specific model
from repositories.inference_configuration_repository import InferenceConfigurationRepository

inference_repo = InferenceConfigurationRepository(db.inference_configurations)

# Get quality preset for a model
quality_config = await inference_repo.find_by_model_and_type(
    model_id="model-uuid-123",
    configuration_type="quality"
)

# Get speed preset for a model
speed_config = await inference_repo.find_by_model_and_type(
    model_id="model-uuid-123",
    configuration_type="speed"
)
```

**By Base Model** (for fallback or default presets):
```python
# Get all SDXL configurations (useful for new untested models)
sdxl_configs = await inference_repo.find_by_base_model(
    base_model="sdxl"
)

# Get default quality config for flux_dev models
default_flux_quality = await inference_repo.find_by_base_model_and_type(
    base_model="flux_dev",
    configuration_type="quality"
)
```

### Applying Configurations

When preparing a generation request, merge the configuration parameters with user overrides:

```python
# Load preset
config = await inference_repo.find_by_model_and_type(model_id, "quality")

# Base parameters
params = {
    "steps": config["steps"],
    "cfg_scale": config["cfg_scale"],
    "sampler": config["sampler"],
    "scheduler": config["scheduler"],
}

# Add model-specific parameters
params.update(config["model_specific_params"])

# Apply user overrides (if any)
if user_overrides:
    params.update(user_overrides)

# Send to ComfyUI workflow
workflow = build_workflow(prompt, params)
```

### When to Use Each Preset

| Scenario | Recommended Preset | Rationale |
|----------|-------------------|-----------|
| User clicks "Generate" (first time) | **Speed** | Fast feedback for iteration |
| User clicks "Regenerate with Quality" | **Quality** | Final output after prompt refinement |
| Batch generation for selection | **Speed** | Generate many options quickly |
| Final export for project | **Quality** | Best quality for deliverable |
| Real-time preview | **Speed** | Minimize wait time |
| Character reference creation | **Quality** | Consistency requires detail |
| Background/environment test | **Speed** | Composition matters more than detail |
| Production render | **Quality** | Professional output required |

## Model-Specific Parameters

Different architectures require unique parameters stored in `model_specific_params`:

### SDXL Models
```json
{
  "width": 1024,
  "height": 1024,
  "clip_skip": -1,
  "denoise": 1.0
}
```

### Flux Models
```json
{
  "width": 1024,
  "height": 1024,
  "guidance": 3.5,
  "max_shift": 1.15,
  "base_shift": 0.5
}
```

### Wanx 2.2 (Video)
```json
{
  "width": 768,
  "height": 768,
  "video_fps": 24,
  "video_frames": 25,
  "requires_vae": "wan2.2_vae.safetensors",
  "text_encoder": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
  "lightning_lora": "wan2.2_i2v_lightx2v_4steps_lora_v1"  // Speed preset only
}
```

### Pony Diffusion
```json
{
  "width": 1024,
  "height": 1024,
  "clip_skip": -2  // Pony requires clip_skip of -2
}
```

## Maintaining Configurations

### Adding New Models

When new models are added to the `database_models` collection with `is_active: true`, run the population script to create their configurations:

```bash
cd backend
python scripts/populate_inference_configurations.py
```

The script will:
1. Fetch all active models
2. Infer or extract their `base_model` type
3. Create quality and speed presets based on architecture
4. Skip models that already have configurations

### Updating Presets

To update a preset for all models of a base type:

1. Edit the preset in `populate_inference_configurations.py`
2. Manually update existing documents or clear the collection
3. Re-run the population script

**Example**: Update all SDXL speed presets to use 12 steps instead of 15:

```python
# In populate_inference_configurations.py
INFERENCE_PRESETS["sdxl"]["speed"]["steps"] = 12
```

Then in MongoDB:
```javascript
db.inference_configurations.deleteMany({ base_model: "sdxl", configuration_type: "speed" });
```

Finally, re-run the script.

### Custom Model Configurations

For specific models that need non-standard settings, directly insert or update configurations:

```python
custom_config = {
    "id": str(uuid.uuid4()),
    "model_id": "special-model-id",
    "base_model": "sdxl",
    "configuration_type": "quality",
    "steps": 40,  # Higher than standard
    "cfg_scale": 9.0,  # Custom value
    "sampler": "dpmpp_sde",
    "scheduler": "karras",
    "model_specific_params": {
        "width": 1152,  # Non-standard resolution
        "height": 896,
        "clip_skip": -2
    },
    "created_at": datetime.now(timezone.utc),
    "updated_at": datetime.now(timezone.utc)
}

await inference_repo.create(custom_config)
```

## Best Practices

### For Developers

1. **Always query by model_id first** - Most specific and accurate configuration
2. **Fallback to base_model** - If model-specific config is missing, use base model defaults
3. **Allow user overrides** - Configurations are starting points, not restrictions
4. **Cache configurations** - These rarely change during a session
5. **Validate parameters** - Check that required model-specific params are present before sending to ComfyUI

### For System Administrators

1. **Keep presets updated** - As models evolve, optimal settings may change
2. **Monitor generation times** - Adjust speed presets if too slow for UX requirements
3. **Test quality presets** - Ensure quality settings actually produce noticeably better results
4. **Document custom configs** - If a model needs special settings, note why in the database
5. **Regular cleanup** - Remove configurations for models that are no longer active

### For AI Model Curators

1. **Benchmark new models** - Test various step counts to find optimal speed/quality balance
2. **Research architecture** - Check model documentation for recommended settings
3. **Compare with existing** - If a model is similar to existing ones, start with those presets
4. **Validate video parameters** - Ensure VAE, text encoders, and frame counts are correct
5. **Tag appropriately** - Ensure `base_model` accurately reflects the architecture

## Troubleshooting

### Configuration Not Found

**Symptom**: Query returns `None` for an active model

**Solutions**:
1. Verify model is actually marked `is_active: true`
2. Check if `base_model` is properly set
3. Run population script to generate missing configs
4. Fallback to base_model presets temporarily

### Poor Generation Quality

**Symptom**: Quality preset produces subpar results

**Investigation**:
1. Check if model has specific requirements (VAE, text encoders)
2. Verify sampler/scheduler compatibility with the model
3. Compare with ComfyUI community recommendations
4. Test with different step counts to find optimal range
5. Ensure CFG scale is appropriate for the architecture

### Slow Speed Preset

**Symptom**: Speed preset is too slow for iterative workflows

**Solutions**:
1. Reduce steps further (minimum ~4-8 for most models)
2. Try faster samplers (euler, euler_a, dpm_fast)
3. Enable lightning LoRAs if available
4. Reduce resolution for initial previews
5. Consider SDXL Turbo or LCM models for real-time needs

### Missing Model-Specific Parameters

**Symptom**: Generation fails due to missing required parameters

**Solutions**:
1. Check ComfyUI logs for specific error
2. Add required parameters to `model_specific_params`
3. Reference official model card or documentation
4. Test with example workflows from model creator
5. Update population script with correct params

## Future Enhancements

Potential improvements to the configuration system:

1. **User-defined presets** - Allow users to save custom configuration profiles
2. **A/B testing** - Track which configurations produce the best user selections
3. **Dynamic optimization** - Adjust parameters based on generation success rates
4. **Hardware profiles** - Different presets for different GPU capabilities
5. **Workflow templates** - Store full ComfyUI workflow JSONs with configurations
6. **Version history** - Track changes to configurations over time
7. **Preset categories** - Beyond quality/speed: "creative", "photorealistic", "stylized", etc.

## Related Documentation

- **Database Schema**: See `backend/server.py` for model collection schema
- **Repository Pattern**: See `backend/repositories/base_repository.py`
- **Model Management**: See `backend/active_models_service.py`
- **ComfyUI Integration**: See `docs/COMFYUI_INTEGRATION.md` (if exists)

## Changelog

- **2024-01**: Initial implementation with quality/speed presets
- Support for 9 base model architectures
- Automatic population script for active models
- Indexed queries for performance
