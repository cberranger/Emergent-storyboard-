# FaceFusion API Complete Catalog

## Table of Contents
1. [Available Operations (Processors)](#available-operations-processors)
2. [Face Swapping Parameters](#face-swapping-parameters)
3. [Face Enhancement Parameters](#face-enhancement-parameters)
4. [Face Editing Parameters](#face-editing-parameters)
5. [Age Modification Parameters](#age-modification-parameters)
6. [Expression Restoration Parameters](#expression-restoration-parameters)
7. [Deep Swapper Parameters](#deep-swapper-parameters)
8. [Frame Enhancement Parameters](#frame-enhancement-parameters)
9. [Frame Colorizer Parameters](#frame-colorizer-parameters)
10. [Lip Syncer Parameters](#lip-syncer-parameters)
11. [Face Debugger Parameters](#face-debugger-parameters)
12. [Face Detection & Selection](#face-detection--selection)
13. [Face Masking Parameters](#face-masking-parameters)
14. [Output Settings](#output-settings)
15. [Processing Modes](#processing-modes)
16. [Execution Settings](#execution-settings)

---

## Available Operations (Processors)

FaceFusion supports multiple processors that can be combined:

```python
available_processors = [
    'age_modifier',
    'deep_swapper',
    'expression_restorer',
    'face_debugger',
    'face_editor',
    'face_enhancer',
    'face_swapper',
    'frame_colorizer',
    'frame_enhancer',
    'lip_syncer'
]
```

**CLI Parameter:** `--processors`  
**Default:** `['face_swapper']`  
**Multiple:** Yes (space-separated list)

---

## Face Swapping Parameters

### Models Available

```python
face_swapper_models = [
    'blendswap_256',
    'ghost_1_256',
    'ghost_2_256',
    'ghost_3_256',
    'hififace_unofficial_256',
    'hyperswap_1a_256',
    'hyperswap_1b_256',
    'hyperswap_1c_256',
    'inswapper_128',
    'inswapper_128_fp16',
    'simswap_256',
    'simswap_unofficial_512',
    'uniface_256'
]
```

### Model-Specific Pixel Boost Options

```python
face_swapper_pixel_boost = {
    'blendswap_256': ['256x256', '384x384', '512x512', '768x768', '1024x1024'],
    'ghost_1_256': ['256x256', '512x512', '768x768', '1024x1024'],
    'ghost_2_256': ['256x256', '512x512', '768x768', '1024x1024'],
    'ghost_3_256': ['256x256', '512x512', '768x768', '1024x1024'],
    'hififace_unofficial_256': ['256x256', '512x512', '768x768', '1024x1024'],
    'hyperswap_1a_256': ['256x256', '512x512', '768x768', '1024x1024'],
    'hyperswap_1b_256': ['256x256', '512x512', '768x768', '1024x1024'],
    'hyperswap_1c_256': ['256x256', '512x512', '768x768', '1024x1024'],
    'inswapper_128': ['128x128', '256x256', '384x384', '512x512', '768x768', '1024x1024'],
    'inswapper_128_fp16': ['128x128', '256x256', '384x384', '512x512', '768x768', '1024x1024'],
    'simswap_256': ['256x256', '512x512', '768x768', '1024x1024'],
    'simswap_unofficial_512': ['512x512', '768x768', '1024x1024'],
    'uniface_256': ['256x256', '512x512', '768x768', '1024x1024']
}
```

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `--face-swapper-model` | choice | See models above | `hyperswap_1a_256` | Face swapping model |
| `--face-swapper-pixel-boost` | choice | Model-dependent | Model's first option | Processing resolution |
| `--face-swapper-weight` | float | 0.0 - 1.0 (step 0.05) | 0.5 | Blend weight (select models only) |

### Source/Target File Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-s, --source-paths` | file paths | Image file(s) containing source face(s) |
| `-t, --target-path` | file path | Image or video file to apply face swap to |
| `-o, --output-path` | file path | Output file location |

**Supported Source Formats:** `.bmp`, `.jpeg`, `.png`, `.tiff`, `.webp`  
**Supported Target Formats:** Images + `.avi`, `.m4v`, `.mkv`, `.mp4`, `.mov`, `.webm`, `.wmv`

---

## Face Enhancement Parameters

### Models Available

```python
face_enhancer_models = [
    'codeformer',
    'gfpgan_1.2',
    'gfpgan_1.3',
    'gfpgan_1.4',
    'gpen_bfr_256',
    'gpen_bfr_512',
    'gpen_bfr_1024',
    'gpen_bfr_2048',
    'restoreformer_plus_plus'
]
```

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `--face-enhancer-model` | choice | See models above | `gfpgan_1.4` | Enhancement model |
| `--face-enhancer-blend` | int | 0 - 100 | 80 | Blend factor (percentage) |
| `--face-enhancer-weight` | float | 0.0 - 1.0 (step 0.05) | 0.5 | Enhancement weight (codeformer only) |

---

## Face Editing Parameters

### Models Available

```python
face_editor_models = ['live_portrait']
```

### All Face Editor Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `--face-editor-model` | choice | `live_portrait` | `live_portrait` | Face editor model |
| `--face-editor-eyebrow-direction` | float | -1.0 to 1.0 (0.05) | 0.0 | Eyebrow movement |
| `--face-editor-eye-gaze-horizontal` | float | -1.0 to 1.0 (0.05) | 0.0 | Horizontal eye direction |
| `--face-editor-eye-gaze-vertical` | float | -1.0 to 1.0 (0.05) | 0.0 | Vertical eye direction |
| `--face-editor-eye-open-ratio` | float | -1.0 to 1.0 (0.05) | 0.0 | Eye openness |
| `--face-editor-lip-open-ratio` | float | -1.0 to 1.0 (0.05) | 0.0 | Lip openness |
| `--face-editor-mouth-grim` | float | -1.0 to 1.0 (0.05) | 0.0 | Grim expression |
| `--face-editor-mouth-pout` | float | -1.0 to 1.0 (0.05) | 0.0 | Pout expression |
| `--face-editor-mouth-purse` | float | -1.0 to 1.0 (0.05) | 0.0 | Purse expression |
| `--face-editor-mouth-smile` | float | -1.0 to 1.0 (0.05) | 0.0 | Smile intensity |
| `--face-editor-mouth-position-horizontal` | float | -1.0 to 1.0 (0.05) | 0.0 | Horizontal mouth position |
| `--face-editor-mouth-position-vertical` | float | -1.0 to 1.0 (0.05) | 0.0 | Vertical mouth position |
| `--face-editor-head-pitch` | float | -1.0 to 1.0 (0.05) | 0.0 | Head tilt up/down |
| `--face-editor-head-yaw` | float | -1.0 to 1.0 (0.05) | 0.0 | Head turn left/right |
| `--face-editor-head-roll` | float | -1.0 to 1.0 (0.05) | 0.0 | Head roll rotation |

---

## Age Modification Parameters

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `--age-modifier-model` | choice | `styleganex_age` | `styleganex_age` | Age modification model |
| `--age-modifier-direction` | int | -100 to 100 | 0 | Age direction (negative=younger, positive=older) |

---

## Expression Restoration Parameters

### Parameters

| Parameter | Type | Options | Default | Description |
|-----------|------|---------|---------|-------------|
| `--expression-restorer-model` | choice | `live_portrait` | `live_portrait` | Expression model |
| `--expression-restorer-factor` | int | 0 - 100 | 100 | Restoration factor |
| `--expression-restorer-areas` | list | `upper-face`, `lower-face` | All | Face areas |

---

## Deep Swapper Parameters

### Models Available (170+ Celebrity Models)

**Example Models:**
- `druuzil/adam_levine_320`
- `druuzil/angelina_jolie_384`
- `iperov/emma_watson_224`
- `mats/billie_eilish_224`
- `rumateus/margot_robbie_224`
- `custom/*` (user models in `.assets/models/custom`)

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `--deep-swapper-model` | choice | 170+ models | First available | Pre-trained model |
| `--deep-swapper-morph` | int | 0 - 100 | 50 | Morph intensity |

---

## Frame Enhancement Parameters

### Models Available

```python
frame_enhancer_models = [
    'clear_reality_x4', 'lsdir_x4', 'nomos8k_sc_x4',
    'real_esrgan_x2', 'real_esrgan_x2_fp16',
    'real_esrgan_x4', 'real_esrgan_x4_fp16',
    'real_esrgan_x8', 'real_esrgan_x8_fp16',
    'real_hatgan_x4', 'real_web_photo_x4', 'realistic_rescaler_x4',
    'remacri_x4', 'siax_x4', 'span_kendata_x4', 'swin2_sr_x4',
    'ultra_sharp_x4', 'ultra_sharp_2_x4'
]
```

### Parameters

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| `--frame-enhancer-model` | choice | See above | First available |
| `--frame-enhancer-blend` | int | 0 - 100 | 80 |

---

## Frame Colorizer Parameters

### Parameters

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--frame-colorizer-model` | choice | `ddcolor`, `ddcolor_artistic`, `deoldify`, `deoldify_artistic`, `deoldify_stable` | First |
| `--frame-colorizer-blend` | int | 0 - 100 | 80 |
| `--frame-colorizer-size` | choice | `192x192`, `256x256`, `384x384`, `512x512` | Model-dependent |

---

## Lip Syncer Parameters

### Parameters

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--lip-syncer-model` | choice | `edtalk_256`, `wav2lip_96`, `wav2lip_gan_96` | First |
| `--lip-syncer-weight` | float | 0.0 - 1.0 (0.05) | 0.5 |

---

## Face Debugger Parameters

### Parameters

| Parameter | Type | Options |
|-----------|------|---------|
| `--face-debugger-items` | list | `bounding-box`, `face-landmark-5`, `face-landmark-5/68`, `face-landmark-68`, `face-landmark-68/5`, `face-mask` |

---

## Face Detection & Selection

### Face Detector

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--face-detector-model` | choice | `many`, `retinaface`, `scrfd`, `yolo_face`, `yunet` | `yolo_face` |
| `--face-detector-size` | choice | Model-dependent | Largest |
| `--face-detector-angles` | list[int] | 0, 90, 180, 270 | [0] |
| `--face-detector-score` | float | 0.0 - 1.0 (0.05) | 0.5 |

### Face Landmarker

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--face-landmarker-model` | choice | `many`, `2dfan4`, `peppa_wutz` | `2dfan4` |
| `--face-landmarker-score` | float | 0.0 - 1.0 (0.05) | 0.5 |

### Face Selector

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--face-selector-mode` | choice | `many`, `one`, `reference` | `reference` |
| `--face-selector-order` | choice | `left-right`, `right-left`, `top-bottom`, `bottom-top`, `small-large`, `large-small`, `best-worst`, `worst-best` | `large-small` |
| `--face-selector-gender` | choice | `female`, `male` | None |
| `--face-selector-race` | choice | `white`, `black`, `latino`, `asian`, `indian`, `arabic` | None |
| `--face-selector-age-start` | int | 0 - 100 | None |
| `--face-selector-age-end` | int | 0 - 100 | None |
| `--reference-face-position` | int | 0+ | 0 |
| `--reference-face-distance` | float | 0.0 - 1.0 (0.05) | 0.3 |
| `--reference-frame-number` | int | 0+ | 0 |

---

## Face Masking Parameters

### Mask Models

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--face-occluder-model` | choice | `many`, `xseg_1`, `xseg_2`, `xseg_3` | `xseg_1` |
| `--face-parser-model` | choice | `bisenet_resnet_18`, `bisenet_resnet_34` | `bisenet_resnet_34` |

### Mask Configuration

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--face-mask-types` | list | `box`, `occlusion`, `area`, `region` | [`box`] |
| `--face-mask-areas` | list | `upper-face`, `lower-face`, `mouth` | All |
| `--face-mask-regions` | list | `skin`, `left-eyebrow`, `right-eyebrow`, `left-eye`, `right-eye`, `glasses`, `nose`, `mouth`, `upper-lip`, `lower-lip` | All |
| `--face-mask-blur` | float | 0.0 - 1.0 (0.05) | 0.3 |
| `--face-mask-padding` | list[int] | [0-100, 0-100, 0-100, 0-100] | [0, 0, 0, 0] |

---

## Output Settings

### Image Output

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| `--output-image-quality` | int | 0 - 100 | 80 |
| `--output-image-scale` | float | 0.25 - 8.0 (0.25) | 1.0 |

### Audio Output

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--output-audio-encoder` | choice | `flac`, `aac`, `libmp3lame`, `libopus`, `libvorbis`, `pcm_s16le`, `pcm_s32le` | System-dependent |
| `--output-audio-quality` | int | 0 - 100 | 80 |
| `--output-audio-volume` | int | 0 - 100 | 100 |

### Video Output

| Parameter | Type | Options/Range | Default |
|-----------|------|---------------|--------|
| `--output-video-encoder` | choice | `libx264`, `libx264rgb`, `libx265`, `libvpx-vp9`, `h264_nvenc`, `hevc_nvenc`, `h264_amf`, `hevc_amf`, `h264_qsv`, `hevc_qsv`, `h264_videotoolbox`, `hevc_videotoolbox`, `rawvideo` | System-dependent |
| `--output-video-preset` | choice | `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow` | `veryfast` |
| `--output-video-quality` | int | 0 - 100 | 80 |
| `--output-video-scale` | float | 0.25 - 8.0 (0.25) | 1.0 |
| `--output-video-fps` | float | Any positive | Auto-detect |

### Frame Extraction

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--trim-frame-start` | int | 0+ | None |
| `--trim-frame-end` | int | 0+ | None |
| `--temp-frame-format` | choice | `bmp`, `jpeg`, `png`, `tiff` | `png` |
| `--keep-temp` | flag | - | False |

---

## Processing Modes

### UI Workflows

```python
ui_workflows = ['instant_runner', 'job_runner', 'job_manager']
```

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--ui-workflow` | choice | See above | `instant_runner` |

### Instant Runner Mode

**Description:** Immediate processing when Start clicked

**Actions:**
- Start: Begin processing
- Stop: Halt processing
- Clear: Clear output

### Job Runner Mode

**Actions:**
```python
job_runner_actions = [
    'job-run',        # Run single queued job
    'job-run-all',    # Run all queued jobs
    'job-retry',      # Retry single failed job
    'job-retry-all'   # Retry all failed jobs
]
```

### Job Manager Mode

**Actions:**
```python
job_manager_actions = [
    'job-create',      # Create new job
    'job-submit',      # Submit job to queue
    'job-delete',      # Delete job
    'job-add-step',    # Add processing step
    'job-remix-step',  # Remix existing step
    'job-insert-step', # Insert step at position
    'job-remove-step'  # Remove step
]
```

### Job Statuses

```python
job_statuses = ['drafted', 'queued', 'completed', 'failed']
```

---

## Execution Settings

### Execution Providers

```python
execution_providers = [
    'cuda',      # NVIDIA CUDA
    'tensorrt',  # NVIDIA TensorRT
    'directml',  # DirectML (Windows)
    'rocm',      # AMD ROCm
    'migraphx',  # AMD MIGraphX
    'openvino',  # Intel OpenVINO
    'coreml',    # Apple CoreML
    'cpu'        # CPU fallback
]
```

### Execution Parameters

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| `--execution-providers` | list | See above | Auto-detect |
| `--execution-device-ids` | list[int] | Device IDs | [0] |
| `--execution-thread-count` | int | 1 - 32 | Auto |

### Memory Management

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--video-memory-strategy` | choice | `strict`, `moderate`, `tolerant` | `moderate` |
| `--system-memory-limit` | int | 0 - 128 (GB, 0=unlimited) | 0 |

---

## Path Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--config-path` | file path | `facefusion.ini` | Config file |
| `--temp-path` | directory | System temp | Temporary files |
| `--jobs-path` | directory | `.jobs` | Job storage |
| `--source-pattern` | pattern | None | Source file pattern |
| `--target-pattern` | pattern | None | Target file pattern |
| `--output-pattern` | pattern | None | Output file pattern |

---

## Download Configuration

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--download-providers` | list | `github`, `huggingface` | Both |
| `--download-scope` | choice | `lite`, `full` | `lite` |

---

## Voice Extraction

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--voice-extractor-model` | choice | `kim_vocal_1`, `kim_vocal_2`, `uvr_mdxnet` | `kim_vocal_2` |

---

## Logging & Debugging

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--log-level` | choice | `error`, `warn`, `info`, `debug` | `info` |
| `--halt-on-error` | flag | - | False |

---

## Benchmark Settings

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--benchmark-mode` | choice | `warm`, `cold` | `warm` |
| `--benchmark-resolutions` | list | `240p`, `360p`, `540p`, `720p`, `1080p`, `1440p`, `2160p` | First |
| `--benchmark-cycle-count` | int | 1 - 10 | 1 |

---

## UI Configuration

| Parameter | Type | Options | Default |
|-----------|------|---------|--------|
| `--open-browser` | flag | - | False |
| `--ui-layouts` | list | `default`, `benchmark`, `jobs`, `webcam` | `default` |

### Preview Options

```python
preview_modes = ['default', 'frame-by-frame', 'face-by-face']
preview_resolutions = ['512x512', '768x768', '1024x1024']
```

### Webcam Options

```python
webcam_modes = ['inline', 'udp', 'v4l2']
webcam_resolutions = ['320x240', '640x480', '800x600', '1024x768', '1280x720', '1280x960', '1920x1080']
```

---

## Complete Parameter Reference Summary

### Core Processing Chain

1. **Input**: `--source-paths`, `--target-path`
2. **Detection**: `--face-detector-*` parameters
3. **Landmarking**: `--face-landmarker-*` parameters
4. **Selection**: `--face-selector-*` parameters
5. **Masking**: `--face-mask-*` parameters
6. **Processing**: `--processors` with processor-specific parameters
7. **Output**: `--output-*` parameters

### State Management

All parameters stored in `state_manager` during session:  
- Job-level keys: Persist across steps (paths, execution settings)
- Step-level keys: Per-step configuration (processor settings, face detection)

### API Surface

**Gradio Interface:**
- Launch: `python facefusion.py run`
- Default port: 7860
- Access: http://localhost:7860

**Command Line:**
```bash
python facefusion.py headless-run \
  --source-paths source.jpg \
  --target-path target.mp4 \
  --output-path output.mp4 \
  --processors face_swapper face_enhancer \
  --face-swapper-model inswapper_128 \
  --face-enhancer-model gfpgan_1.4
```

**Job Queue API:**
```bash
# Create job
python facefusion.py job-create --job-id my_job

# Add step
python facefusion.py job-add-step --job-id my_job [...parameters...]

# Submit to queue
python facefusion.py job-submit --job-id my_job

# Run job
python facefusion.py job-run --job-id my_job
```
