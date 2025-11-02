# FaceFusion API Catalog

This document catalogs all available FaceFusion API parameters and endpoints for integration with the Gradio Client API at `192.168.1.10:9002`.

## 🔌 Gradio Client Integration

FaceFusion exposes its functionality through a Gradio interface accessible via the `/api/predict` endpoint. The Gradio Client library provides programmatic access to all FaceFusion features.

### Connection Details
- **Host**: `192.168.1.10:9002`
- **Endpoint**: `/api/predict`
- **Protocol**: HTTP with multipart file uploads

## 📋 Complete Parameter Catalog

### 1. Face Swapping

**Endpoint**: `/api/predict` (fn_index varies by interface)

#### Core Parameters
- `source_face`: File upload (image/video containing face to extract)
- `target_media`: File upload (image/video to apply face to)
- `output_path`: String (output file path)

#### Face Selection
- `reference_face_position`: Integer (0-based index for multi-face detection)
- `reference_face_distance`: Float (0.0-1.0, similarity threshold)
- `source_face_index`: Integer (which face from source to use)
- `target_face_index`: Integer (which face in target to replace)

#### Face Masking
- `face_mask_types`: List[String] (`["box"]`, `["occlusion"]`, `["region"]`)
- `face_mask_blur`: Float (0.0-1.0, edge softness)
- `face_mask_padding`: Tuple[Int] (top, right, bottom, left padding in pixels)
- `face_mask_regions`: List[Polygon] (custom polygon regions for masking)
  - Format: `[[x1,y1], [x2,y2], [x3,y3], ...]` for each polygon

#### Face Detection
- `face_detector_model`: String (`"retinaface"`, `"yoloface"`, `"scrfd"`, `"yunet"`)
- `face_detector_size`: String (`"320x320"`, `"640x640"`, `"1280x1280"`)
- `face_detector_score`: Float (0.0-1.0, confidence threshold)
- `face_landmarker_model`: String (`"2dfan4"`, `"peppa_wutz"`)

#### Swapper Models
- `face_swapper_model`: String (`"inswapper_128"`, `"inswapper_128_fp16"`, `"simswap_256"`, `"simswap_512_unofficial"`, `"ghost_2_unet_2"`, `"uniface_256"`)
- `face_swapper_pixel_boost`: String (`"128"`, `"256"`, `"512"`, `"1024"`)

### 2. Face Enhancement

**Endpoint**: `/api/predict`

#### Enhancement Models
- `face_enhancer_model`: String
  - `"gfpgan_1.2"` - Older GFPGAN version
  - `"gfpgan_1.3"` - Standard GFPGAN
  - `"gfpgan_1.4"` - Latest GFPGAN (recommended)
  - `"gpen_bfr_256"` - GPEN 256 resolution
  - `"gpen_bfr_512"` - GPEN 512 resolution
  - `"gpen_bfr_1024"` - GPEN 1024 resolution
  - `"gpen_bfr_2048"` - GPEN 2048 resolution
  - `"restoreformer_plus_plus"` - RestoreFormer++
  - `"codeformer"` - CodeFormer model

#### Enhancement Control
- `face_enhancer_blend`: Float (0.0-1.0, blend factor between original and enhanced)
- `face_enhancer_iterations`: Integer (1-10, number of enhancement passes)

### 3. Face Editing

**Endpoint**: `/api/predict`

#### Age Modification
- `face_editor_age`: Integer (0-100, target age)
- `face_editor_age_direction`: String (`"younger"`, `"older"`, `"auto"`)

#### Expression Control
- `face_editor_eyebrow_direction`: String (`"up"`, `"down"`, `"neutral"`)
- `face_editor_eye_gaze`: String (`"left"`, `"right"`, `"up"`, `"down"`, `"center"`)
- `face_editor_eye_open_ratio`: Float (0.0-2.0, eye openness)
- `face_editor_lip_open_ratio`: Float (0.0-2.0, mouth openness)
- `face_editor_mouth_grim`: Float (-1.0-1.0, grimace/smile)
- `face_editor_mouth_pout`: Float (0.0-1.0, pout amount)
- `face_editor_mouth_purse`: Float (0.0-1.0, purse amount)
- `face_editor_mouth_smile`: Float (0.0-1.0, smile amount)
- `face_editor_mouth_position`: Float (-1.0-1.0, mouth vertical position)
- `face_editor_head_pitch`: Float (-30.0-30.0, head up/down angle)
- `face_editor_head_yaw`: Float (-30.0-30.0, head left/right angle)
- `face_editor_head_roll`: Float (-30.0-30.0, head tilt angle)

#### Feature Modification
- `face_editor_face_shape`: Float (0.0-1.0, face shape morphing)
- `face_editor_nose_length`: Float (0.0-2.0, nose length)
- `face_editor_nose_width`: Float (0.0-2.0, nose width)
- `face_editor_eye_distance`: Float (0.0-2.0, inter-eye distance)
- `face_editor_eye_size`: Float (0.0-2.0, eye size)
- `face_editor_lip_size`: Float (0.0-2.0, lip size)
- `face_editor_hair_style`: Integer (0-50, hair style ID)
- `face_editor_hair_color`: String (RGB hex code, e.g., `"#000000"`)

#### Editor Blending
- `face_editor_blend`: Float (0.0-1.0, blend factor)
- `face_editor_model`: String (`"live_portrait"`, `"face_editor_v1"`)

### 4. Video Processing

**Endpoint**: `/api/predict`

