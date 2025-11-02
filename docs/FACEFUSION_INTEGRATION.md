# FaceFusion Integration Guide

Comprehensive documentation for FaceFusion integration in StoryCanvas with complete parameter reference, workflow guides, best practices, code examples, and troubleshooting for 192.168.1.10:9002 server.

## Table of Contents
- [Overview](#overview)
- [Complete Parameter Reference](#complete-parameter-reference)
- [API Endpoints](#api-endpoints)
- [Code Examples](#code-examples)
- [Workflow Guides](#workflow-guides)
- [Parameter Interactions & Best Practices](#parameter-interactions--best-practices)
- [Server Configuration](#server-configuration)
- [Troubleshooting 192.168.1.10:9002](#troubleshooting-19216811099002)

## Overview

FaceFusion provides face manipulation capabilities:
- **Face Enhancement**: GFPGAN, CodeFormer, RestoreFormer++
- **Age Adjustment**: Morph faces to any age (0-100 years)
- **Face Swapping**: High-quality face replacement

### Architecture
```
Frontend → Backend → FaceFusionClient → FaceFusion Server (192.168.1.10:9002)
```

## Complete Parameter Reference

### Face Enhancement Parameters

#### `face_enhancer_model` (string)

| Model | Speed | Quality | Best For | GPU Time |
|-------|-------|---------|----------|----------|
| `gfpgan_1.4` | Fast | Good | General use | 1-2s |
| `codeformer` | Medium | Very Good | Detail preservation | 2-3s |
| `restoreformer_plus_plus` | Slow | Excellent | Professional | 3-5s |

**Default:** `"gfpgan_1.4"`

#### `face_enhancer_blend` (float)

**Range:** 0.0 - 1.0
- `0.0`: No enhancement
- `0.3-0.5`: Subtle
- `0.6-0.8`: Standard
- `0.9-1.0`: Maximum

**Default:** `1.0`

### Age Adjustment Parameters

#### `face_editor_age` (int)

**Range:** 0 - 100

**Categories:**
- 0-12: Child
- 13-19: Teen
- 20-35: Young adult
- 36-55: Middle-aged
- 56-70: Senior
- 71-100: Elderly

**Quality by Jump:**
| Jump | Quality | Action |
|------|---------|--------|
| ±5 | Excellent | Direct |
| ±15 | Very Good | Direct |
| ±30 | Good | Consider intermediate |
| ±40+ | Fair | Use intermediates |

**Default:** `25`

#### `face_editor_blend` (float)

**Range:** 0.0 - 1.0
**Default:** `1.0`
**Tip:** Use 0.5-0.7 for large age jumps

### Face Swap Parameters

#### `face_swapper_model` (string)
- `"inswapper_128"` (default)
- `"inswapper_256"` (if available)

#### `source_face_path` (string)
- Clearly visible face
- Front-facing ±30°
- Min 256x256px
- JPG, PNG, WebP

#### `target_image_path` (string)
- Contains face(s)
- Any resolution
- Preserves lighting/pose

## API Endpoints

### 1. Face Enhancement

`POST /api/facefusion/enhance-face`

**Request:**
```json
{
  "character_id": "char-123",
  "image_url": "http://localhost:8000/uploads/face.jpg",
  "enhancement_model": "gfpgan_1.4",
  "facefusion_url": "http://192.168.1.10:9002"
}
```

**Response (200):**
```json
{
  "character_id": "char-123",
  "original_image": "http://localhost:8000/uploads/face.jpg",
  "enhanced_image": "http://localhost:8000/uploads/enhanced_123.png",
  "enhancement_model": "gfpgan_1.4",
  "message": "Face enhanced successfully"
}
```

**Errors:** 404 (not found), 503 (server offline), 500 (processing failed)

### 2. Age Adjustment

`POST /api/facefusion/adjust-face-age`

**Request:**
```json
{
  "character_id": "char-123",
  "image_url": "http://localhost:8000/uploads/face.jpg",
  "target_age": 45,
  "facefusion_url": "http://192.168.1.10:9002"
}
```

**Response (200):**
```json
{
  "character_id": "char-123",
  "original_image": "http://localhost:8000/uploads/face.jpg",
  "adjusted_image": "http://localhost:8000/uploads/aged_123.png",
  "target_age": 45,
  "message": "Face age adjusted successfully"
}
```

**Errors:** 400 (invalid age), 404 (not found), 503 (server offline)

### 3. Face Swap

`POST /api/facefusion/swap-face`

**Request:**
```json
{
  "character_id": "char-123",
  "source_face_url": "http://localhost:8000/uploads/face.jpg",
  "target_image_url": "http://localhost:8000/uploads/body.jpg",
  "facefusion_url": "http://192.168.1.10:9002"
}
```

**Response (200):**
```json
{
  "character_id": "char-123",
  "source_face": "http://localhost:8000/uploads/face.jpg",
  "target_image": "http://localhost:8000/uploads/body.jpg",
  "swapped_image": "http://localhost:8000/uploads/swapped_123.png",
  "message": "Face swapped successfully"
}
```

### 4. Server Status

`GET /api/facefusion/status?facefusion_url=http://192.168.1.10:9002`

**Response (200):**
```json
{
  "facefusion_url": "http://192.168.1.10:9002",
  "is_online": true,
  "status": "online",
  "message": "FaceFusion server is accessible"
}
```

### 5. Batch Processing

`POST /api/facefusion/batch-process`

**Request:**
```json
{
  "character_id": "char-123",
  "operations": [
    {"type": "enhance", "image_url": "...", "enhancement_model": "gfpgan_1.4"},
    {"type": "age_adjust", "image_url": "...", "target_age": 50}
  ],
  "facefusion_url": "http://192.168.1.10:9002"
}
```

**Response (200):**
```json
{
  "character_id": "char-123",
  "total_operations": 2,
  "successful_operations": 2,
  "failed_operations": 0,
  "results": [
    {"operation": {...}, "success": true, "result_url": "..."},
    {"operation": {...}, "success": true, "result_url": "..."}
  ]
}
```

## Code Examples

### Frontend JavaScript

#### Enhancement
```javascript
import { faceFusionService } from '@/services';

const enhanceFace = async (character, imageUrl) => {
  const result = await faceFusionService.enhanceFace({
    character_id: character.id,
    image_url: imageUrl,
    enhancement_model: 'gfpgan_1.4',
    facefusion_url: 'http://192.168.1.10:9002'
  });
  return result.enhanced_image;
};
```

#### Age Adjustment
```javascript
const adjustAge = async (character, imageUrl, targetAge) => {
  const result = await faceFusionService.adjustFaceAge({
    character_id: character.id,
    image_url: imageUrl,
    target_age: targetAge,
    facefusion_url: 'http://192.168.1.10:9002'
  });
  return result.adjusted_image;
};
```

#### Face Swap
```javascript
const swapFace = async (character, sourceFaceUrl, targetImageUrl) => {
  const result = await faceFusionService.swapFace({
    character_id: character.id,
    source_face_url: sourceFaceUrl,
    target_image_url: targetImageUrl,
    facefusion_url: 'http://192.168.1.10:9002'
  });
  return result.swapped_image;
};
```

#### Batch Processing
```javascript
const batchProcess = async (character, operations) => {
  const result = await faceFusionService.batchProcess({
    character_id: character.id,
    operations: operations,
    facefusion_url: 'http://192.168.1.10:9002'
  });
  
  console.log(`Completed ${result.successful_operations}/${result.total_operations}`);
  result.results.forEach((r, i) => {
    if (r.success) {
      console.log(`Op ${i}: ${r.result_url}`);
    } else {
      console.error(`Op ${i} failed: ${r.error}`);
    }
  });
  
  return result;
};
```

#### Status Check
```javascript
const checkStatus = async (serverUrl = 'http://192.168.1.10:9002') => {
  const status = await faceFusionService.getStatus({
    facefusion_url: serverUrl
  });
  return status.is_online;
};
```

### Backend Python

#### Client Usage
```python
from backend.server import FaceFusionClient

client = FaceFusionClient("http://192.168.1.10:9002")

# Check connection
is_online = await client.check_connection()

# Enhance
enhanced = await client.enhance_face(
    image_path="/path/to/image.jpg",
    enhancement_model="gfpgan_1.4"
)

# Age adjust
aged = await client.adjust_face_age(
    image_path="/path/to/image.jpg",
    target_age=45
)

# Swap
swapped = await client.swap_face(
    source_face_path="/path/to/face.jpg",
    target_image_path="/path/to/body.jpg"
)
```

#### Custom Workflow
```python
from fastapi import APIRouter, HTTPException

@router.post("/custom/enhance-and-age")
async def enhance_and_age(
    image_url: str,
    target_age: int,
    facefusion_url: str = "http://192.168.1.10:9002"
):
    client = FaceFusionClient(facefusion_url)
    
    if not await client.check_connection():
        raise HTTPException(503, "Server unavailable")
    
    image_path = convert_url_to_path(image_url)
    
    # Enhance first
    enhanced = await client.enhance_face(image_path, "codeformer")
    if not enhanced:
        raise HTTPException(500, "Enhancement failed")
    
    # Then age adjust
    aged = await client.adjust_face_age(enhanced, target_age)
    if not aged:
        raise HTTPException(500, "Age adjustment failed")
    
    return {
        "original": image_url,
        "enhanced": path_to_url(enhanced),
        "final": path_to_url(aged)
    }
```

## Workflow Guides

### Workflow 1: Face Enhancement

**Goal:** Improve AI-generated face quality

**Steps:**
1. Select image (512x512+ px, front-facing)
2. Choose model (GFPGAN=fast, CodeFormer=quality, RestoreFormer++=max)
3. Process
4. Compare original vs enhanced
5. Apply result

**Best Practices:**
- ✅ Keep original backup
- ✅ Test multiple models
- ✅ Enhance once only
- ❌ Don't enhance high-quality images
- ❌ Don't use on stylized art

**Code:**
```javascript
const result = await faceFusionService.enhanceFace({
  character_id: char.id,
  image_url: faceUrl,
  enhancement_model: 'gfpgan_1.4',
  facefusion_url: 'http://192.168.1.10:9002'
});
```

### Workflow 2: Age Progression

**Goal:** Create age variants for character timeline

**Steps:**
1. Establish base age (e.g., 25)
2. Define key ages (childhood=12, teen=16, adult=25, middle=45, senior=65)
3. Process each age variant
4. View side-by-side for consistency
5. Add intermediates if needed

**Age Jump Guidelines:**
- ±5 years: Direct processing, excellent quality
- ±15 years: Direct processing, very good quality
- ±30 years: Consider intermediate, good quality
- ±40+ years: Use intermediates (e.g., 25→45→65)

**Best Practices:**
- ✅ Use same base for all ages
- ✅ Smaller jumps = better quality
- ✅ Enhance after aging
- ❌ Don't de-age below 10
- ❌ Don't make extreme jumps

**Code:**
```javascript
const aged45 = await faceFusionService.adjustFaceAge({
  character_id: char.id,
  image_url: baseUrl,
  target_age: 45,
  facefusion_url: 'http://192.168.1.10:9002'
});
```

### Workflow 3: Face Swapping

**Goal:** Apply character face to different poses/scenes

**Steps:**
1. Prepare source (character face, front-facing, 512x512+)
2. Select target (desired pose, match angle, similar lighting)
3. Perform swap
4. Evaluate (lighting, blending, proportions, skin tone)
5. Optional: Enhance result

**Angle Matching Quality:**
- Front→Front: ★★★★★ Perfect
- Front→15°: ★★★★☆ Very good
- Front→30°: ★★★☆☆ Acceptable
- Front→45°: ★★☆☆☆ Marginal
- Front→90°: ★☆☆☆☆ Poor, avoid

**Best Practices:**
- ✅ Match angles closely
- ✅ Match lighting direction
- ✅ High-res sources
- ✅ Enhance source first
- ❌ Don't use profile angles

**Code:**
```javascript
const swapped = await faceFusionService.swapFace({
  character_id: char.id,
  source_face_url: faceUrl,
  target_image_url: poseUrl,
  facefusion_url: 'http://192.168.1.10:9002'
});

// Optional: Enhance result
const enhanced = await faceFusionService.enhanceFace({
  character_id: char.id,
  image_url: swapped.swapped_image,
  enhancement_model: 'codeformer',
  facefusion_url: 'http://192.168.1.10:9002'
});
```

### Workflow 4: Batch Processing

**Goal:** Process multiple operations efficiently

**Example 1: Model Comparison**
```javascript
const operations = [
  { type: 'enhance', image_url: img, enhancement_model: 'gfpgan_1.4' },
  { type: 'enhance', image_url: img, enhancement_model: 'codeformer' },
  { type: 'enhance', image_url: img, enhancement_model: 'restoreformer_plus_plus' }
];

const result = await faceFusionService.batchProcess({
  character_id: char.id,
  operations,
  facefusion_url: 'http://192.168.1.10:9002'
});
```

**Example 2: Age Gallery**
```javascript
const ages = [15, 25, 35, 45, 55, 65];
const operations = ages.map(age => ({
  type: 'age_adjust',
  image_url: baseImage,
  target_age: age
}));

const result = await faceFusionService.batchProcess({
  character_id: char.id,
  operations,
  facefusion_url: 'http://192.168.1.10:9002'
});
// Creates 6 age variants
```

**Best Practices:**
- ✅ Start small (3-5 ops)
- ✅ Monitor first operation
- ✅ Log all results
- ✅ Handle failures
- ❌ Don't assume all succeed

## Parameter Interactions & Best Practices

### Enhancement Model Selection

**For AI-Generated Faces:**
- GFPGAN: Moderate quality boost, fast
- CodeFormer: Identity preservation, balanced
- RestoreFormer++: Overkill, slow

**For Photo Restoration:**
- CodeFormer: Balanced results
- RestoreFormer++: Professional output
- GFPGAN: May over-smooth

**For Batch Operations:**
- GFPGAN: Speed priority
- Avoid RestoreFormer++ (too slow)

### Chaining Operations

**Recommended Order:**
1. Enhance source → 2. Process (age/swap) → 3. Optional enhance result

**Example: Enhance + Age**
```javascript
const enhanced = await enhanceFace(char, originalUrl);
const aged = await adjustAge(char, enhanced, 50);
const final = await enhanceFace(char, aged); // optional
```

**Example: Enhance + Swap**
```javascript
const enhancedFace = await enhanceFace(char, faceUrl);
const swapped = await swapFace(char, enhancedFace, targetUrl);
const final = await enhanceFace(char, swapped);
```

### Blend Value Guidelines

**Enhancement:**
- 0.5-0.6: Preserve style/character
- 0.7-0.8: Standard improvement
- 0.9-1.0: Maximum restoration

**Age Adjustment:**
- 0.5-0.6: Subtle, preserve identity (large jumps)
- 0.7-0.8: Noticeable aging
- 0.9-1.0: Dramatic (small jumps)

### Performance vs Quality

**For Speed:**
- GFPGAN over CodeFormer
- InSwapper 128 over 256
- Reduce resolution
- Batch operations

**For Quality:**
- CodeFormer/RestoreFormer++
- Higher resolution (1024px+)
- Full resolution processing
- Chain operations

## Server Configuration

### Default (localhost)
```javascript
facefusion_url: 'http://localhost:7870'
```

### Network Server (192.168.1.10:9002)
```javascript
facefusion_url: 'http://192.168.1.10:9002'
```

### Frontend Configuration
```javascript
const [facefusionUrl, setFacefusionUrl] = useState('http://192.168.1.10:9002');

const result = await faceFusionService.enhanceFace({
  character_id: char.id,
  image_url: imageUrl,
  enhancement_model: 'gfpgan_1.4',
  facefusion_url: facefusionUrl
});
```

### Backend Configuration
```python
client = FaceFusionClient("http://192.168.1.10:9002")

# Or use environment variable
import os
facefusion_url = os.getenv('FACEFUSION_URL', 'http://localhost:7870')
client = FaceFusionClient(facefusion_url)
```

### Environment Variables

**Backend (.env):**
```bash
FACEFUSION_URL=http://192.168.1.10:9002
```

**Frontend (.env):**
```bash
REACT_APP_FACEFUSION_URL=http://192.168.1.10:9002
```

## Troubleshooting 192.168.1.10:9002

### Issue 1: Connection Refused

**Symptoms:**
- Status returns `is_online: false`
- "Connection refused" error
- 503 errors on operations

**Diagnosis:**
```bash
# Test connectivity
ping 192.168.1.10

# Test port
curl http://192.168.1.10:9002/api/v1/status

# Check from backend server
curl http://192.168.1.10:9002/api/v1/status
```

**Solutions:**

1. **Verify FaceFusion is running:**
```bash
# SSH to 192.168.1.10
ssh user@192.168.1.10

# Check if process is running
ps aux | grep facefusion

# Check port
netstat -tln | grep 9002
```

2. **Start FaceFusion server:**
```bash
# On 192.168.1.10
cd /path/to/facefusion
python facefusion.py run --web-server-host 0.0.0.0 --web-server-port 9002
```

3. **Check firewall:**
```bash
# Allow port 9002
sudo ufw allow 9002/tcp

# Or for specific source
sudo ufw allow from 192.168.1.0/24 to any port 9002
```

4. **Verify network connectivity:**
- Ensure both servers on same network
- Check router/switch configuration
- Test with telnet: `telnet 192.168.1.10 9002`

### Issue 2: Timeout Errors

**Symptoms:**
- Operations timeout after 30-60s
- "Request timeout" errors
- Partial processing

**Solutions:**

1. **Increase timeout in backend:**
```python
class FaceFusionClient:
    async def enhance_face(self, image_path: str, enhancement_model: str):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
            # ... rest of code
```

2. **Check server load:**
```bash
# On 192.168.1.10
top
nvidia-smi  # Check GPU usage
```

3. **Reduce image size:**
```javascript
// Resize before processing
const resized = await resizeImage(imageUrl, 1024, 1024);
const result = await faceFusionService.enhanceFace({...});
```

### Issue 3: Processing Fails

**Symptoms:**
- 500 errors
- "Processing failed" messages
- Returns null/empty result

**Solutions:**

1. **Check FaceFusion logs:**
```bash
# On 192.168.1.10
tail -f /path/to/facefusion/logs/facefusion.log
```

2. **Verify image format:**
```python
# Ensure supported format
from PIL import Image
img = Image.open(image_path)
if img.format not in ['JPEG', 'PNG', 'WebP']:
    img = img.convert('RGB')
    img.save(new_path, 'PNG')
```

3. **Check GPU memory:**
```bash
nvidia-smi

# If out of memory, restart FaceFusion
pkill -f facefusion
python facefusion.py run --web-server-host 0.0.0.0 --web-server-port 9002
```

### Issue 4: Slow Performance

**Symptoms:**
- Operations take >30s
- High CPU usage
- System lag

**Solutions:**

1. **Verify GPU acceleration:**
```bash
# Check CUDA
nvcc --version

# Check PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

2. **Use faster models:**
```javascript
// Use GFPGAN instead of RestoreFormer++
enhancement_model: 'gfpgan_1.4'  // Fast
// instead of
enhancement_model: 'restoreformer_plus_plus'  // Slow
```

3. **Reduce resolution:**
```javascript
// Process at lower resolution
const MAX_SIZE = 1024;
if (imageWidth > MAX_SIZE || imageHeight > MAX_SIZE) {
  resizedImage = await resizeImage(image, MAX_SIZE);
}
```

### Issue 5: Network Configuration

**Symptoms:**
- Works from backend, fails from frontend
- CORS errors
- Mixed content warnings

**Solutions:**

1. **CORS configuration (FaceFusion server):**
```python
# Add CORS headers
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Use backend proxy (recommended):**
- Frontend → Backend → FaceFusion
- Avoids CORS issues
- Better security
- Current implementation already uses this pattern

3. **Mixed content (HTTPS/HTTP):**
- If frontend is HTTPS, FaceFusion must be HTTPS
- Or proxy through backend (already implemented)

### Diagnostic Checklist

**Quick Health Check:**
```bash
# 1. Ping server
ping 192.168.1.10

# 2. Check port
telnet 192.168.1.10 9002

# 3. Test API
curl http://192.168.1.10:9002/api/v1/status

# 4. Check from StoryCanvas backend
curl http://192.168.1.10:9002/api/v1/status

# 5. Test enhancement endpoint
curl -X POST http://192.168.1.10:9002/api/v1/enhance-face \
  -H "Content-Type: application/json" \
  -d '{"source_path": "/path/test.jpg", "face_enhancer_model": "gfpgan_1.4"}'
```

**Common Error Messages:**

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | Server not running | Start FaceFusion server |
| Timeout | Slow processing or network | Increase timeout, check GPU |
| 404 | Image not found | Verify image path/URL |
| 503 | Server unavailable | Check FaceFusion status |
| 500 | Processing error | Check logs, verify image format |
| CORS error | Cross-origin request | Use backend proxy |

### Performance Benchmarks (192.168.1.10:9002)

**Expected Processing Times (RTX 3090, 512x512 image):**
- GFPGAN enhancement: 1-2s
- CodeFormer enhancement: 2-3s
- RestoreFormer++ enhancement: 3-5s
- Age adjustment: 2-3s
- Face swap: 3-4s

**If experiencing slower times:**
- Check GPU utilization: `nvidia-smi`
- Check network latency: `ping 192.168.1.10`
- Monitor server load: `top` or `htop`
- Review FaceFusion logs for bottlenecks

### Emergency Recovery

**If FaceFusion becomes unresponsive:**

1. **Restart FaceFusion:**
```bash
ssh user@192.168.1.10
pkill -f facefusion
cd /path/to/facefusion
python facefusion.py run --web-server-host 0.0.0.0 --web-server-port 9002
```

2. **Clear GPU memory:**
```bash
# Kill any stuck processes
nvidia-smi
# Find PID of stuck process
kill -9 <PID>
```

3. **Reboot server (last resort):**
```bash
sudo reboot
```

### Monitoring & Logging

**Enable detailed logging:**
```python
# In backend/server.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Log all FaceFusion requests
logging.info(f"FaceFusion request: {operation} to {facefusion_url}")
```

**Monitor FaceFusion health:**
```javascript
// Frontend: Periodic status check
setInterval(async () => {
  const status = await faceFusionService.getStatus({
    facefusion_url: 'http://192.168.1.10:9002'
  });
  console.log('FaceFusion status:', status.is_online);
}, 30000); // Every 30 seconds
```

---

## Summary

This comprehensive guide covers all aspects of FaceFusion integration:

- **Complete parameter reference** for all operations with recommendations
- **API endpoints** with full request/response examples
- **Code examples** for frontend and backend implementations
- **Workflow guides** for each operation type with best practices
- **Parameter interactions** and optimization strategies
- **Server configuration** for 192.168.1.10:9002 deployment
- **Troubleshooting** section with diagnostic tools and solutions

For additional support, consult FaceFusion documentation or StoryCanvas development team.