#### Frame Control
- `trim_frame_start`: Integer (starting frame number)
- `trim_frame_end`: Integer (ending frame number)
- `output_video_fps`: Float (frames per second, e.g., 24.0, 30.0, 60.0)
- `skip_audio`: Boolean (whether to exclude audio from output)
- `video_memory_strategy`: String (`"strict"`, `"moderate"`, `"tolerant"`)

#### Frame Extraction
- `extract_frames`: Boolean (extract individual frames)
- `extract_frame_quality`: Integer (1-100, JPEG quality)
- `extract_frame_format`: String (`"jpg"`, `"png"`, `"bmp"`)

#### Video Assembly
- `temp_frame_format`: String (`"jpg"`, `"png"`, `"bmp"`)
- `output_video_encoder`: String (`"libx264"`, `"libx265"`, `"libvpx-vp9"`, `"h264_nvenc"`, `"hevc_nvenc"`)
- `output_video_preset`: String (`"ultrafast"`, `"superfast"`, `"veryfast"`, `"faster"`, `"fast"`, `"medium"`, `"slow"`, `"slower"`, `"veryslow"`)
- `output_video_quality`: Integer (0-100, video quality)

### 5. Output Configuration

#### Image Output
- `output_image_quality`: Integer (1-100, JPEG quality)
- `output_image_resolution`: String (`"512x512"`, `"768x768"`, `"1024x1024"`, `"1920x1080"`, etc.)

#### Video Output
- `output_video_quality`: Integer (0-100, video quality)
- `output_video_resolution`: String (e.g., `"1920x1080"`, `"1280x720"`, `"3840x2160"`)

### 6. Processing Options

#### Performance
- `execution_device_id`: String (`"0"`, `"1"`, etc. for GPU selection)
- `execution_queue_count`: Integer (1-8, parallel execution threads)
- `execution_thread_count`: Integer (1-128, CPU threads)

#### Memory Management
- `face_detector_device`: String (`"cuda"`, `"cpu"`)
- `face_recognizer_device`: String (`"cuda"`, `"cpu"`)
- `face_enhancer_device`: String (`"cuda"`, `"cpu"`)

#### Temporary Files
- `keep_temp`: Boolean (keep temporary files)
- `temp_frame_format`: String (`"jpg"`, `"png"`, `"bmp"`)
- `temp_frame_quality`: Integer (1-100)

### 7. Job Queue Management

#### Job Submission
- `job_id`: String (optional job identifier for async processing)
- `priority`: Integer (1-10, job priority)
- `callback_url`: String (webhook URL for completion notification)

#### Job Status
- `status`: String (`"queued"`, `"processing"`, `"completed"`, `"failed"`)
- `progress`: Float (0.0-1.0, completion percentage)
- `estimated_time`: Integer (estimated seconds remaining)

## 🔄 Processing Workflows

### Synchronous Processing
Immediate processing with direct result return. Suitable for:
- Single image enhancement
- Quick face swaps
- Real-time preview generation

### Asynchronous Processing
Job-based processing with status polling. Required for:
- Video processing
- Batch operations
- Long-running enhancements
- Multi-step workflows

## 📊 Response Formats

### Success Response
```json
{
  "data": [
    {
      "name": "output.jpg",
      "data": "base64_encoded_data",
      "is_file": true,
      "orig_name": "output.jpg"
    }
  ],
  "duration": 2.45,
  "average_duration": 2.3
}
```

### Job Status Response
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "progress": 0.45,
  "estimated_time": 15,
  "result": null
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```

## 🎯 Common Parameter Combinations

### High-Quality Face Swap
```python
{
    "face_swapper_model": "inswapper_128",
    "face_detector_model": "scrfd",
    "face_detector_size": "640x640",
    "face_mask_types": ["occlusion"],
    "face_mask_blur": 0.3,
    "face_enhancer_model": "gfpgan_1.4",
    "face_enhancer_blend": 0.8
}
```

### Age Progression
```python
{
    "face_editor_age": 65,
    "face_editor_age_direction": "older",
    "face_editor_blend": 0.9,
    "face_enhancer_model": "codeformer",
    "face_enhancer_blend": 0.7
}
```

### Expression Control
```python
{
    "face_editor_mouth_smile": 0.8,
    "face_editor_eye_open_ratio": 1.2,
    "face_editor_head_pitch": 5.0,
    "face_editor_blend": 0.85
}
```

### Video Face Swap
```python
{
    "face_swapper_model": "inswapper_128",
    "trim_frame_start": 0,
    "trim_frame_end": 150,
    "output_video_fps": 30.0,
    "output_video_encoder": "libx264",
    "output_video_preset": "medium",
    "output_video_quality": 85
}
```

## 🔧 Integration Examples

### Gradio Client Usage
```python
from gradio_client import Client

client = Client("http://192.168.1.10:9002/")

# Face swap
result = client.predict(
    source_face="path/to/source.jpg",
    target_media="path/to/target.jpg",
    face_swapper_model="inswapper_128",
    fn_index=0  # Varies by interface
)

# Enhancement
result = client.predict(
    target_media="path/to/image.jpg",
    face_enhancer_model="gfpgan_1.4",
    face_enhancer_blend=0.8,
    fn_index=1
)
```

## 📝 Notes

- All file parameters support both local paths and HTTP URLs
- Multipart uploads handle files up to 100MB by default
- Video processing is always asynchronous for files >10 seconds
- Face indices are 0-based (first face is index 0)
- Polygon regions use normalized coordinates (0.0-1.0)
- Job IDs are UUIDs generated server-side if not provided
