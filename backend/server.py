from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import aiohttp
import json
import asyncio
from fastapi.staticfiles import StaticFiles
import shutil
import warnings

import sys
# Ensure 'backend' directory is on sys.path for absolute-style imports (services, repositories, database)
BACKEND_DIR = Path(__file__).parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import database manager
from database import db_manager, get_database

# Import active models service
from active_models_service import ActiveModelsService
from models import BackendModelInfo, BackendInfo, ModelType

# Import v1 API router
from api.v1 import api_v1_router

# Import standardized errors
from utils.errors import (
    ProjectNotFoundError, SceneNotFoundError, ClipNotFoundError,
    ServerNotFoundError, ValidationError, InvalidParameterError,
    ResourceNotFoundError, InsufficientStorageError, ServiceUnavailableError,
    ServerError, GenerationError, ConflictError
)

# For backward compatibility - global db reference
db = None  # Will be initialized during startup
active_models_service = None  # Will be initialized during startup

# Database dependency for endpoints
def get_database():
    """Get database connection, raising error if not available"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return db

# FaceFusion integration
class FaceFusionClient:
    def __init__(self, base_url: str = "http://localhost:7870"):
        self.base_url = base_url.rstrip('/')
    
    async def enhance_face(self, image_path: str, enhancement_model: str = "gfpgan_1.4") -> Optional[str]:
        """Enhance face quality using FaceFusion"""
        try:
            async with aiohttp.ClientSession() as session:
                # Create enhancement job
                job_data = {
                    "source_path": image_path,
                    "face_enhancer_model": enhancement_model,
                    "face_enhancer_blend": 1.0
                }
                
                async with session.post(f"{self.base_url}/api/v1/enhance-face", json=job_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("output_path")
        except Exception as e:
            logging.error(f"Error enhancing face with FaceFusion: {e}")
        return None
    
    async def adjust_face_age(self, image_path: str, target_age: int) -> Optional[str]:
        """Adjust face age using FaceFusion"""
        try:
            async with aiohttp.ClientSession() as session:
                job_data = {
                    "source_path": image_path,
                    "face_editor_age": target_age,
                    "face_editor_blend": 1.0
                }
                
                async with session.post(f"{self.base_url}/api/v1/adjust-face", json=job_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("output_path")
        except Exception as e:
            logging.error(f"Error adjusting face age with FaceFusion: {e}")
        return None
    
    async def swap_face(self, source_face_path: str, target_image_path: str) -> Optional[str]:
        """Swap face using FaceFusion"""
        try:
            async with aiohttp.ClientSession() as session:
                job_data = {
                    "source_face_path": source_face_path,
                    "target_image_path": target_image_path,
                    "face_swapper_model": "inswapper_128"
                }
                
                async with session.post(f"{self.base_url}/api/v1/swap-face", json=job_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("output_path")
        except Exception as e:
            logging.error(f"Error swapping face with FaceFusion: {e}")
        return None
    
    async def check_connection(self) -> bool:
        """Check if FaceFusion server is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/status") as response:
                    return response.status == 200
        except Exception:
            return False

# Create the main app without a prefix
app = FastAPI(
    title="StoryCanvas API",
    description=(
        "StoryCanvas API for AI-powered video production. "
        "\n\n**Note:** Legacy `/api` endpoints are deprecated and will be removed on 2025-06-01. "
        "All new integrations should use `/api/v1` endpoints. "
        "See [API Migration Guide](/api/v1/docs) for details."
    ),
    version="1.0.0"
)

# Create a router without prefix (will be added when mounting)
# All endpoints in this router are deprecated
api_router = APIRouter(
    deprecated=True,
    tags=["⚠️ DEPRECATED - Legacy API (Use /api/v1 instead)"]
)

# Deprecation configuration
LEGACY_API_SUNSET_DATE = "2025-06-01"
LEGACY_API_VERSION = "legacy"
CURRENT_API_VERSION = "v1"

# Middleware to add deprecation headers to legacy API endpoints
class DeprecationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add version header to all API responses
        if request.url.path.startswith("/api/"):
            if request.url.path.startswith("/api/v1/"):
                response.headers["X-API-Version"] = CURRENT_API_VERSION
            elif not request.url.path.startswith("/api/v"):
                # Legacy endpoint
                response.headers["X-API-Version"] = LEGACY_API_VERSION
                response.headers["Deprecated"] = "true"
                response.headers["Sunset"] = LEGACY_API_SUNSET_DATE
                response.headers["Link"] = '</api/v1>; rel="alternate"'
                
                # Log deprecation warning
                logging.warning(
                    f"DEPRECATED API CALL: {request.method} {request.url.path} - "
                    f"Migrate to /api/v1 before {LEGACY_API_SUNSET_DATE}"
                )
                
        return response

app.add_middleware(DeprecationMiddleware)

# Create uploads directory
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Pydantic Models
class ComfyUIServer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    server_type: str = "standard"  # "standard" or "runpod"
    api_key: Optional[str] = None  # For RunPod serverless
    endpoint_id: Optional[str] = None  # Extracted from RunPod URL
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ComfyUIServerCreate(BaseModel):
    name: str
    url: str
    server_type: str = "standard"
    api_key: Optional[str] = None

class Model(BaseModel):
    name: str
    type: str  # checkpoint, lora, vae, etc.

# Enhanced Model Management System
class CivitaiModelInfo(BaseModel):
    modelId: str
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[List[str]] = []
    trainedWords: Optional[List[str]] = []
    baseModel: Optional[str] = None
    baseModelType: Optional[str] = None
    modelVersions: Optional[List[Dict[str, Any]]] = []
    images: Optional[List[Dict[str, Any]]] = []
    # Additional fields for enhanced display
    allowDerivatives: Optional[bool] = None
    sfwOnly: Optional[bool] = None
    nsfw: Optional[bool] = None
    nsfwLevel: Optional[int] = None
    cosmetic: Optional[Dict[str, Any]] = None
    stats: Optional[Dict[str, Any]] = {}
    allowNoCredit: Optional[bool] = None
    allowCommercialUse: Optional[List[str]] = []
    availability: Optional[str] = None
    supportsGeneration: Optional[bool] = None
    downloadUrl: Optional[str] = None

class ModelConfigurationPreset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    model_id: Optional[str] = None  # Specific model this preset belongs to
    base_model: Optional[str] = None  # Base model type (e.g., "sdxl", "flux_dev", "pony")
    is_global: Optional[bool] = False  # If true, preset applies to all models of this base_model type
    cfg_scale: Optional[float] = 7.0
    steps: Optional[int] = 20
    sampler: Optional[str] = "euler"
    scheduler: Optional[str] = "normal"
    clip_skip: Optional[int] = -1
    resolution_width: Optional[int] = 512
    resolution_height: Optional[int] = 512
    batch_size: Optional[int] = 1
    seed: Optional[int] = -1
    additional_params: Optional[Dict[str, Any]] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DatabaseModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # checkpoint, lora, vae, etc.
    filename: Optional[str] = None
    filepath: Optional[str] = None
    hash: Optional[str] = None
    server_source: Optional[str] = None  # Server ID where this was discovered
    civitai_info: Optional[CivitaiModelInfo] = None
    configuration_presets: List[ModelConfigurationPreset] = []
    metadata: Optional[Dict[str, Any]] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_synced_at: Optional[datetime] = None

class DatabaseModelCreate(BaseModel):
    name: str
    type: str
    filename: Optional[str] = None
    filepath: Optional[str] = None
    hash: Optional[str] = None
    server_source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class DatabaseModelUpdate(BaseModel):
    name: Optional[str] = None
    filename: Optional[str] = None
    filepath: Optional[str] = None
    hash: Optional[str] = None
    civitai_info: Optional[CivitaiModelInfo] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class CivitaiLinkRequest(BaseModel):
    civitai_model_id: str

class CivitaiSearchRequest(BaseModel):
    search_query: Optional[str] = None

class ComfyUIServerInfo(BaseModel):
    server: ComfyUIServer
    models: List[Model] = []
    loras: List[Model] = []
    is_online: bool = False

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    music_file_path: Optional[str] = Field(None, alias="music_file")
    music_duration: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    music_file: Optional[str] = None
    
    class Config:
        populate_by_name = True

class Scene(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: Optional[str] = ""
    lyrics: Optional[str] = ""  # Scene-specific lyrics
    order: int = 0
    # Alternate system
    parent_scene_id: Optional[str] = None  # Reference to original scene if this is an alternate
    alternate_number: int = 0  # 0 = original, 1 = A1, 2 = A2, etc.
    is_alternate: bool = False  # Quick flag to identify alternates
    # Timeline positioning
    duration: float = 0.0  # Total duration calculated from clips
    timeline_start: float = 0.0  # Position in project timeline
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SceneCreate(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = ""
    lyrics: Optional[str] = ""
    order: int = 0

class SceneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    lyrics: Optional[str] = None

class GeneratedContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_type: str  # "image" or "video"
    url: Optional[str] = None
    prompt: str
    negative_prompt: Optional[str] = ""
    server_id: str
    server_name: str
    model_name: str
    model_type: Optional[str] = None  # "sdxl", "flux_dev", "flux_krea", "wan_2_1", "wan_2_2", "hidream"
    generation_params: Dict[str, Any] = {}
    is_selected: bool = False  # Whether this is the active content for the clip
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator('url')
    def validate_url(cls, v, values):
        """Validate URL for security"""
        if v:
            from utils.url_validator import url_validator
            content_type = values.get('content_type', 'unknown')
            if content_type == 'video':
                url_validator.validate_video_url(v)
            elif content_type == 'image':
                url_validator.validate_image_url(v)
        return v

class ClipVersion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version_number: int
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    image_prompt: Optional[str] = None
    video_prompt: Optional[str] = None
    generation_params: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator('image_url')
    def validate_image_url(cls, v):
        """Validate image URL for security"""
        if v:
            from utils.url_validator import url_validator
            url_validator.validate_image_url(v)
        return v

    @validator('video_url')
    def validate_video_url(cls, v):
        """Validate video URL for security"""
        if v:
            from utils.url_validator import url_validator
            url_validator.validate_video_url(v)
        return v

class Clip(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scene_id: str
    name: str
    lyrics: Optional[str] = ""
    length: float = 5.0  # seconds
    timeline_position: float = 0.0  # position on timeline
    order: int = 0
    # Alternate system
    parent_clip_id: Optional[str] = None  # Reference to original clip if this is an alternate
    alternate_number: int = 0  # 0 = original, 1 = A1, 2 = A2, etc.
    is_alternate: bool = False  # Quick flag to identify alternates
    # Enhanced prompting system
    image_prompt: Optional[str] = ""
    video_prompt: Optional[str] = ""
    # Gallery system
    generated_images: List[GeneratedContent] = []
    generated_videos: List[GeneratedContent] = []
    selected_image_id: Optional[str] = None
    selected_video_id: Optional[str] = None
    # Character reference
    character_id: Optional[str] = None
    # Legacy version system (keeping for compatibility)
    versions: List[ClipVersion] = []
    active_version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClipCreate(BaseModel):
    scene_id: str
    name: str
    lyrics: Optional[str] = ""
    length: float = 5.0
    timeline_position: float = 0.0
    order: int = 0
    image_prompt: Optional[str] = ""
    video_prompt: Optional[str] = ""

class ClipUpdate(BaseModel):
    """Model for updating clip fields"""
    name: Optional[str] = None
    lyrics: Optional[str] = None
    length: Optional[float] = None
    timeline_position: Optional[float] = None
    order: Optional[int] = None
    image_prompt: Optional[str] = None
    video_prompt: Optional[str] = None

    @validator('length')
    def validate_length(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Length must be positive')
        return v

    @validator('timeline_position')
    def validate_timeline_position(cls, v):
        if v is not None and v < 0:
            raise ValueError('Timeline position cannot be negative')
        return v

class TimelinePositionUpdate(BaseModel):
    position: float = Field(..., ge=0, description="Timeline position in seconds")

    @validator('position')
    def validate_position(cls, v):
        if v < 0:
            raise ValueError('Timeline position cannot be negative')
        if v > 10000:  # Max ~3 hours
            raise ValueError('Timeline position exceeds maximum (10000 seconds)')
        return round(v, 2)  # Round to 2 decimal places

class LoraConfig(BaseModel):
    name: str
    weight: float = 1.0

class GenerationRequest(BaseModel):
    clip_id: str
    server_id: str
    prompt: str
    negative_prompt: Optional[str] = ""
    model: Optional[str] = None
    lora: Optional[str] = None  # Keep for backward compatibility
    loras: Optional[List[LoraConfig]] = []  # New multiple LoRAs support
    generation_type: str  # "image" or "video"
    params: Optional[Dict[str, Any]] = None

class StyleTemplate(BaseModel):
    """Style template for reusable generation parameters"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    category: str = "custom"  # custom, cinematic, anime, realistic, artistic
    model: Optional[str] = None
    negative_prompt: Optional[str] = ""
    loras: List[LoraConfig] = []
    params: Dict[str, Any] = {}
    preview_url: Optional[str] = None
    is_public: bool = False
    created_by: Optional[str] = None  # User ID when auth is implemented
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    use_count: int = 0

class StyleTemplateCreate(BaseModel):
    """Create a new style template"""
    name: str
    description: Optional[str] = ""
    category: str = "custom"
    model: Optional[str] = None
    negative_prompt: Optional[str] = ""
    loras: List[LoraConfig] = []
    params: Dict[str, Any] = {}
    preview_url: Optional[str] = None
    is_public: bool = False

class Character(BaseModel):
    """Character for consistent generation across project"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: Optional[str] = ""
    reference_images: List[str] = []  # URLs to reference images
    lora: Optional[str] = None  # LoRA for this character
    trigger_words: Optional[str] = ""  # Words to trigger character in prompts
    style_notes: Optional[str] = ""  # Style guidance
    generation_method: Optional[str] = "ip_adapter"  # ip_adapter, reactor, instantid, lora
    face_image: Optional[str] = None  # For Reactor/InstantID workflows
    generation_params: Optional[Dict[str, Any]] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CharacterCreate(BaseModel):
    """Create a new character"""
    project_id: str
    name: str
    description: Optional[str] = ""
    reference_images: List[str] = []
    lora: Optional[str] = None
    trigger_words: Optional[str] = ""
    style_notes: Optional[str] = ""
    generation_method: Optional[str] = "ip_adapter"  # ip_adapter, reactor, instantid, lora
    face_image: Optional[str] = None  # For Reactor/InstantID workflows
    generation_params: Optional[Dict[str, Any]] = {}

class GenerationPool(BaseModel):
    """Generation Pool - shared library of generated content"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: Optional[str] = ""
    content_type: str  # "image" or "video"
    source_type: str  # "clip_generation", "manual_upload", "batch_generation"
    source_clip_id: Optional[str] = None  # Original clip that generated this
    media_url: str  # Path to image/video file
    thumbnail_url: Optional[str] = None  # Preview thumbnail
    generation_params: Optional[Dict[str, Any]] = None  # Settings used for generation
    tags: List[str] = []  # For searching/filtering
    metadata: Optional[Dict[str, Any]] = None  # Additional info (resolution, duration, etc.)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GenerationPoolCreate(BaseModel):
    """Create a new pool item"""
    project_id: str
    name: str
    description: Optional[str] = ""
    content_type: str
    source_type: str
    source_clip_id: Optional[str] = None
    media_url: str
    thumbnail_url: Optional[str] = None
    generation_params: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    metadata: Optional[Dict[str, Any]] = None

# Enhanced Model defaults configuration with Fast and Quality presets
MODEL_DEFAULTS = {
    "flux_dev": {
        "fast": {
            "steps": 8,
            "cfg": 2.0,
            "width": 1024,
            "height": 1024,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 3,
            "video_fps": 24,
            "video_frames": 14
        },
        "quality": {
            "steps": 28,
            "cfg": 3.5,
            "width": 1024,
            "height": 1024,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 3,
            "video_fps": 24,
            "video_frames": 25
        }
    },
    "flux_krea": {
        "fast": {
            "steps": 4,
            "cfg": 1.0,
            "width": 1024,
            "height": 1024,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 24,
            "video_frames": 14
        },
        "quality": {
            "steps": 8,
            "cfg": 1.5,
            "width": 1024,
            "height": 1024,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 24,
            "video_frames": 25
        }
    },
    "sdxl": {
        "fast": {
            "steps": 15,
            "cfg": 6.0,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": True,
            "max_loras": 5,
            "video_fps": 12,
            "video_frames": 14
        },
        "quality": {
            "steps": 35,
            "cfg": 7.5,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": True,
            "max_loras": 5,
            "video_fps": 12,
            "video_frames": 25
        }
    },
    "pony": {
        "fast": {
            "steps": 12,
            "cfg": 6.5,
            "width": 1024,
            "height": 1024,
            "sampler": "euler_a",
            "scheduler": "normal",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 4,
            "negative_prompt_default": "low quality, blurry, distorted",
            "video_fps": 12,
            "video_frames": 14
        },
        "quality": {
            "steps": 28,
            "cfg": 7.0,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 4,
            "negative_prompt_default": "low quality, blurry, distorted",
            "video_fps": 12,
            "video_frames": 25
        }
    },
    "wan_2_1": {
        "fast": {
            "steps": 15,
            "cfg": 7.0,
            "width": 512,
            "height": 512,
            "sampler": "ddim",
            "scheduler": "normal",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 3,
            "video_fps": 24,
            "video_frames": 14,
            "requires_vae": "wan_2.1_vae.safetensors",
            "text_encoder": "clip_l.safetensors"
        },
        "quality": {
            "steps": 25,
            "cfg": 7.5,
            "width": 512,
            "height": 512,
            "sampler": "ddim",
            "scheduler": "normal",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 3,
            "video_fps": 24,
            "video_frames": 25,
            "requires_vae": "wan_2.1_vae.safetensors",
            "text_encoder": "clip_l.safetensors"
        }
    },
    "wan_2_2": {
        "fast": {
            "steps": 8,
            "cfg": 6.5,
            "width": 768,
            "height": 768,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 24,
            "video_frames": 14,
            "requires_high_noise_model": True,
            "requires_low_noise_model": True,
            "requires_vae": "wan2.2_vae.safetensors",
            "text_encoder": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
            "lightning_lora": "wan2.2_i2v_lightx2v_4steps_lora_v1"
        },
        "quality": {
            "steps": 20,
            "cfg": 7.5,
            "width": 768,
            "height": 768,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 24,
            "video_frames": 25,
            "requires_high_noise_model": True,
            "requires_low_noise_model": True,
            "requires_vae": "wan2.2_vae.safetensors",
            "text_encoder": "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
        }
    },
    "hidream": {
        "fast": {
            "steps": 12,
            "cfg": 5.0,
            "width": 1024,
            "height": 1024,
            "sampler": "euler_a",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 3,
            "video_fps": 12,
            "video_frames": 14
        },
        "quality": {
            "steps": 25,
            "cfg": 6.5,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 3,
            "video_fps": 12,
            "video_frames": 25
        }
    },
    "qwen_image": {
        "fast": {
            "steps": 10,
            "cfg": 5.5,
            "width": 1024,
            "height": 1024,
            "sampler": "euler_a",
            "scheduler": "normal",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 12,
            "video_frames": 14,
            "specializes_in": "text_rendering"
        },
        "quality": {
            "steps": 20,
            "cfg": 7.0,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 12,
            "video_frames": 25,
            "specializes_in": "text_rendering"
        }
    },
    "qwen_edit": {
        "fast": {
            "steps": 8,
            "cfg": 4.5,
            "width": 1024,
            "height": 1024,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": False,
            "supports_refiner": False,
            "max_loras": 0,
            "video_fps": 12,
            "video_frames": 14,
            "specializes_in": "image_editing"
        },
        "quality": {
            "steps": 15,
            "cfg": 6.0,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": False,
            "supports_refiner": False,
            "max_loras": 0,
            "video_fps": 12,
            "video_frames": 25,
            "specializes_in": "image_editing"
        }
    },
    "illustrious": {
        "fast": {
            "steps": 12,
            "cfg": 6.0,
            "width": 1024,
            "height": 1024,
            "sampler": "euler_a",
            "scheduler": "normal",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 4,
            "negative_prompt_default": "low quality, blurry, distorted",
            "video_fps": 12,
            "video_frames": 14
        },
        "quality": {
            "steps": 25,
            "cfg": 7.0,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 4,
            "negative_prompt_default": "low quality, blurry, distorted",
            "video_fps": 12,
            "video_frames": 25
        }
    },
    "ltx_video": {
        "fast": {
            "steps": 10,
            "cfg": 2.5,
            "width": 768,
            "height": 768,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": False,
            "supports_refiner": False,
            "max_loras": 0,
            "video_fps": 24,
            "video_frames": 41,
            "specializes_in": "video_generation"
        },
        "quality": {
            "steps": 20,
            "cfg": 3.0,
            "width": 768,
            "height": 768,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": False,
            "supports_refiner": False,
            "max_loras": 0,
            "video_fps": 24,
            "video_frames": 81,
            "specializes_in": "video_generation"
        }
    },
    "hunyuan_video": {
        "fast": {
            "steps": 15,
            "cfg": 6.0,
            "width": 512,
            "height": 512,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 24,
            "video_frames": 16,
            "specializes_in": "video_generation"
        },
        "quality": {
            "steps": 30,
            "cfg": 7.5,
            "width": 512,
            "height": 512,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 24,
            "video_frames": 32,
            "specializes_in": "video_generation"
        }
    },
    "flux1_pro_dev": {
        "fast": {
            "steps": 8,
            "cfg": 2.5,
            "width": 1024,
            "height": 1024,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 3,
            "video_fps": 24,
            "video_frames": 14
        },
        "quality": {
            "steps": 25,
            "cfg": 4.0,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 3,
            "video_fps": 24,
            "video_frames": 25
        }
    },
    "flux1_pro_schnell": {
        "fast": {
            "steps": 4,
            "cfg": 1.5,
            "width": 1024,
            "height": 1024,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 24,
            "video_frames": 14
        },
        "quality": {
            "steps": 8,
            "cfg": 2.0,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 24,
            "video_frames": 25
        }
    },
    "flux_kontext": {
        "fast": {
            "steps": 6,
            "cfg": 2.0,
            "width": 1024,
            "height": 1024,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 24,
            "video_frames": 14,
            "specializes_in": "context_aware"
        },
        "quality": {
            "steps": 15,
            "cfg": 3.5,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": True,
            "supports_refiner": False,
            "max_loras": 2,
            "video_fps": 24,
            "video_frames": 25,
            "specializes_in": "context_aware"
        }
    },
    "qwen_edit_2509": {
        "fast": {
            "steps": 8,
            "cfg": 4.5,
            "width": 1024,
            "height": 1024,
            "sampler": "euler",
            "scheduler": "simple",
            "supports_lora": False,
            "supports_refiner": False,
            "max_loras": 0,
            "video_fps": 12,
            "video_frames": 14,
            "specializes_in": "image_editing",
            "version": "2509"
        },
        "quality": {
            "steps": 15,
            "cfg": 6.0,
            "width": 1024,
            "height": 1024,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "supports_lora": False,
            "supports_refiner": False,
            "max_loras": 0,
            "video_fps": 12,
            "video_frames": 25,
            "specializes_in": "image_editing",
            "version": "2509"
        }
    }
}

def detect_model_type(model_name: str) -> Optional[str]:
    """Intelligently detect model type from model name"""
    model_name_lower = model_name.lower()
    
    if "flux" in model_name_lower:
        if "dev" in model_name_lower:
            return "flux_dev"
        elif "krea" in model_name_lower:
            return "flux_krea"
        else:
            return "flux_dev"  # Default flux variant
    elif "sdxl" in model_name_lower or "xl" in model_name_lower:
        return "sdxl"
    elif "pony" in model_name_lower:
        return "pony"
    elif "wan" in model_name_lower:
        if "2.2" in model_name_lower or "22" in model_name_lower:
            return "wan_2_2"
        else:
            return "wan_2_1"
    elif "hidream" in model_name_lower:
        return "hidream"
    elif "qwen" in model_name_lower:
        if "edit" in model_name_lower:
            return "qwen_edit"
        else:
            return "qwen_image"
    elif "sd15" in model_name_lower or "1.5" in model_name_lower:
        return "wan_2_1"  # Use SD 1.5 defaults
    
    # Default fallback
    return "sdxl"

def get_model_defaults(model_name: str, preset: str = "fast") -> Dict[str, Any]:
    """Get intelligent defaults based on model type and preset"""
    model_type = detect_model_type(model_name)
    model_config = MODEL_DEFAULTS.get(model_type, MODEL_DEFAULTS["sdxl"])
    
    # Return the requested preset, defaulting to fast if not found
    return model_config.get(preset, model_config.get("fast", model_config.get("quality", {})))

# ComfyUI API Helper
class ComfyUIClient:
    def __init__(self, server: ComfyUIServer):
        self.server = server
        self.base_url = server.url.rstrip('/')
        
        # Detect and extract RunPod endpoint ID
        if "runpod.ai" in self.base_url or server.server_type == "runpod":
            self.server_type = "runpod"
            # Extract endpoint ID from URL like https://api.runpod.ai/v2/ud50myrcxgmeay
            if "/v2/" in self.base_url:
                self.endpoint_id = self.base_url.split("/v2/")[-1].split("/")[0]
            else:
                self.endpoint_id = server.endpoint_id or "unknown"
        else:
            self.server_type = "standard"
            self.endpoint_id = None
        
    async def check_connection(self) -> bool:
        try:
            if self.server_type == "runpod":
                return await self._check_runpod_connection()
            else:
                return await self._check_standard_connection()
        except:
            return False
    
    async def _check_standard_connection(self) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/system_stats", timeout=5) as response:
                return response.status == 200
    
    async def _check_runpod_connection(self) -> bool:
        """Check if RunPod serverless endpoint is accessible and healthy"""
        if not self.server.api_key:
            logger.warning(f"No API key for RunPod server {self.endpoint_id}")
            return False

        if not self.endpoint_id:
            logger.error("No endpoint ID for RunPod server")
            return False

        headers = {
            "Authorization": f"Bearer {self.server.api_key}",
            "Content-Type": "application/json"
        }

        # Try multiple methods to verify endpoint
        async with aiohttp.ClientSession() as session:
            # Method 1: Check endpoint status
            try:
                status_url = f"https://api.runpod.ai/v2/{self.endpoint_id}/status"
                async with session.get(status_url, headers=headers, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if endpoint is ready to receive requests
                        if data.get("status") in ["RUNNING", "READY", "IDLE"]:
                            logger.info(f"RunPod endpoint {self.endpoint_id} is {data.get('status')}")
                            return True
                        else:
                            logger.warning(f"RunPod endpoint {self.endpoint_id} status: {data.get('status')}")
                            return False
                    elif response.status == 401:
                        logger.error(f"Invalid API key for RunPod endpoint {self.endpoint_id}")
                        return False
                    elif response.status == 404:
                        logger.error(f"RunPod endpoint {self.endpoint_id} not found")
                        return False
            except asyncio.TimeoutError:
                logger.error(f"Timeout checking RunPod endpoint {self.endpoint_id}")
                return False
            except aiohttp.ClientError as e:
                logger.error(f"Network error checking RunPod endpoint: {e}")
                return False

            # Method 2: Try to get endpoint info as fallback
            try:
                info_url = f"https://api.runpod.ai/v2/{self.endpoint_id}"
                async with session.get(info_url, headers=headers, timeout=5) as response:
                    if response.status == 200:
                        logger.info(f"RunPod endpoint {self.endpoint_id} exists")
                        return True
                    return False
            except Exception as e:
                logger.error(f"Failed to verify RunPod endpoint: {e}")
                return False
    
    async def get_models(self) -> Dict[str, List[str]]:
        try:
            if self.server_type == "runpod":
                return await self._get_runpod_models()
            else:
                return await self._get_standard_models()
        except Exception as e:
            logging.error(f"Error getting models: {e}")
        return {"checkpoints": [], "loras": [], "vaes": []}
    
    async def _get_standard_models(self) -> Dict[str, List[str]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/object_info") as response:
                if response.status == 200:
                    data = await response.json()
                    # Extract model information from ComfyUI object_info
                    models = {"checkpoints": [], "loras": [], "vaes": []}
                    
                    # Parse the complex object_info structure
                    for node_type, node_info in data.items():
                        if "input" in node_info and "required" in node_info["input"]:
                            required_inputs = node_info["input"]["required"]
                            for input_name, input_info in required_inputs.items():
                                if isinstance(input_info, list) and len(input_info) > 0:
                                    if "ckpt_name" in input_name.lower() or "checkpoint" in input_name.lower():
                                        if isinstance(input_info[0], list):
                                            models["checkpoints"].extend(input_info[0])
                                    elif "lora" in input_name.lower():
                                        if isinstance(input_info[0], list):
                                            models["loras"].extend(input_info[0])
                                    elif "vae" in input_name.lower():
                                        if isinstance(input_info[0], list):
                                            models["vaes"].extend(input_info[0])
                    
                    # Remove duplicates
                    for key in models:
                        models[key] = list(set(models[key]))
                    
                    return models
        return {"checkpoints": [], "loras": [], "vaes": []}
    
    async def _get_runpod_models(self) -> Dict[str, List[str]]:
        # RunPod serverless doesn't expose model info via API
        # Return some common models that are typically available
        return {
            "checkpoints": [
                "sd_xl_base_1.0.safetensors",
                "sd_xl_refiner_1.0.safetensors", 
                "v1-5-pruned-emaonly.ckpt",
                "realisticVisionV60B1_v60B1VAE.safetensors"
            ],
            "loras": [
                "lcm-lora-sdxl.safetensors",
                "pytorch_lora_weights.safetensors"
            ],
            "vaes": [
                "sdxl_vae.safetensors",
                "vae-ft-mse-840000-ema-pruned.ckpt"
            ]
        }
    
    async def generate_image(self, prompt: str, negative_prompt: str = "", model: str = None, params: Dict = None, loras: List = None) -> Optional[str]:
        try:
            if self.server_type == "runpod":
                return await self._generate_image_runpod(prompt, negative_prompt, model, params, loras)
            else:
                return await self._generate_image_standard(prompt, negative_prompt, model, params, loras)
        except Exception as e:
            logging.error(f"Error generating image: {e}")
        return None
    
    async def _generate_image_runpod(self, prompt: str, negative_prompt: str = "", model: str = None, params: Dict = None, loras: List = None) -> Optional[str]:
        if not self.server.api_key:
            logging.error("No API key provided for RunPod server")
            return None
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.server.api_key}"
        }
        
        # Prepare RunPod request
        runpod_input = {
            "prompt": prompt,
        }
        
        if negative_prompt:
            runpod_input["negative_prompt"] = negative_prompt
        
        if params:
            runpod_input.update({
                "width": params.get("width", 512),
                "height": params.get("height", 512), 
                "steps": params.get("steps", 20),
                "cfg_scale": params.get("cfg", 8),
                "seed": params.get("seed", -1)
            })
        
        request_data = {"input": runpod_input}
        
        async with aiohttp.ClientSession() as session:
            # Submit job to RunPod
            async with session.post(
                f"https://api.runpod.ai/v2/{self.endpoint_id}/run",
                headers=headers,
                json=request_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    job_id = result.get("id")
                    
                    if job_id:
                        # Poll for completion
                        for _ in range(120):  # 2 minutes timeout
                            await asyncio.sleep(1)
                            async with session.get(
                                f"https://api.runpod.ai/v2/{self.endpoint_id}/stream/{job_id}",
                                headers=headers
                            ) as status_response:
                                if status_response.status == 200:
                                    status_data = await status_response.json()
                                    status = status_data.get("status")
                                    
                                    if status == "COMPLETED":
                                        output = status_data.get("output", {})
                                        # RunPod typically returns image URLs or base64 data
                                        if isinstance(output, dict):
                                            image_url = output.get("image_url") or output.get("images", [{}])[0].get("url")
                                            if image_url:
                                                return image_url
                                        elif isinstance(output, str) and output.startswith("http"):
                                            return output
                                    elif status in ["FAILED", "CANCELLED"]:
                                        error_msg = status_data.get("error", "Generation failed")
                                        logging.error(f"RunPod generation failed: {error_msg}")
                                        break
        
        return None
    
    async def _generate_image_standard(self, prompt: str, negative_prompt: str = "", model: str = None, params: Dict = None, loras: List = None) -> Optional[str]:
        # Enhanced ComfyUI workflow for text-to-image with advanced parameters
        params = params or {}
        loras = loras or []
        
        # Check if using custom workflow
        if params.get('use_custom_workflow') and params.get('workflow_json'):
            try:
                import json
                workflow = json.loads(params['workflow_json'])
                # Replace placeholders in workflow with actual values
                workflow_str = json.dumps(workflow)
                workflow_str = workflow_str.replace('{{PROMPT}}', prompt)
                workflow_str = workflow_str.replace('{{NEGATIVE_PROMPT}}', negative_prompt)
                workflow_str = workflow_str.replace('{{MODEL}}', model or 'v1-5-pruned-emaonly.ckpt')
                workflow = json.loads(workflow_str)
            except:
                # Fall back to default workflow if custom workflow fails
                pass
        
        # Basic ComfyUI workflow for text-to-image
        workflow = {
                "3": {
                    "inputs": {
                        "seed": params.get("seed", 42) if params else 42,
                        "steps": params.get("steps", 20) if params else 20,
                        "cfg": params.get("cfg", 8) if params else 8,
                        "sampler_name": params.get("sampler", "euler") if params else "euler",
                        "scheduler": params.get("scheduler", "normal") if params else "normal",
                        "denoise": 1,
                        "model": ["4", 0],
                        "positive": ["6", 0],
                        "negative": ["7", 0],
                        "latent_image": ["5", 0]
                    },
                    "class_type": "KSampler"
                },
                "4": {
                    "inputs": {
                        "ckpt_name": model or "v1-5-pruned-emaonly.ckpt"
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "5": {
                    "inputs": {
                        "width": params.get("width", 512) if params else 512,
                        "height": params.get("height", 512) if params else 512,
                        "batch_size": 1
                    },
                    "class_type": "EmptyLatentImage"
                },
                "6": {
                    "inputs": {
                        "text": prompt,
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "7": {
                    "inputs": {
                        "text": negative_prompt,
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "8": {
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["4", 2]
                    },
                    "class_type": "VAEDecode"
                },
                "9": {
                    "inputs": {
                        "filename_prefix": "ComfyUI",
                        "images": ["8", 0]
                    },
                    "class_type": "SaveImage"
                }
            }
            
        try:
            async with aiohttp.ClientSession() as session:
                # Queue the prompt
                async with session.post(f"{self.base_url}/prompt", json={"prompt": workflow}) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        
                        if prompt_id:
                            # Poll for completion
                            for _ in range(60):  # 60 seconds timeout
                                await asyncio.sleep(1)
                                async with session.get(f"{self.base_url}/history/{prompt_id}") as hist_response:
                                    if hist_response.status == 200:
                                        history = await hist_response.json()
                                        if prompt_id in history:
                                            outputs = history[prompt_id].get("outputs", {})
                                            for node_id, output in outputs.items():
                                                if "images" in output:
                                                    image_info = output["images"][0]
                                                    filename = image_info["filename"]
                                                    return f"{self.base_url}/view?filename={filename}"
        except Exception as e:
            logging.error(f"Error generating image: {e}")
        return None

    async def generate_video(self, prompt: str, negative_prompt: str = "", model: str = None, params: Dict = None, loras: List = None) -> Optional[str]:
        try:
            if self.server_type == "runpod":
                return await self._generate_video_runpod(prompt, negative_prompt, model, params, loras)
            else:
                return await self._generate_video_standard(prompt, negative_prompt, model, params, loras)
        except Exception as e:
            logging.error(f"Error generating video: {e}")
        return None

    async def _generate_video_runpod(self, prompt: str, negative_prompt: str = "", model: str = None, params: Dict = None, loras: List = None) -> Optional[str]:
        if not self.server.api_key:
            logging.error("No API key provided for RunPod server")
            return None
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.server.api_key}"
        }
        
        # Prepare RunPod request for video generation
        runpod_input = {
            "prompt": prompt,
            "generation_type": "video"
        }
        
        if negative_prompt:
            runpod_input["negative_prompt"] = negative_prompt
        
        if params:
            # Video-specific parameters
            runpod_input.update({
                "width": params.get("width", 768),
                "height": params.get("height", 768), 
                "frames": params.get("video_frames", 14),
                "fps": params.get("video_fps", 24),
                "steps": params.get("steps", 20),
                "cfg_scale": params.get("cfg", 7),
                "seed": params.get("seed", -1),
                "motion_bucket_id": params.get("motion_bucket_id", 127)
            })
        
        request_data = {"input": runpod_input}
        
        async with aiohttp.ClientSession() as session:
            # Submit job to RunPod
            async with session.post(
                f"https://api.runpod.ai/v2/{self.endpoint_id}/run",
                headers=headers,
                json=request_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    job_id = result.get("id")
                    
                    if job_id:
                        # Poll for completion - videos take longer
                        for _ in range(300):  # 5 minutes timeout
                            await asyncio.sleep(2)
                            async with session.get(
                                f"https://api.runpod.ai/v2/{self.endpoint_id}/stream/{job_id}",
                                headers=headers
                            ) as status_response:
                                if status_response.status == 200:
                                    status_data = await status_response.json()
                                    status = status_data.get("status")
                                    
                                    if status == "COMPLETED":
                                        output = status_data.get("output", {})
                                        if isinstance(output, dict):
                                            video_url = output.get("video_url") or output.get("videos", [{}])[0].get("url")
                                            if video_url:
                                                return video_url
                                        elif isinstance(output, str) and output.startswith("http"):
                                            return output
                                    elif status in ["FAILED", "CANCELLED"]:
                                        error_msg = status_data.get("error", "Video generation failed")
                                        logging.error(f"RunPod video generation failed: {error_msg}")
                                        break
        
        return None
    
    async def _generate_video_standard(self, prompt: str, negative_prompt: str = "", model: str = None, params: Dict = None, loras: List = None) -> Optional[str]:
        # Enhanced ComfyUI workflow for video generation
        params = params or {}
        loras = loras or []
        
        # Detect model type to use appropriate workflow
        model_type = detect_model_type(model or "")
        
        if "wan" in model_type:
            # Use Wan 2.1/2.2 specific workflow
            workflow = await self._create_wan_video_workflow(prompt, negative_prompt, model, params, loras)
        elif "svd" in model_type.lower() or "stable_video" in model_type.lower():
            # Use Stable Video Diffusion workflow
            workflow = await self._create_svd_workflow(prompt, negative_prompt, model, params, loras)
        else:
            # Use AnimateDiff workflow for other models
            workflow = await self._create_animatediff_workflow(prompt, negative_prompt, model, params, loras)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Queue the prompt
                async with session.post(f"{self.base_url}/prompt", json={"prompt": workflow}) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        
                        if prompt_id:
                            # Poll for completion - videos take longer
                            for _ in range(300):  # 5 minutes timeout
                                await asyncio.sleep(2)
                                async with session.get(f"{self.base_url}/history/{prompt_id}") as hist_response:
                                    if hist_response.status == 200:
                                        history = await hist_response.json()
                                        if prompt_id in history:
                                            outputs = history[prompt_id].get("outputs", {})
                                            for node_id, output in outputs.items():
                                                if "gifs" in output or "videos" in output:
                                                    # Look for video output
                                                    video_files = output.get("gifs", output.get("videos", []))
                                                    if video_files:
                                                        video_info = video_files[0]
                                                        filename = video_info.get("filename")
                                                        if filename:
                                                            return f"{self.base_url}/view?filename={filename}"
        except Exception as e:
            logging.error(f"Error generating video: {e}")
        return None
    
    async def _create_wan_video_workflow(self, prompt: str, negative_prompt: str, model: str, params: Dict, loras: List) -> Dict:
        """Create ComfyUI workflow for Wan 2.1/2.2 video generation"""
        model_type = detect_model_type(model)
        
        # Basic Wan video workflow structure
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": model or "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": negative_prompt or "",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "width": params.get("width", 768),
                    "height": params.get("height", 768),
                    "length": params.get("video_frames", 14),
                    "batch_size": 1
                },
                "class_type": "EmptyLatentVideo"
            },
            "5": {
                "inputs": {
                    "seed": params.get("seed", 42),
                    "steps": params.get("steps", 20),
                    "cfg": params.get("cfg", 7.5),
                    "sampler_name": params.get("sampler", "euler"),
                    "scheduler": params.get("scheduler", "simple"),
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0]
                },
                "class_type": "KSampler"
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "7": {
                "inputs": {
                    "filename_prefix": "video",
                    "fps": params.get("video_fps", 24),
                    "images": ["6", 0]
                },
                "class_type": "SaveAnimatedWEBP"
            }
        }
        
        return workflow
    
    async def _create_svd_workflow(self, prompt: str, negative_prompt: str, model: str, params: Dict, loras: List) -> Dict:
        """Create ComfyUI workflow for Stable Video Diffusion"""
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": model or "svd_xt_1_1.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "width": params.get("width", 1024),
                    "height": params.get("height", 576),
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "3": {
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "seed": params.get("seed", 42),
                    "steps": params.get("steps", 25),
                    "cfg": params.get("cfg", 2.5),
                    "sampler_name": "euler",
                    "scheduler": "karras",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["3", 0],
                    "negative": ["3", 0],
                    "latent_image": ["2", 0]
                },
                "class_type": "KSampler"
            },
            "5": {
                "inputs": {
                    "samples": ["4", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "6": {
                "inputs": {
                    "filename_prefix": "svd_video",
                    "fps": params.get("video_fps", 6),
                    "images": ["5", 0]
                },
                "class_type": "SaveAnimatedWEBP"
            }
        }
        
        return workflow
    
    async def _create_animatediff_workflow(self, prompt: str, negative_prompt: str, model: str, params: Dict, loras: List) -> Dict:
        """Create ComfyUI workflow for AnimateDiff video generation"""
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": model or "v1-5-pruned-emaonly.ckpt"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": negative_prompt or "low quality, blurry",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "width": params.get("width", 512),
                    "height": params.get("height", 512),
                    "length": params.get("video_frames", 16),
                    "batch_size": 1
                },
                "class_type": "EmptyLatentVideo"
            },
            "5": {
                "inputs": {
                    "seed": params.get("seed", 42),
                    "steps": params.get("steps", 20),
                    "cfg": params.get("cfg", 7.5),
                    "sampler_name": params.get("sampler", "euler_a"),
                    "scheduler": params.get("scheduler", "normal"),
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0]
                },
                "class_type": "KSampler"
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "7": {
                "inputs": {
                    "filename_prefix": "animatediff",
                    "fps": params.get("video_fps", 8),
                    "images": ["6", 0]
                },
                "class_type": "SaveAnimatedWEBP"
            }
        }
        
        return workflow

    # Character Generation Methods
    
    async def generate_character_with_ip_adapter(self, prompt: str, character_image: str, model: str = None, params: Dict = None) -> Optional[str]:
        """Generate consistent character using IP-Adapter"""
        try:
            if self.server_type == "runpod":
                return await self._generate_ip_adapter_runpod(prompt, character_image, model, params)
            else:
                return await self._generate_ip_adapter_standard(prompt, character_image, model, params)
        except Exception as e:
            logging.error(f"Error generating character with IP-Adapter: {e}")
        return None
    
    async def generate_character_with_reactor(self, prompt: str, face_image: str, target_image: str = None, model: str = None, params: Dict = None) -> Optional[str]:
        """Generate character using Reactor face swap"""
        try:
            if self.server_type == "runpod":
                return await self._generate_reactor_runpod(prompt, face_image, target_image, model, params)
            else:
                return await self._generate_reactor_standard(prompt, face_image, target_image, model, params)
        except Exception as e:
            logging.error(f"Error generating character with Reactor: {e}")
        return None
    
    async def generate_character_with_instantid(self, prompt: str, face_image: str, pose_image: str = None, model: str = None, params: Dict = None) -> Optional[str]:
        """Generate character using InstantID with pose control"""
        try:
            if self.server_type == "runpod":
                return await self._generate_instantid_runpod(prompt, face_image, pose_image, model, params)
            else:
                return await self._generate_instantid_standard(prompt, face_image, pose_image, model, params)
        except Exception as e:
            logging.error(f"Error generating character with InstantID: {e}")
        return None
    
    async def _generate_ip_adapter_standard(self, prompt: str, character_image: str, model: str = None, params: Dict = None) -> Optional[str]:
        """IP-Adapter workflow for standard ComfyUI"""
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": model or "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": "low quality, blurry, bad anatomy",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "image": character_image,
                    "model": ["1", 0]
                },
                "class_type": "IPAdapterModelLoader"
            },
            "5": {
                "inputs": {
                    "weight": 0.7,
                    "image": character_image,
                    "ipadapter": ["4", 0],
                    "clip_vision": ["6", 0],
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0]
                },
                "class_type": "IPAdapterApply"
            },
            "6": {
                "inputs": {
                    "ckpt_name": "clip_vision.safetensors"
                },
                "class_type": "CLIPVisionLoader"
            },
            "7": {
                "inputs": {
                    "width": params.get("width", 1024) if params else 1024,
                    "height": params.get("height", 1024) if params else 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "8": {
                "inputs": {
                    "seed": params.get("seed", 42) if params else 42,
                    "steps": params.get("steps", 20) if params else 20,
                    "cfg": params.get("cfg", 7.5) if params else 7.5,
                    "sampler_name": params.get("sampler", "euler") if params else "euler",
                    "scheduler": params.get("scheduler", "normal") if params else "normal",
                    "denoise": 1.0,
                    "model": ["5", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["7", 0]
                },
                "class_type": "KSampler"
            },
            "9": {
                "inputs": {
                    "samples": ["8", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "10": {
                "inputs": {
                    "filename_prefix": "character_ip_adapter",
                    "images": ["9", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Queue the prompt
                async with session.post(f"{self.base_url}/prompt", json={"prompt": workflow}) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        
                        # Wait for completion and get result
                        while True:
                            async with session.get(f"{self.base_url}/history/{prompt_id}") as history_response:
                                if history_response.status == 200:
                                    history = await history_response.json()
                                    if prompt_id in history:
                                        # Get the filename from the history
                                        images = history[prompt_id].get("outputs", {}).get("10", {}).get("images", [])
                                        if images:
                                            filename = images[0].get("filename")
                                            return f"{self.base_url}/view?filename={filename}"
                            await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Error in IP-Adapter workflow: {e}")
        return None
    
    async def _generate_reactor_standard(self, prompt: str, face_image: str, target_image: str = None, model: str = None, params: Dict = None) -> Optional[str]:
        """Reactor face swap workflow for standard ComfyUI"""
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": model or "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": "low quality, blurry, bad anatomy",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "image": face_image
                },
                "class_type": "LoadImageMask"
            },
            "5": {
                "inputs": {
                    "image": target_image or face_image,
                    "model": ["1", 0],
                    "face_image": ["4", 0],
                    "blend_ratio": 0.8
                },
                "class_type": "ReactorFaceSwap"
            },
            "6": {
                "inputs": {
                    "seed": params.get("seed", 42) if params else 42,
                    "steps": params.get("steps", 20) if params else 20,
                    "cfg": params.get("cfg", 7.5) if params else 7.5,
                    "sampler_name": params.get("sampler", "euler") if params else "euler",
                    "scheduler": params.get("scheduler", "normal") if params else "normal",
                    "denoise": 0.75,
                    "model": ["5", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0]
                },
                "class_type": "KSampler"
            },
            "7": {
                "inputs": {
                    "samples": ["6", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "8": {
                "inputs": {
                    "filename_prefix": "character_reactor",
                    "images": ["7", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Queue the prompt
                async with session.post(f"{self.base_url}/prompt", json={"prompt": workflow}) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        
                        # Wait for completion and get result
                        while True:
                            async with session.get(f"{self.base_url}/history/{prompt_id}") as history_response:
                                if history_response.status == 200:
                                    history = await history_response.json()
                                    if prompt_id in history:
                                        # Get the filename from the history
                                        images = history[prompt_id].get("outputs", {}).get("8", {}).get("images", [])
                                        if images:
                                            filename = images[0].get("filename")
                                            return f"{self.base_url}/view?filename={filename}"
                            await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Error in Reactor workflow: {e}")
        return None
    
    # RunPod methods (simplified for now)
    async def _generate_ip_adapter_runpod(self, prompt: str, character_image: str, model: str = None, params: Dict = None) -> Optional[str]:
        """IP-Adapter for RunPod (simplified)"""
        # For now, fall back to standard generation
        return await self.generate_image(prompt, "low quality, blurry", model, params, [])
    
    async def _generate_reactor_runpod(self, prompt: str, face_image: str, target_image: str = None, model: str = None, params: Dict = None) -> Optional[str]:
        """Reactor for RunPod (simplified)"""
        # For now, fall back to standard generation
        return await self.generate_image(prompt, "low quality, blurry", model, params, [])
    
    async def _generate_instantid_runpod(self, prompt: str, face_image: str, pose_image: str = None, model: str = None, params: Dict = None) -> Optional[str]:
        """InstantID for RunPod (simplified)"""
        # For now, fall back to standard generation
        return await self.generate_image(prompt, "low quality, blurry", model, params, [])
    
    async def _generate_instantid_standard(self, prompt: str, face_image: str, pose_image: str = None, model: str = None, params: Dict = None) -> Optional[str]:
        """InstantID workflow (placeholder for future implementation)"""
        # For now, fall back to IP-Adapter
        return await self._generate_ip_adapter_standard(prompt, face_image, model, params)
    
    async def generate_with_openpose(self, prompt: str, reference_image: str, negative_prompt: str = "", model: str = None, params: Dict = None) -> Optional[str]:
        """Generate using OpenPose ControlNet for consistent posing"""
        try:
            if self.server_type == "runpod":
                return await self._generate_openpose_runpod(prompt, reference_image, negative_prompt, model, params)
            else:
                return await self._generate_openpose_standard(prompt, reference_image, negative_prompt, model, params)
        except Exception as e:
            logging.error(f"Error generating with OpenPose: {e}")
        return None
    
    async def generate_with_depth(self, prompt: str, reference_image: str, negative_prompt: str = "", model: str = None, params: Dict = None) -> Optional[str]:
        """Generate using Depth ControlNet for 3D consistency"""
        try:
            if self.server_type == "runpod":
                return await self._generate_depth_runpod(prompt, reference_image, negative_prompt, model, params)
            else:
                return await self._generate_depth_standard(prompt, reference_image, negative_prompt, model, params)
        except Exception as e:
            logging.error(f"Error generating with Depth ControlNet: {e}")
        return None
    
    async def _generate_openpose_standard(self, prompt: str, reference_image: str, negative_prompt: str = "", model: str = None, params: Dict = None) -> Optional[str]:
        """OpenPose workflow for standard ComfyUI"""
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": model or "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": negative_prompt or "low quality, blurry, bad anatomy, distorted",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "image": reference_image
                },
                "class_type": "LoadImage"
            },
            "5": {
                "inputs": {
                    "preprocessor": "dw_openpose_full",
                    "model": "control_v11p_sd15_openpose.pth",
                    "image": ["4", 0]
                },
                "class_type": "ControlNetLoader"
            },
            "6": {
                "inputs": {
                    "strength": 0.8,
                    "conditioning": ["2", 0],
                    "control_net": ["5", 0],
                    "image": ["4", 0]
                },
                "class_type": "ControlNetApply"
            },
            "7": {
                "inputs": {
                    "seed": params.get("seed", 42) if params else 42,
                    "steps": params.get("steps", 20) if params else 20,
                    "cfg": params.get("cfg", 7.5) if params else 7.5,
                    "sampler_name": params.get("sampler", "euler") if params else "euler",
                    "scheduler": params.get("scheduler", "normal") if params else "normal",
                    "denoise": 0.75,
                    "model": ["6", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["8", 0]
                },
                "class_type": "KSampler"
            },
            "8": {
                "inputs": {
                    "width": params.get("width", 1024) if params else 1024,
                    "height": params.get("height", 1024) if params else 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "9": {
                "inputs": {
                    "samples": ["7", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "10": {
                "inputs": {
                    "filename_prefix": "character_openpose",
                    "images": ["9", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/prompt", json={"prompt": workflow}) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        
                        while True:
                            async with session.get(f"{self.base_url}/history/{prompt_id}") as history_response:
                                if history_response.status == 200:
                                    history = await history_response.json()
                                    if prompt_id in history:
                                        images = history[prompt_id].get("outputs", {}).get("10", {}).get("images", [])
                                        if images:
                                            filename = images[0].get("filename")
                                            return f"{self.base_url}/view?filename={filename}"
                            await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Error in OpenPose workflow: {e}")
        return None
    
    async def _generate_depth_standard(self, prompt: str, reference_image: str, negative_prompt: str = "", model: str = None, params: Dict = None) -> Optional[str]:
        """Depth ControlNet workflow for standard ComfyUI"""
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": model or "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": negative_prompt or "low quality, blurry, bad anatomy, distorted",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "image": reference_image
                },
                "class_type": "LoadImage"
            },
            "5": {
                "inputs": {
                    "preprocessor": "depth_midas",
                    "model": "control_v11f1p_sd15_depth.pth",
                    "image": ["4", 0]
                },
                "class_type": "ControlNetLoader"
            },
            "6": {
                "inputs": {
                    "strength": 0.7,
                    "conditioning": ["2", 0],
                    "control_net": ["5", 0],
                    "image": ["4", 0]
                },
                "class_type": "ControlNetApply"
            },
            "7": {
                "inputs": {
                    "seed": params.get("seed", 42) if params else 42,
                    "steps": params.get("steps", 20) if params else 20,
                    "cfg": params.get("cfg", 7.5) if params else 7.5,
                    "sampler_name": params.get("sampler", "euler") if params else "euler",
                    "scheduler": params.get("scheduler", "normal") if params else "normal",
                    "denoise": 0.75,
                    "model": ["6", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["8", 0]
                },
                "class_type": "KSampler"
            },
            "8": {
                "inputs": {
                    "width": params.get("width", 1024) if params else 1024,
                    "height": params.get("height", 1024) if params else 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "9": {
                "inputs": {
                    "samples": ["7", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "10": {
                "inputs": {
                    "filename_prefix": "character_depth",
                    "images": ["9", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/prompt", json={"prompt": workflow}) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        
                        while True:
                            async with session.get(f"{self.base_url}/history/{prompt_id}") as history_response:
                                if history_response.status == 200:
                                    history = await history_response.json()
                                    if prompt_id in history:
                                        images = history[prompt_id].get("outputs", {}).get("10", {}).get("images", [])
                                        if images:
                                            filename = images[0].get("filename")
                                            return f"{self.base_url}/view?filename={filename}"
                            await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Error in Depth workflow: {e}")
        return None
    
    # RunPod fallback methods
    async def _generate_openpose_runpod(self, prompt: str, reference_image: str, negative_prompt: str = "", model: str = None, params: Dict = None) -> Optional[str]:
        """OpenPose for RunPod (simplified fallback)"""
        return await self.generate_image(prompt, negative_prompt or "low quality, blurry", model, params, [])
    
    async def _generate_depth_runpod(self, prompt: str, reference_image: str, negative_prompt: str = "", model: str = None, params: Dict = None) -> Optional[str]:
        """Depth for RunPod (simplified fallback)"""
        return await self.generate_image(prompt, negative_prompt or "low quality, blurry", model, params, [])

# API Routes
# DEPRECATED: These legacy /api endpoints are deprecated. Use /api/v1 instead.
# Sunset date: 2025-06-01

@api_router.get("/")
async def root():
    """DEPRECATED: Use /api/v1/ instead. This endpoint will be removed on 2025-06-01."""
    warnings.warn("Legacy /api/ endpoint is deprecated. Use /api/v1/", DeprecationWarning)
    logging.warning("Legacy /api/ endpoint accessed. Client should migrate to /api/v1/")
    return {
        "message": "StoryCanvas API is running", 
        "status": "healthy",
        "deprecated": True,
        "sunset_date": LEGACY_API_SUNSET_DATE,
        "migration_url": "/api/v1/"
    }

@api_router.get("/health")
async def health_check():
    """DEPRECATED: Use /api/v1/health instead. This endpoint will be removed on 2025-06-01."""
    warnings.warn("Legacy /api/health endpoint is deprecated. Use /api/v1/health", DeprecationWarning)
    logging.warning("Legacy /api/health endpoint accessed. Client should migrate to /api/v1/health")
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {},
        "deprecated": True,
        "sunset_date": LEGACY_API_SUNSET_DATE,
        "migration_url": "/api/v1/health"
    }

    # Check database
    db_healthy = await db_manager.health_check()
    health_status["components"]["database"] = {
        "status": "up" if db_healthy else "down",
        "database": db_manager.db_name,
        "url": db_manager.mongo_url.replace('mongodb://', 'mongodb://***@')
    }

    # Overall status
    if not db_healthy:
        health_status["status"] = "unhealthy"

    return health_status

# ComfyUI Server Management
@api_router.post("/comfyui/servers", response_model=ComfyUIServer)
async def add_comfyui_server(server_data: ComfyUIServerCreate, db_conn = Depends(get_database)):
    server_dict = server_data.dict()
    
    # Auto-detect RunPod serverless
    if "runpod.ai" in server_dict["url"]:
        server_dict["server_type"] = "runpod"
        # Extract endpoint ID from URL
        if "/v2/" in server_dict["url"]:
            endpoint_id = server_dict["url"].split("/v2/")[-1].split("/")[0]
            server_dict["endpoint_id"] = endpoint_id
    
    server = ComfyUIServer(**server_dict)
    await db_conn.comfyui_servers.insert_one(server.dict())
    return server

@api_router.get("/comfyui/servers", response_model=List[ComfyUIServer])
async def get_comfyui_servers(db_conn = Depends(get_database)):
    servers = await db_conn.comfyui_servers.find().to_list(100)
    return [ComfyUIServer(**server) for server in servers]

@api_router.delete("/comfyui/servers/{server_id}")
async def delete_comfyui_server(server_id: str, db_conn = Depends(get_database)):
    server_data = await db_conn.comfyui_servers.find_one({"id": server_id})
    if not server_data:
        raise ServerNotFoundError(server_id)
    
    await db_conn.comfyui_servers.delete_one({"id": server_id})
    return {"message": "Server deleted successfully"}

@api_router.get("/comfyui/servers/{server_id}/info", response_model=ComfyUIServerInfo)
async def get_server_info(server_id: str, db_conn = Depends(get_database)):
    server_data = await db_conn.comfyui_servers.find_one({"id": server_id})
    if not server_data:
        raise ServerNotFoundError(server_id)
    
    server = ComfyUIServer(**server_data)
    client = ComfyUIClient(server)
    
    is_online = await client.check_connection()
    models_data = {"checkpoints": [], "loras": [], "vaes": []} if not is_online else await client.get_models()
    
    models = [Model(name=name, type="checkpoint") for name in models_data.get("checkpoints", [])]
    loras = [Model(name=name, type="lora") for name in models_data.get("loras", [])]
    
    return ComfyUIServerInfo(
        server=server,
        models=models,
        loras=loras,
        is_online=is_online
    )

# Enhanced Model Management System
@api_router.get("/models", response_model=List[DatabaseModel])
async def get_models(
    type: Optional[str] = None,
    server_source: Optional[str] = None,
    is_active: Optional[bool] = None,
    db_conn = Depends(get_database)
):
    """Get all models with optional filtering"""
    query = {}
    if type:
        query["type"] = type
    if server_source:
        query["server_source"] = server_source
    if is_active is not None:
        query["is_active"] = is_active
    
    models = await db_conn.database_models.find(query).to_list(1000)
    return [DatabaseModel(**model) for model in models]

@api_router.put("/models/{model_id}", response_model=DatabaseModel)
async def update_model(model_id: str, model_update: DatabaseModelUpdate, db_conn = Depends(get_database)):
    """Update a model"""
    update_data = {k: v for k, v in model_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db_conn.database_models.update_one(
        {"id": model_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Model not found")
    
    updated_model = await db_conn.database_models.find_one({"id": model_id})
    return DatabaseModel(**updated_model)

@api_router.delete("/models/{model_id}")
async def delete_model(model_id: str, db_conn = Depends(get_database)):
    """Delete a model"""
    result = await db_conn.database_models.delete_one({"id": model_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Model deleted successfully"}

@api_router.post("/models/{model_id}/sync-civitai")
async def sync_model_civitai(model_id: str, db_conn = Depends(get_database)):
    """Sync model with Civitai database and get available profiles"""
    print(f"Sync request received for model: {model_id}")  # Debug
    
    # First check if this model is active on any backend
    if active_models_service:
        active_model = await active_models_service.get_active_models(backend_id=None, model_type=None)
        is_active = any(model['model_id'] == model_id for model in active_model)
        
        if not is_active:
            raise HTTPException(
                status_code=403, 
                detail="Model is not active on any backend server. Only active models can be synced with Civitai."
            )
    
    model_data = await db_conn.database_models.find_one({"id": model_id})
    if not model_data:
        raise HTTPException(status_code=404, detail="Model not found")
    
    print(f"Model found: {model_data['name']}")  # Debug
    
    try:
        # Search in Civitai database using MongoDB
        best_match = await find_best_civitai_match_mongodb(model_data["name"], db_conn)
        
        if not best_match:
            # Fallback: try to find any match with lower threshold
            fallback_match = await find_best_civitai_match_mongodb(model_data["name"], db_conn, fallback=True)
            if fallback_match:
                best_match = fallback_match
                match_quality = "low_confidence"
            else:
                raise HTTPException(status_code=404, detail="No matching model found in Civitai database")
        else:
            match_quality = "high_confidence"
        
        # Get available profiles for this model
        available_profiles = await get_model_profiles(best_match, db_conn)
        
        # Get data from first model version
        first_version = best_match.get("modelVersions", [{}])[0] if best_match.get("modelVersions") else {}
        
        # Create enhanced Civitai info
        civitai_info = CivitaiModelInfo(
            modelId=str(best_match.get("id")),
            name=best_match.get("name"),
            description=best_match.get("description"),
            type=best_match.get("type"),
            tags=best_match.get("tags", []),
            trainedWords=first_version.get("trainedWords", []),
            baseModel=first_version.get("baseModel"),
            baseModelType=first_version.get("baseModelType"),
            modelVersions=best_match.get("modelVersions", []),
            images=first_version.get("images", []),
            # Additional fields
            allowDerivatives=best_match.get("allowDerivatives"),
            sfwOnly=best_match.get("sfwOnly"),
            nsfw=best_match.get("nsfw"),
            nsfwLevel=best_match.get("nsfwLevel"),
            cosmetic=best_match.get("cosmetic"),
            stats=best_match.get("stats", {}),
            allowNoCredit=best_match.get("allowNoCredit"),
            allowCommercialUse=best_match.get("allowCommercialUse", []),
            availability=best_match.get("availability"),
            supportsGeneration=best_match.get("supportsGeneration"),
            downloadUrl=first_version.get("files", [{}])[0].get("downloadUrl") if first_version.get("files") else None
        )
        
        # Update model with Civitai info and available profiles
        await db_conn.database_models.update_one(
            {"id": model_id},
            {"$set": {
                "civitai_info": civitai_info.dict(), 
                "available_profiles": available_profiles,
                "updated_at": datetime.now(timezone.utc),
                "civitai_match_quality": match_quality
            }}
        )
        
        # Also update active models tracking with Civitai info
        if active_models_service:
            await active_models_service.sync_model_with_civitai(
                model_id=model_id,
                civitai_info=civitai_info.dict(),
                match_quality=match_quality
            )
        
        return {
            "model_id": model_id,
            "civitai_info": civitai_info.dict(),
            "available_profiles": available_profiles,
            "match_quality": match_quality
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during sync: {str(e)}")  # Debug
        raise HTTPException(status_code=500, detail=f"Failed to sync from Civitai database: {str(e)}")

@api_router.post("/models/{model_id}/search-civitai")
async def search_civitai_matches(model_id: str, request: CivitaiSearchRequest, db_conn = Depends(get_database)):
    """Search for potential Civitai matches using MongoDB"""
    
    # First check if this model is active on any backend
    if active_models_service:
        active_model = await active_models_service.get_active_models(backend_id=None, model_type=None)
        is_active = any(model['model_id'] == model_id for model in active_model)
        
        if not is_active:
            raise HTTPException(
                status_code=403, 
                detail="Model is not active on any backend server. Only active models can search Civitai matches."
            )
    
    model_data = await db_conn.database_models.find_one({"id": model_id})
    if not model_data:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        # Use custom search query or model name
        query = request.search_query or model_data["name"]
        
        # Search in MongoDB using text search
        matches = []
        query_lower = query.lower()
        
        # First try exact name match
        exact_match = await db_conn.database_models.find_one({
            "source": "civitai_sdxl",
            "name": {"$regex": query, "$options": "i"}
        })
        
        if exact_match:
            matches.append({
                "civitai_model": exact_match["civitai_info"],
                "match_score": 1.0,
                "match_reason": "Exact name match in MongoDB"
            })
        
        # Then try text search for more results
        text_search_results = await db_conn.database_models.find({
            "source": "civitai_sdxl",
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"civitai_info.description": {"$regex": query, "$options": "i"}},
                {"civitai_info.tags": {"$in": [query]}}
            ]
        }).to_list(length=20)
        
        for doc in text_search_results:
            # Skip if already added as exact match
            if any(m["civitai_model"]["modelId"] == doc["civitai_info"]["modelId"] for m in matches):
                continue
            
            # Calculate simple score
            score = 0.0
            name = doc["civitai_info"]["name"].lower()
            description = doc["civitai_info"].get("description", "").lower()
            tags = [tag.lower() for tag in doc["civitai_info"].get("tags", [])]
            
            # Name matching
            if query_lower in name:
                score += 0.8
            if name in query_lower:
                score += 0.6
            
            # Description matching
            if query_lower in description:
                score += 0.3
            
            # Tag matching
            for tag in tags:
                if query_lower in tag or tag in query_lower:
                    score += 0.2
                    break
            
            if score > 0.3:  # Include reasonable matches
                matches.append({
                    "civitai_model": doc["civitai_info"],
                    "match_score": min(score, 1.0),
                    "match_reason": "MongoDB text search match"
                })
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "server_model": model_data["name"],
            "search_query": query,
            "matches": matches[:20]  # Return top 20 matches
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search Civitai database: {str(e)}")


# Active Models Tracking Endpoints

@api_router.get("/active-models", response_model=List[BackendModelInfo])
async def get_active_models(backend_id: Optional[str] = None, 
                           model_type: Optional[str] = None,
                           db_conn = Depends(get_database)):
    """Get list of active models on backends"""
    if not active_models_service:
        raise HTTPException(status_code=503, detail="Active models service not available")
    
    # Convert string to ModelType enum if provided
    type_enum = None
    if model_type:
        try:
            type_enum = ModelType(model_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid model type: {model_type}")
    
    models = await active_models_service.get_active_models(
        backend_id=backend_id,
        model_type=type_enum
    )
    
    return models

@api_router.get("/backends", response_model=List[BackendInfo])
async def get_backends(online_only: bool = True, db_conn = Depends(get_database)):
    """Get list of ComfyUI backends"""
    if not active_models_service:
        raise HTTPException(status_code=503, detail="Active models service not available")
    
    backends = await active_models_service.get_backends(online_only=online_only)
    return backends

@api_router.get("/backends/{backend_id}/models", response_model=List[BackendModelInfo])
async def get_backend_models(backend_id: str, db_conn = Depends(get_database)):
    """Get models for a specific backend"""
    if not active_models_service:
        raise HTTPException(status_code=503, detail="Active models service not available")
    
    models = await active_models_service.get_active_models(backend_id=backend_id)
    return models

@api_router.post("/models/{model_id}/link-civitai")
async def link_civitai_model(model_id: str, request: CivitaiLinkRequest, db_conn = Depends(get_database)):
    """Manually link a model to a specific Civitai model"""
    model_data = await db_conn.database_models.find_one({"id": model_id})
    if not model_data:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        civitai_api_key = os.getenv("CIVITAI_API_KEY")
        if not civitai_api_key:
            raise HTTPException(status_code=400, detail="Civitai API key not configured")
        
        # Get specific Civitai model
        model_url = f"https://civitai.com/api/v1/models/{request.civitai_model_id}"
        headers = {"Authorization": f"Bearer {civitai_api_key}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(model_url, headers=headers) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to fetch Civitai model")
                
                civitai_model = await response.json()
                
                civitai_info = CivitaiModelInfo(
                    modelId=str(civitai_model.get("id")),
                    name=civitai_model.get("name"),
                    description=civitai_model.get("description"),
                    type=civitai_model.get("type"),
                    tags=civitai_model.get("tags", []),
                    trainedWords=civitai_model.get("trainedWords", []),
                    baseModel=civitai_model.get("baseModel"),
                    baseModelType=civitai_model.get("baseModelType"),
                    modelVersions=civitai_model.get("modelVersions", []),
                    images=civitai_model.get("images", [])
                )
                
                # Update model with Civitai info
                await db_conn.database_models.update_one(
                    {"id": model_id},
                    {"$set": {
                        "civitai_info": civitai_info.dict(), 
                        "updated_at": datetime.now(timezone.utc),
                        "civitai_match_quality": "manual"
                    }}
                )
                
                updated_model = await db_conn.database_models.find_one({"id": model_id})
                return DatabaseModel(**updated_model)
                
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch from Civitai: {str(e)}")

def calculate_match_score(server_name: str, civitai_item: dict) -> float:
    """Calculate match score between server model name and Civitai item"""
    from difflib import SequenceMatcher
    
    server_name_clean = server_name.lower().strip()
    civitai_name = civitai_item.get("name", "").lower().strip()
    
    # Exact match
    if civitai_name == server_name_clean:
        return 1.0
    
    # Contains match
    if server_name_clean in civitai_name or civitai_name in server_name_clean:
        return 0.8
    
    # Check filenames
    for version in civitai_item.get("modelVersions", []):
        for file in version.get("files", []):
            filename = file.get("name", "").lower().strip()
            if filename == server_name_clean or server_name_clean in filename:
                return 0.9
    
    # Fuzzy matching
    similarity = SequenceMatcher(None, server_name_clean, civitai_name).ratio()
    return similarity * 0.6

def get_match_reason(server_name: str, civitai_item: dict) -> str:
    """Get the reason for the match"""
    server_name_clean = server_name.lower().strip()
    civitai_name = civitai_item.get("name", "").lower().strip()
    
    if civitai_name == server_name_clean:
        return "Exact name match"
    elif server_name_clean in civitai_name or civitai_name in server_name_clean:
        return "Partial name match"
    else:
        for version in civitai_item.get("modelVersions", []):
            for file in version.get("files", []):
                filename = file.get("name", "").lower().strip()
                if filename == server_name_clean or server_name_clean in filename:
                    return "Filename match"
        
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, server_name_clean, civitai_name).ratio()
        return f"Fuzzy match ({similarity:.2f})"

@api_router.post("/models/{model_id}/presets", response_model=ModelConfigurationPreset)
async def create_model_preset(
    model_id: str, 
    preset_data: ModelConfigurationPreset, 
    db_conn = Depends(get_database)
):
    """Create a configuration preset for a model"""
    model_data = await db_conn.database_models.find_one({"id": model_id})
    if not model_data:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Detect base model type
    base_model = detect_model_type(model_data["name"])
    
    # Update preset with references
    preset_data.model_id = model_id
    preset_data.base_model = base_model
    
    # Store preset in the model_presets collection
    preset_dict = preset_data.dict()
    preset_dict["created_at"] = datetime.now(timezone.utc)
    preset_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db_conn.model_presets.insert_one(preset_dict)
    
    return preset_data

@api_router.post("/models/presets/global/{base_model}", response_model=ModelConfigurationPreset)
async def create_global_preset(
    base_model: str, 
    preset_data: ModelConfigurationPreset, 
    db_conn = Depends(get_database)
):
    """Create a global configuration preset for all models of a specific base type"""
    # Validate base_model
    if base_model not in MODEL_DEFAULTS:
        raise HTTPException(status_code=400, detail=f"Invalid base model: {base_model}")
    
    # Update preset with base model info
    preset_data.base_model = base_model
    preset_data.is_global = True
    preset_data.model_id = None
    
    # Store preset in the model_presets collection
    preset_dict = preset_data.dict()
    preset_dict["created_at"] = datetime.now(timezone.utc)
    preset_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db_conn.model_presets.insert_one(preset_dict)
    
    return preset_data

@api_router.get("/models/presets/global/{base_model}", response_model=List[ModelConfigurationPreset])
async def get_global_presets(base_model: str, db_conn = Depends(get_database)):
    """Get all global presets for a specific base model type"""
    # Validate base_model
    if base_model not in MODEL_DEFAULTS:
        raise HTTPException(status_code=400, detail=f"Invalid base model: {base_model}")
    
    # Get global presets for this base model type
    global_presets = await db_conn.model_presets.find({
        "base_model": base_model,
        "is_global": True
    }).to_list(100)
    
    return [ModelConfigurationPreset(**preset) for preset in global_presets]

@api_router.put("/models/{model_id}/presets/{preset_id}", response_model=ModelConfigurationPreset)
async def update_model_preset(
    model_id: str,
    preset_id: str,
    preset_update: ModelConfigurationPreset,
    db_conn = Depends(get_database)
):
    """Update a configuration preset"""
    # Find the preset in the model_presets collection
    existing_preset = await db_conn.model_presets.find_one({
        "id": preset_id,
        "$or": [
            {"model_id": model_id},  # Model-specific preset
            {"is_global": True}      # Global preset (can be updated by anyone)
        ]
    })
    
    if not existing_preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    # Update the preset
    preset_update.updated_at = datetime.now(timezone.utc)
    
    await db_conn.model_presets.update_one(
        {"id": preset_id},
        {"$set": preset_update.dict(exclude_unset=True)}
    )
    
    # Return updated preset
    updated_preset = await db_conn.model_presets.find_one({"id": preset_id})
    return ModelConfigurationPreset(**updated_preset)

@api_router.delete("/models/{model_id}/presets/{preset_id}")
async def delete_model_preset(
    model_id: str,
    preset_id: str,
    db_conn = Depends(get_database)
):
    """Delete a configuration preset"""
    # Find the preset in the model_presets collection
    existing_preset = await db_conn.model_presets.find_one({
        "id": preset_id,
        "$or": [
            {"model_id": model_id},  # Model-specific preset
            {"is_global": True}      # Global preset (can be deleted by anyone)
        ]
    })
    
    if not existing_preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    # Don't allow deletion of default presets
    if existing_preset.get("id", "").startswith("default_"):
        raise HTTPException(status_code=403, detail="Cannot delete default presets")
    
    # Delete the preset
    await db_conn.model_presets.delete_one({"id": preset_id})
    
    return {"message": "Preset deleted successfully"}

@api_router.post("/servers/{server_id}/sync-models")
async def sync_server_models(server_id: str, db_conn = Depends(get_database)):
    """Sync models from a ComfyUI server to the database"""
    server_data = await db_conn.comfyui_servers.find_one({"id": server_id})
    if not server_data:
        raise ServerNotFoundError(server_id)
    
    server = ComfyUIServer(**server_data)
    client = ComfyUIClient(server)
    
    is_online = await client.check_connection()
    if not is_online:
        raise HTTPException(status_code=400, detail="Server is offline")
    
    models_data = await client.get_models()
    
    # Update active models tracking
    all_models = []
    
    # Prepare checkpoint models
    for checkpoint_name in models_data.get("checkpoints", []):
        all_models.append({
            "id": f"{server_id}_{checkpoint_name}",
            "name": checkpoint_name,
            "path": f"checkpoints/{checkpoint_name}",
            "type": "checkpoint",
            "size": None,  # Could be fetched if needed
            "metadata": {"server_id": server_id, "model_type": "checkpoint"}
        })
        await sync_single_model(checkpoint_name, "checkpoint", server_id, db_conn)
    
    # Prepare LoRA models
    for lora_name in models_data.get("loras", []):
        all_models.append({
            "id": f"{server_id}_{lora_name}",
            "name": lora_name,
            "path": f"loras/{lora_name}",
            "type": "lora",
            "size": None,
            "metadata": {"server_id": server_id, "model_type": "lora"}
        })
        await sync_single_model(lora_name, "lora", server_id, db_conn)
    
    # Update active models in the tracking system
    if active_models_service:
        await active_models_service.update_backend_models(
            backend_id=server_id,
            backend_name=server.name,
            backend_url=server.url,
            models_data=all_models
        )
        print(f"Tracked {len(all_models)} active models for backend {server.name}")
    
    return {"message": f"Synced {len(all_models)} models from server"}

async def sync_single_model(name: str, type: str, server_id: str, db_conn):
    """Sync a single model to the database"""
    existing = await db_conn.database_models.find_one({
        "name": name,
        "type": type
    })
    
    if existing:
        # Update server source and sync time
        await db_conn.database_models.update_one(
            {"id": existing["id"]},
            {"$set": {"server_source": server_id, "last_synced_at": datetime.now(timezone.utc)}}
        )
    else:
        # Create new model entry
        model = DatabaseModel(
            name=name,
            type=type,
            server_source=server_id,
            last_synced_at=datetime.now(timezone.utc)
        )
        await db_conn.database_models.insert_one(model.dict())

async def find_best_civitai_match_db(server_model_name: str, db_conn, fallback: bool = False) -> dict:
    """
    Enhanced matching algorithm using MongoDB database.
    
    Args:
        server_model_name: Name of the model from the ComfyUI server
        db_conn: Database connection
        fallback: If True, use lower threshold for matching
    
    Returns:
        Best matching dict or None if no match found
    """
    import re
    
    def clean_model_name(name: str) -> str:
        """Clean model name by removing extensions and common prefixes"""
        name = re.sub(r'\.(safetensors|ckpt|pth|pt)$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^(sd|stable-diffusion|sd-|sdxl|sd_xl)_?', '', name, flags=re.IGNORECASE)
        name = re.sub(r'_v\d+(-\d+)?(_lightning)?(_bakedvae)?', '', name, flags=re.IGNORECASE)
        name = re.sub(r'(-\d+)+$', '', name)
        name = re.sub(r'[-_]+', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip().lower()
    
    server_name_clean = clean_model_name(server_model_name)
    server_name_original = server_model_name.lower().strip()
    
    print(f"Searching database for: '{server_name_clean}'")  # Debug
    
    # Strategy 1: Exact name match
    exact_match = await db_conn.civitai_models.find_one({
        "name": server_name_original
    })
    if exact_match:
        print(f"Found exact match: {exact_match['name']}")  # Debug
        return exact_match
    
    # Strategy 2: Text search with high relevance
    text_search = await db_conn.civitai_models.find(
        {"$text": {"$search": server_name_clean}},
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).limit(5).to_list(length=5)
    
    if text_search:
        best_text_match = text_search[0]
        score = best_text_match.get("score", 0)
        print(f"Found text match: {best_text_match['name']} (score: {score})")  # Debug
        
        # Accept if score is reasonable
        if score > (1.0 if not fallback else 0.5):
            return best_text_match
    
    # Strategy 3: Regex matching for partial names
    if "realvisxl" in server_name_clean:
        regex_match = await db_conn.civitai_models.find_one({
            "name": {"$regex": r"RealVisXL.*Lightning", "$options": "i"}
        })
        if regex_match:
            print(f"Found regex match: {regex_match['name']}")  # Debug
            return regex_match
    
    # Strategy 4: Fallback to any partial match
    if fallback:
        partial_match = await db_conn.civitai_models.find_one({
            "name": {"$regex": server_name_clean.split()[0], "$options": "i"}
        })
        if partial_match:
            print(f"Found partial match: {partial_match['name']}")  # Debug
            return partial_match
    
    print("No matches found")  # Debug
    return None

async def get_model_profiles(civitai_model: dict, db_conn) -> list:
    """
    Get available profiles for a model based on direct links and base model.
    
    Args:
        civitai_model: The matched Civitai model
        db_conn: Database connection
    
    Returns:
        List of available profiles with priority levels
    """
    model_id = str(civitai_model.get("id"))
    base_model = civitai_model.get("baseModel")
    model_name = civitai_model.get("name", "")
    
    profiles = []
    
    # Priority 1: Direct model ID matches
    direct_profiles = await db_conn.model_profiles.find({
        "linked_model_ids": model_id
    }).to_list(length=10)
    
    for profile in direct_profiles:
        profile["priority_level"] = "exact"
        profile["priority_score"] = 100
        profiles.append(profile)
    
    # Priority 2: Base model matches
    if base_model:
        base_profiles = await db_conn.model_profiles.find({
            "linked_base_models": {"$regex": base_model, "$options": "i"}
        }).to_list(length=10)
        
        for profile in base_profiles:
            # Avoid duplicates
            if not any(p["_id"] == profile["_id"] for p in profiles):
                profile["priority_level"] = "base_model"
                profile["priority_score"] = 75
                profiles.append(profile)
    
    # Priority 3: Generic type-based matches
    model_type = civitai_model.get("type", "").lower()
    if model_type == "checkpoint":
        generic_profiles = await db_conn.model_profiles.find({
            "priority": "generic"
        }).to_list(length=5)
        
        for profile in generic_profiles:
            if not any(p["_id"] == profile["_id"] for p in profiles):
                profile["priority_level"] = "generic"
                profile["priority_score"] = 50
                profiles.append(profile)
    
    # Sort by priority score
    profiles.sort(key=lambda x: x["priority_score"], reverse=True)
    
    print(f"Found {len(profiles)} profiles for {model_name}")  # Debug
    for profile in profiles:
        print(f"  - {profile['name']} ({profile['priority_level']}, score: {profile['priority_score']})")  # Debug
    
    return profiles

# Project Management
@api_router.post("/projects", response_model=Project)
async def create_project(project_data: ProjectCreate, db_conn = Depends(get_database)):
    project_dict = project_data.dict()
    project = Project(**project_dict)
    await db_conn.projects.insert_one(project.dict())
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects(db_conn = Depends(get_database)):
    projects = await db_conn.projects.find().to_list(100)
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, db_conn = Depends(get_database)):
    from utils.errors import ProjectNotFoundError

    project_data = await db_conn.projects.find_one({"id": project_id})
    if not project_data:
        raise ProjectNotFoundError(project_id)
    return Project(**project_data)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_data: ProjectUpdate, db_conn = Depends(get_database)):
    from utils.errors import ProjectNotFoundError, ValidationError
    
    existing_project = await db_conn.projects.find_one({"id": project_id})
    if not existing_project:
        raise ProjectNotFoundError(project_id)
    
    update_data = project_data.dict(exclude_unset=True)
    if not update_data:
        raise ValidationError("No fields to update")
    
    # Map music_file to music_file_path for database storage
    if "music_file" in update_data:
        update_data["music_file_path"] = update_data.pop("music_file")
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db_conn.projects.update_one(
        {"id": project_id},
        {"$set": update_data}
    )
    
    updated_project = await db_conn.projects.find_one({"id": project_id})
    return Project(**updated_project)

@api_router.post("/projects/{project_id}/upload-music")
async def upload_music(project_id: str, file: UploadFile = File(...)):
    from utils.file_validator import file_validator
    from config import config as app_config
    from utils.errors import ProjectNotFoundError

    project_data = await db.projects.find_one({"id": project_id})
    if not project_data:
        raise ProjectNotFoundError(project_id)

    # Validate file
    await file_validator.validate_music_file(file)

    # Check disk space
    has_space, message = file_validator.check_disk_space(UPLOADS_DIR, app_config.MAX_MUSIC_SIZE)
    if not has_space:
        # Parse available/required from message if possible, otherwise use defaults
        raise InsufficientStorageError(app_config.MAX_MUSIC_SIZE / (1024 * 1024), 0)

    # Sanitize filename
    safe_filename = file_validator.sanitize_filename(file.filename)

    # Save the uploaded file
    file_path = UPLOADS_DIR / f"{project_id}_{safe_filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update project with music file path
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {"music_file_path": str(file_path), "updated_at": datetime.now(timezone.utc)}}
    )

    return {"message": "Music uploaded successfully", "file_path": str(file_path)}

@api_router.post("/upload-face-image")
async def upload_face_image(file: UploadFile = File(...)):
    """Upload face image for reactor/face swap"""
    from utils.file_validator import file_validator
    from config import config as app_config

    # Validate file
    await file_validator.validate_image_file(file)

    # Check disk space
    has_space, message = file_validator.check_disk_space(UPLOADS_DIR, app_config.MAX_IMAGE_SIZE)
    if not has_space:
        raise InsufficientStorageError(app_config.MAX_IMAGE_SIZE / (1024 * 1024), 0)

    # Create faces directory if it doesn't exist
    faces_dir = UPLOADS_DIR / "faces"
    faces_dir.mkdir(exist_ok=True)

    # Generate unique filename with sanitized extension
    safe_filename = file_validator.sanitize_filename(file.filename)
    file_extension = safe_filename.split('.')[-1] if '.' in safe_filename else 'jpg'
    unique_filename = f"face_{uuid.uuid4()}.{file_extension}"
    file_path = faces_dir / unique_filename

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return the URL that can be accessed by ComfyUI
    file_url = f"/uploads/faces/{unique_filename}"
    
    return {
        "message": "Face image uploaded successfully", 
        "file_url": file_url,
        "file_path": str(file_path)
    }

@api_router.post("/upload-character-images")
async def upload_character_images(
    face_image: UploadFile = File(None),
    full_body_image: UploadFile = File(None), 
    reference_images: List[UploadFile] = File(None)
):
    """Upload comprehensive character images for advanced generation"""
    from utils.file_validator import file_validator
    from config import config as app_config
    
    # Create character images directory
    character_dir = UPLOADS_DIR / "characters" / str(uuid.uuid4())
    character_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = {}
    
    # Process face image
    if face_image:
        await file_validator.validate_image_file(face_image)
        face_filename = f"face_{uuid.uuid4()}.jpg"
        face_path = character_dir / face_filename
        with open(face_path, "wb") as buffer:
            shutil.copyfileobj(face_image.file, buffer)
        uploaded_files["face_image"] = f"/uploads/characters/{character_dir.name}/{face_filename}"
    
    # Process full body image
    if full_body_image:
        await file_validator.validate_image_file(full_body_image)
        body_filename = f"full_body_{uuid.uuid4()}.jpg"
        body_path = character_dir / body_filename
        with open(body_path, "wb") as buffer:
            shutil.copyfileobj(full_body_image.file, buffer)
        uploaded_files["full_body_image"] = f"/uploads/characters/{character_dir.name}/{body_filename}"
    
    # Process reference images
    if reference_images:
        reference_urls = []
        for idx, ref_img in enumerate(reference_images):
            if ref_img:
                await file_validator.validate_image_file(ref_img)
                ref_filename = f"reference_{idx}_{uuid.uuid4()}.jpg"
                ref_path = character_dir / ref_filename
                with open(ref_path, "wb") as buffer:
                    shutil.copyfileobj(ref_img.file, buffer)
                reference_urls.append(f"/uploads/characters/{character_dir.name}/{ref_filename}")
        uploaded_files["reference_images"] = reference_urls
    
    return {
        "message": "Character images uploaded successfully",
        "files": uploaded_files,
        "character_dir": f"/uploads/characters/{character_dir.name}"
    }

@api_router.post("/generate-character-profiles")
async def generate_character_profiles(
    character_id: str,
    server_id: str,
    profile_type: str = "comprehensive",  # comprehensive, headshots, poses, expressions
    pose_style: str = "professional",     # professional, casual, action, formal
    controlnet_type: str = "openpose",    # openpose, depth, canny, scribble
    count: int = 4
):
    """Generate professional character profiles using advanced controlnets"""
    # Ensure database is connected
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Get character
    character_data = await db.characters.find_one({"id": character_id})
    if not character_data:
        raise ResourceNotFoundError("Character", character_id)
    
    character = Character(**character_data)
    
    # Get server
    server_data = await db.comfyui_servers.find_one({"id": server_id})
    if not server_data:
        raise ServerNotFoundError(server_id)
    
    server = ComfyUIServer(**server_data)
    client = ComfyUIClient(server)
    
    # Check if server is online
    if not await client.check_connection():
        raise ServiceUnavailableError("ComfyUI", "Server is offline")
    
    # Generate profiles based on type
    profiles = []
    prompts = get_profile_prompts(profile_type, pose_style, character)
    
    for i, prompt_data in enumerate(prompts[:count]):
        try:
            if controlnet_type == "openpose" and character.face_image:
                # Use OpenPose for consistent posing
                result_url = await client.generate_with_openpose(
                    prompt_data["prompt"],
                    character.face_image,
                    prompt_data.get("negative_prompt", ""),
                    prompt_data.get("model", "sd_xl_base_1.0.safetensors"),
                    character.generation_params
                )
            elif controlnet_type == "depth" and character.face_image:
                # Use Depth ControlNet for 3D consistency
                result_url = await client.generate_with_depth(
                    prompt_data["prompt"],
                    character.face_image,
                    prompt_data.get("negative_prompt", ""),
                    prompt_data.get("model", "sd_xl_base_1.0.safetensors"),
                    character.generation_params
                )
            elif character.generation_method == "ip_adapter" and character.reference_images:
                # Use IP-Adapter for facial consistency
                result_url = await client.generate_character_with_ip_adapter(
                    prompt_data["prompt"],
                    character.reference_images[0],
                    prompt_data.get("model", "sd_xl_base_1.0.safetensors"),
                    character.generation_params
                )
            else:
                # Standard generation
                result_url = await client.generate_image(
                    prompt_data["prompt"],
                    prompt_data.get("negative_prompt", ""),
                    prompt_data.get("model", "sd_xl_base_1.0.safetensors"),
                    character.generation_params,
                    []
                )
            
            if result_url:
                profiles.append({
                    "url": result_url,
                    "prompt": prompt_data["prompt"],
                    "type": prompt_data.get("type", "standard"),
                    "description": prompt_data.get("description", "")
                })
                
        except Exception as e:
            logging.error(f"Error generating profile {i}: {e}")
            continue
    
    return {
        "character_id": character_id,
        "character_name": character.name,
        "profile_type": profile_type,
        "controlnet_type": controlnet_type,
        "profiles": profiles,
        "total_generated": len(profiles)
    }

def get_profile_prompts(profile_type: str, pose_style: str, character: Character) -> List[Dict]:
    """Get professional prompts for character profile generation"""
    base_name = character.name
    base_description = character.description or f"professional portrait of {base_name}"
    trigger_words = character.trigger_words or ""
    
    prompts = []
    
    if profile_type == "comprehensive":
        if pose_style == "professional":
            prompts = [
                {
                    "prompt": f"professional headshot of {base_name}, {base_description}, business attire, studio lighting, high quality, detailed face, {trigger_words}",
                    "type": "headshot",
                    "description": "Professional Headshot"
                },
                {
                    "prompt": f"three-quarter body shot of {base_name}, {base_description}, professional pose, office background, confident expression, {trigger_words}",
                    "type": "three_quarter",
                    "description": "Three-Quarter View"
                },
                {
                    "prompt": f"full body portrait of {base_name}, {base_description}, standing pose, professional attire, neutral background, full height visible, {trigger_words}",
                    "type": "full_body",
                    "description": "Full Body Portrait"
                },
                {
                    "prompt": f"action pose of {base_name}, {base_description}, dynamic movement, professional setting, engaged expression, {trigger_words}",
                    "type": "action",
                    "description": "Action Pose"
                }
            ]
        elif pose_style == "casual":
            prompts = [
                {
                    "prompt": f"casual headshot of {base_name}, {base_description}, relaxed expression, natural lighting, everyday attire, {trigger_words}",
                    "type": "casual_headshot",
                    "description": "Casual Headshot"
                },
                {
                    "prompt": f"lifestyle pose of {base_name}, {base_description}, casual setting, relaxed stance, natural expression, {trigger_words}",
                    "type": "lifestyle",
                    "description": "Lifestyle Pose"
                }
            ]
    elif profile_type == "headshots":
        prompts = [
            {
                "prompt": f"front facing headshot of {base_name}, {base_description}, direct gaze, professional lighting, detailed features, {trigger_words}",
                "type": "front_headshot",
                "description": "Front View"
            },
            {
                "prompt": f"profile view of {base_name}, {base_description}, side lighting, facial structure visible, {trigger_words}",
                "type": "profile_headshot",
                "description": "Profile View"
            },
            {
                "prompt": f"three-quarter headshot of {base_name}, {base_description}, angled view, dimensional lighting, {trigger_words}",
                "type": "three_quarter_headshot",
                "description": "Three-Quarter View"
            }
        ]
    elif profile_type == "expressions":
        expressions = ["smiling", "serious", "thoughtful", "confident"]
        for expr in expressions:
            prompts.append({
                "prompt": f"{expr} portrait of {base_name}, {base_description}, {expr} expression, emotional depth, {trigger_words}",
                "type": f"expression_{expr}",
                "description": expr.title()
            })
    
    return prompts

# Scene Management
@api_router.post("/scenes", response_model=Scene)
async def create_scene(scene_data: SceneCreate):
    scene_dict = scene_data.dict()
    scene = Scene(**scene_dict)
    await db.scenes.insert_one(scene.dict())
    return scene

@api_router.get("/projects/{project_id}/timeline")
async def get_project_timeline(project_id: str):
    """Get complete project timeline with all scenes and clips for the storyboard."""
    try:
        # Get project
        project_data = await db.projects.find_one({"id": project_id})
        if not project_data:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Remove MongoDB _id field
        if "_id" in project_data:
            del project_data["_id"]

        # Get all scenes for this project
        scenes = await db.scenes.find({"project_id": project_id}).sort("order").to_list(100)

        # For each scene, get its clips
        timeline_scenes = []
        for scene in scenes:
            # Remove MongoDB _id field
            if "_id" in scene:
                del scene["_id"]

            clips = await db.clips.find({"scene_id": scene["id"]}).sort("order").to_list(100)

            # Remove MongoDB _id field from clips
            for clip in clips:
                if "_id" in clip:
                    del clip["_id"]

            scene["clips"] = clips
            timeline_scenes.append(scene)

        return {
            "project": project_data,
            "scenes": timeline_scenes
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}/scenes", response_model=List[Scene])
async def get_project_scenes(project_id: str):
    scenes = await db.scenes.find({"project_id": project_id}).sort("order").to_list(100)
    return [Scene(**scene) for scene in scenes]

@api_router.get("/projects/{project_id}/clips", response_model=List[Clip])
async def get_project_clips(project_id: str, db_conn = Depends(get_database)):
    clips = await db_conn.clips.find({"project_id": project_id}).sort("order").to_list(100)
    return [Clip(**clip) for clip in clips]

@api_router.get("/scenes/{scene_id}", response_model=Scene)
async def get_scene(scene_id: str):
    scene_data = await db.scenes.find_one({"id": scene_id})
    if not scene_data:
        raise SceneNotFoundError(scene_id)
    return Scene(**scene_data)

@api_router.put("/scenes/{scene_id}")
async def update_scene(scene_id: str, scene_update: SceneUpdate):
    update_data = {k: v for k, v in scene_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.scenes.update_one(
        {"id": scene_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise SceneNotFoundError(scene_id)

    return {"message": "Scene updated successfully"}

@api_router.post("/scenes/{scene_id}/create-alternate", response_model=Scene)
async def create_scene_alternate(scene_id: str):
    """Create an alternate version of a scene"""
    # Get the original scene
    original_scene = await db.scenes.find_one({"id": scene_id})
    if not original_scene:
        raise SceneNotFoundError(scene_id)

    # Determine parent scene ID (if this is already an alternate, use its parent)
    parent_id = original_scene.get("parent_scene_id") or scene_id

    # Find the highest alternate number for this parent
    existing_alternates = await db.scenes.find({
        "$or": [
            {"parent_scene_id": parent_id},
            {"id": parent_id, "is_alternate": False}
        ]
    }).to_list(100)

    max_alternate = 0
    for alt in existing_alternates:
        alt_num = alt.get("alternate_number", 0)
        if alt_num > max_alternate:
            max_alternate = alt_num

    new_alternate_number = max_alternate + 1

    # Create new scene as alternate
    new_scene_dict = {
        "id": str(uuid.uuid4()),
        "project_id": original_scene["project_id"],
        "name": f"{original_scene['name']} A{new_alternate_number}",
        "description": original_scene.get("description", ""),
        "lyrics": original_scene.get("lyrics", ""),
        "order": original_scene.get("order", 0),
        "parent_scene_id": parent_id,
        "alternate_number": new_alternate_number,
        "is_alternate": True,
        "duration": original_scene.get("duration", 0.0),
        "timeline_start": original_scene.get("timeline_start", 0.0),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    new_scene = Scene(**new_scene_dict)
    await db.scenes.insert_one(new_scene.dict())

    return new_scene

# Clip Management
@api_router.post("/clips", response_model=Clip)
async def create_clip(clip_data: ClipCreate):
    clip_dict = clip_data.dict()
    clip = Clip(**clip_dict)
    await db.clips.insert_one(clip.dict())
    return clip

@api_router.get("/scenes/{scene_id}/clips", response_model=List[Clip])
async def get_scene_clips(scene_id: str):
    clips = await db.clips.find({"scene_id": scene_id}).sort("order").to_list(100)
    return [Clip(**clip) for clip in clips]

@api_router.get("/clips/{clip_id}", response_model=Clip)
async def get_clip(clip_id: str):
    clip_data = await db.clips.find_one({"id": clip_id})
    if not clip_data:
        raise ClipNotFoundError(clip_id)
    return Clip(**clip_data)

@api_router.put("/clips/{clip_id}", response_model=Clip)
async def update_clip(clip_id: str, clip_update: ClipUpdate):
    """Update clip with partial or full updates"""
    # Check if clip exists
    clip_data = await db.clips.find_one({"id": clip_id})
    if not clip_data:
        raise ClipNotFoundError(clip_id)

    # Build update dict with only provided fields
    update_data = {k: v for k, v in clip_update.dict(exclude_unset=True).items() if v is not None}

    if not update_data:
        raise ValidationError("No valid fields provided for update")

    # Add updated timestamp
    update_data["updated_at"] = datetime.now(timezone.utc)

    # Update clip
    result = await db.clips.update_one(
        {"id": clip_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise ClipNotFoundError(clip_id)

    # Return updated clip
    updated_clip_data = await db.clips.find_one({"id": clip_id})
    return Clip(**updated_clip_data)

@api_router.put("/clips/{clip_id}/timeline-position")
async def update_clip_timeline_position(
    clip_id: str,
    update_data: TimelinePositionUpdate,
    check_overlap: bool = True  # Query param to optionally disable overlap check
):
    """Update clip timeline position with validation"""
    from utils.timeline_validator import timeline_validator

    # Get the clip being moved
    clip_data = await db.clips.find_one({"id": clip_id})
    if not clip_data:
        raise ClipNotFoundError(clip_id)

    clip = Clip(**clip_data)
    new_position = update_data.position

    # Get all clips in the same scene
    all_clips_data = await db.clips.find({"scene_id": clip.scene_id}).to_list(1000)
    all_clips = [Clip(**c) for c in all_clips_data]

    # Check for overlaps if enabled
    if check_overlap:
        is_valid, error_msg = timeline_validator.check_overlap(
            clip_id=clip_id,
            new_position=new_position,
            clip_length=clip.length,
            other_clips=all_clips
        )

        if not is_valid:
            # Suggest alternative position
            suggested_pos = timeline_validator.find_next_available_position(
                clip_length=clip.length,
                other_clips=[c for c in all_clips if c.id != clip_id],
                preferred_position=new_position
            )

            raise HTTPException(
                status_code=409,  # Conflict
                detail={
                    "error": error_msg,
                    "suggested_position": suggested_pos,
                    "clip_id": clip_id,
                    "requested_position": new_position
                }
            )

    # Update position
    result = await db.clips.update_one(
        {"id": clip_id},
        {"$set": {
            "timeline_position": new_position,
            "updated_at": datetime.now(timezone.utc)
        }}
    )

    # Get timeline summary
    updated_clips_data = await db.clips.find({"scene_id": clip.scene_id}).to_list(1000)
    updated_clips = [Clip(**c) for c in updated_clips_data]
    summary = timeline_validator.get_timeline_summary(updated_clips)

    return {
        "message": "Timeline position updated",
        "clip_id": clip_id,
        "new_position": new_position,
        "timeline_summary": summary
    }

@api_router.post("/clips/{clip_id}/create-alternate", response_model=Clip)
async def create_clip_alternate(clip_id: str):
    """Create an alternate version of a clip"""
    # Get the original clip
    original_clip = await db.clips.find_one({"id": clip_id})
    if not original_clip:
        raise ClipNotFoundError(clip_id)

    # Determine parent clip ID (if this is already an alternate, use its parent)
    parent_id = original_clip.get("parent_clip_id") or clip_id

    # Find the highest alternate number for this parent
    existing_alternates = await db.clips.find({
        "$or": [
            {"parent_clip_id": parent_id},
            {"id": parent_id, "is_alternate": False}
        ]
    }).to_list(100)

    max_alternate = 0
    for alt in existing_alternates:
        alt_num = alt.get("alternate_number", 0)
        if alt_num > max_alternate:
            max_alternate = alt_num

    new_alternate_number = max_alternate + 1

    # Create new clip as alternate
    new_clip_dict = {
        "id": str(uuid.uuid4()),
        "scene_id": original_clip["scene_id"],
        "name": f"{original_clip['name']} A{new_alternate_number}",
        "lyrics": original_clip.get("lyrics", ""),
        "length": original_clip.get("length", 5.0),
        "timeline_position": original_clip.get("timeline_position", 0.0),
        "order": original_clip.get("order", 0),
        "parent_clip_id": parent_id,
        "alternate_number": new_alternate_number,
        "is_alternate": True,
        "image_prompt": original_clip.get("image_prompt", ""),
        "video_prompt": original_clip.get("video_prompt", ""),
        "generated_images": [],
        "generated_videos": [],
        "selected_image_id": None,
        "selected_video_id": None,
        "character_id": original_clip.get("character_id"),
        "versions": [],
        "active_version": 1,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    new_clip = Clip(**new_clip_dict)
    await db.clips.insert_one(new_clip.dict())

    return new_clip

@api_router.get("/scenes/{scene_id}/timeline-analysis")
async def analyze_scene_timeline(scene_id: str):
    """
    Analyze timeline for a scene - detect overlaps, gaps, and provide suggestions
    """
    from utils.timeline_validator import timeline_validator

    # Get scene
    scene_data = await db.scenes.find_one({"id": scene_id})
    if not scene_data:
        raise SceneNotFoundError(scene_id)

    # Get all clips in scene
    clips_data = await db.clips.find({"scene_id": scene_id}).to_list(1000)
    clips = [Clip(**c) for c in clips_data]

    # Get timeline summary
    summary = timeline_validator.get_timeline_summary(clips)

    # Detect all overlaps
    overlaps = []
    for i, clip1 in enumerate(clips):
        for clip2 in clips[i+1:]:
            is_valid, error_msg = timeline_validator.check_overlap(
                clip_id=clip1.id,
                new_position=clip1.timeline_position,
                clip_length=clip1.length,
                other_clips=[clip2]
            )
            if not is_valid:
                overlaps.append({
                    "clip1_id": clip1.id,
                    "clip1_name": clip1.name,
                    "clip2_id": clip2.id,
                    "clip2_name": clip2.name,
                    "error": error_msg
                })

    # Detect gaps
    gaps = []
    sorted_clips = sorted(clips, key=lambda c: c.timeline_position)
    for i in range(len(sorted_clips) - 1):
        current_end = sorted_clips[i].timeline_position + sorted_clips[i].length
        next_start = sorted_clips[i+1].timeline_position
        gap_size = next_start - current_end

        if gap_size > 0.1:  # Gap larger than 100ms
            gaps.append({
                "after_clip_id": sorted_clips[i].id,
                "after_clip_name": sorted_clips[i].name,
                "before_clip_id": sorted_clips[i+1].id,
                "before_clip_name": sorted_clips[i+1].name,
                "gap_start": current_end,
                "gap_end": next_start,
                "gap_duration": gap_size
            })

    return {
        "scene_id": scene_id,
        "summary": summary,
        "overlaps": overlaps,
        "gaps": gaps,
        "has_issues": len(overlaps) > 0,
        "total_clips": len(clips)
    }

@api_router.put("/clips/{clip_id}/prompts")
async def update_clip_prompts(clip_id: str, image_prompt: str = "", video_prompt: str = ""):
    result = await db.clips.update_one(
        {"id": clip_id},
        {"$set": {
            "image_prompt": image_prompt,
            "video_prompt": video_prompt,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    if result.matched_count == 0:
        raise ClipNotFoundError(clip_id)
    return {"message": "Prompts updated successfully"}

@api_router.get("/clips/{clip_id}/gallery")
async def get_clip_gallery(clip_id: str):
    clip_data = await db.clips.find_one({"id": clip_id})
    if not clip_data:
        raise ClipNotFoundError(clip_id)
    
    clip = Clip(**clip_data)
    return {
        "images": clip.generated_images,
        "videos": clip.generated_videos,
        "selected_image_id": clip.selected_image_id,
        "selected_video_id": clip.selected_video_id
    }

@api_router.put("/clips/{clip_id}/select-content")
async def select_clip_content(clip_id: str, content_id: str, content_type: str):
    if content_type not in ["image", "video"]:
        raise ValidationError("Invalid content type")
    
    # Update the selected content
    update_field = "selected_image_id" if content_type == "image" else "selected_video_id"
    
    result = await db.clips.update_one(
        {"id": clip_id},
        {"$set": {
            update_field: content_id,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.matched_count == 0:
        raise ClipNotFoundError(clip_id)
    
    # Also update the is_selected flag for all content of this type
    field_name = "generated_images" if content_type == "image" else "generated_videos"
    clip_data = await db.clips.find_one({"id": clip_id})
    if clip_data:
        content_list = clip_data.get(field_name, [])
        for content in content_list:
            content["is_selected"] = (content["id"] == content_id)
        
        await db.clips.update_one(
            {"id": clip_id},
            {"$set": {field_name: content_list}}
        )
    
    return {"message": f"Selected {content_type} updated successfully"}

# Generation Pool Management
@api_router.post("/pool", response_model=GenerationPool)
async def create_pool_item(pool_data: GenerationPoolCreate):
    """Add generated content to the pool"""
    pool_dict = pool_data.dict()
    pool_item = GenerationPool(**pool_dict)
    await db.generation_pool.insert_one(pool_item.dict())
    return pool_item

@api_router.get("/pool/{project_id}", response_model=List[GenerationPool])
async def get_project_pool(project_id: str, content_type: Optional[str] = None, tags: Optional[str] = None):
    """Get all pool items for a project with optional filtering"""
    query = {"project_id": project_id}

    if content_type:
        query["content_type"] = content_type

    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query["tags"] = {"$in": tag_list}

    pool_items = await db.generation_pool.find(query).sort("created_at", -1).to_list(1000)
    return [GenerationPool(**item) for item in pool_items]

@api_router.get("/pool/item/{item_id}", response_model=GenerationPool)
async def get_pool_item(item_id: str):
    """Get a specific pool item"""
    pool_data = await db.generation_pool.find_one({"id": item_id})
    if not pool_data:
        raise HTTPException(status_code=404, detail=f"Pool item {item_id} not found")
    return GenerationPool(**pool_data)

@api_router.put("/pool/item/{item_id}")
async def update_pool_item(item_id: str, name: Optional[str] = None, description: Optional[str] = None, tags: Optional[List[str]] = None):
    """Update pool item metadata"""
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if tags is not None:
        update_data["tags"] = tags

    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    result = await db.generation_pool.update_one(
        {"id": item_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Pool item {item_id} not found")

    return {"message": "Pool item updated successfully"}

@api_router.delete("/pool/item/{item_id}")
async def delete_pool_item(item_id: str):
    """Delete a pool item"""
    result = await db.generation_pool.delete_one({"id": item_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Pool item {item_id} not found")

    return {"message": "Pool item deleted successfully"}

@api_router.post("/pool/item/{item_id}/apply-to-clip/{clip_id}")
async def apply_pool_item_to_clip(item_id: str, clip_id: str):
    """Apply a pool item's media to a clip"""
    # Get pool item
    pool_data = await db.generation_pool.find_one({"id": item_id})
    if not pool_data:
        raise HTTPException(status_code=404, detail=f"Pool item {item_id} not found")

    pool_item = GenerationPool(**pool_data)

    # Get clip
    clip_data = await db.clips.find_one({"id": clip_id})
    if not clip_data:
        raise ClipNotFoundError(clip_id)

    # Add the pool item's media to the clip's generated content
    if pool_item.content_type == "image":
        # Add to generated_images
        new_image = {
            "id": str(uuid.uuid4()),
            "url": pool_item.media_url,
            "thumbnail_url": pool_item.thumbnail_url or pool_item.media_url,
            "prompt": pool_item.generation_params.get("prompt", "") if pool_item.generation_params else "",
            "seed": pool_item.generation_params.get("seed") if pool_item.generation_params else None,
            "model": pool_item.generation_params.get("model", "unknown") if pool_item.generation_params else "unknown",
            "is_selected": False,
            "created_at": datetime.now(timezone.utc)
        }

        result = await db.clips.update_one(
            {"id": clip_id},
            {"$push": {"generated_images": new_image}}
        )
    elif pool_item.content_type == "video":
        # Add to generated_videos
        new_video = {
            "id": str(uuid.uuid4()),
            "url": pool_item.media_url,
            "thumbnail_url": pool_item.thumbnail_url or pool_item.media_url,
            "prompt": pool_item.generation_params.get("prompt", "") if pool_item.generation_params else "",
            "seed": pool_item.generation_params.get("seed") if pool_item.generation_params else None,
            "model": pool_item.generation_params.get("model", "unknown") if pool_item.generation_params else "unknown",
            "is_selected": False,
            "created_at": datetime.now(timezone.utc)
        }

        result = await db.clips.update_one(
            {"id": clip_id},
            {"$push": {"generated_videos": new_video}}
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {pool_item.content_type}")

    return {"message": f"Pool item applied to clip successfully", "content_id": new_image["id"] if pool_item.content_type == "image" else new_video["id"]}

@api_router.get("/models/defaults/{model_name}")
async def get_model_defaults_api(model_name: str):
    """Get intelligent defaults for a specific model"""
    model_type = detect_model_type(model_name)
    defaults = get_model_defaults(model_name)
    return {
        "model_name": model_name,
        "detected_type": model_type,
        "defaults": defaults
    }

@api_router.get("/comfyui/servers/{server_id}/workflows")
async def get_server_workflows(server_id: str, db_conn = Depends(get_database)):
    """Get available workflows from ComfyUI server"""
    server_data = await db_conn.comfyui_servers.find_one({"id": server_id})
    if not server_data:
        raise ServerNotFoundError(server_id)
    
    server = ComfyUIServer(**server_data)
    client = ComfyUIClient(server)
    
    # For standard ComfyUI servers, try to get workflows from the /workflows endpoint
    if server.server_type == "standard":
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{server.url}/workflows") as response:
                    if response.status == 200:
                        workflows = await response.json()
                        return {"workflows": workflows}
        except:
            pass
    
    # Return empty list if no workflows found or server is offline
    return {"workflows": []}

# Model Presets API
@api_router.get("/models/presets/{model_name}")
async def get_model_presets(model_name: str, db_conn = Depends(get_database)):
    """Get all available presets for a model (model-specific + base model presets + defaults)"""
    # Detect base model type
    base_model = detect_model_type(model_name)
    
    # First try to find the model in the database
    model_data = await db_conn.database_models.find_one({"name": model_name})
    
    presets = {}
    
    # Get default presets from MODEL_DEFAULTS
    model_defaults = MODEL_DEFAULTS.get(base_model, MODEL_DEFAULTS.get("sdxl", {}))
    for preset_name, preset_config in model_defaults.items():
        if isinstance(preset_config, dict) and preset_name in ["fast", "quality"]:
            presets[preset_name] = {
                "id": f"default_{base_model}_{preset_name}",
                "name": f"Default {preset_name.title()}",
                "description": f"Default {preset_name} preset for {base_model} models",
                "cfg_scale": preset_config.get("cfg", 7.0),
                "steps": preset_config.get("steps", 20),
                "sampler": preset_config.get("sampler", "euler"),
                "scheduler": preset_config.get("scheduler", "normal"),
                "resolution_width": preset_config.get("width", 512),
                "resolution_height": preset_config.get("height", 512),
                "additional_params": {k: v for k, v in preset_config.items() 
                                  if k not in ["cfg", "steps", "sampler", "scheduler", "width", "height"]},
                "is_default": True
            }
    
    # If model exists in database, get custom presets
    if model_data:
        # Get model-specific presets
        model_presets = await db_conn.model_presets.find({"model_id": model_data["id"]}).to_list(100)
        for preset in model_presets:
            presets[preset["id"]] = {**preset, "is_model_specific": True}
        
        # Get global presets for this base model type
        global_presets = await db_conn.model_presets.find({
            "base_model": base_model,
            "is_global": True
        }).to_list(100)
        for preset in global_presets:
            presets[preset["id"]] = {**preset, "is_global": True}
    
    return {
        "model_name": model_name,
        "base_model": base_model,
        "presets": list(presets.values())
    }

@api_router.get("/models/parameters/{model_name}")
async def get_model_parameters(model_name: str, preset: str = "fast"):
    """Get specific parameters for a model and preset"""
    model_type = detect_model_type(model_name)
    model_config = MODEL_DEFAULTS.get(model_type)
    
    if not model_config:
        raise ResourceNotFoundError("Model", model)
    
    preset_config = model_config.get(preset)
    if not preset_config:
        # Return fast preset as fallback
        preset_config = model_config.get("fast", model_config.get("quality", {}))
    
    return {
        "model_name": model_name,
        "model_type": model_type,
        "preset": preset,
        "parameters": preset_config
    }

@api_router.get("/models/types")
async def get_supported_model_types():
    """Get all supported model types and their available presets"""
    result = {}
    for model_type, config in MODEL_DEFAULTS.items():
        result[model_type] = {
            "presets": list(config.keys()),
            "display_name": model_type.replace("_", " ").title()
        }
    
    return {"supported_models": result}

# Generation
@api_router.post("/generate")
async def generate_content(request: GenerationRequest):
    try:
        logging.info(f"Generation request: {request}")
        
        # Get server info
        server_data = await db.comfyui_servers.find_one({"id": request.server_id})
        if not server_data:
            raise ServerNotFoundError(server_id)
        
        logging.info(f"Found server: {server_data}")
        server = ComfyUIServer(**server_data)
        client = ComfyUIClient(server)
        
    except Exception as e:
        logging.error(f"Error in generate_content setup: {str(e)}")
        raise ServerError(f"Setup error: {str(e)}")
    
    # Check if server is online
    if not await client.check_connection():
        raise ServiceUnavailableError("ComfyUI", "Server is offline")
    
    try:
        # Generate content
        if request.generation_type == "image":
            result_url = await client.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt or "",
            model=request.model,
            params=request.params or {},
            loras=request.loras or []
            )
            
            if result_url:
                from services.gallery_manager import gallery_manager

                # Get server info for metadata
                server = ComfyUIServer(**server_data)

                # Detect model type and get defaults
                model_type = detect_model_type(request.model or "unknown")

                # Create new generated content
                new_content = gallery_manager.create_generated_content(
                    content_type="image",
                    url=result_url,
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt or "",
                    server_id=request.server_id,
                    server_name=server.name,
                    model_name=request.model or "unknown",
                    model_type=model_type,
                    generation_params=request.params or {}
                )

                # Add to clip gallery
                return await gallery_manager.add_generated_content(
                    db=db,
                    clip_id=request.clip_id,
                    new_content=new_content,
                    content_type="image"
                )
            
            raise GenerationError("image", "No result URL returned from server")
        
        elif request.generation_type == "video":
            # Video generation implementation
            result_url = await client.generate_video(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt or "",
                model=request.model,
                params=request.params or {},
                loras=request.loras or []
            )
            
            if result_url:
                from services.gallery_manager import gallery_manager

                # Get server info for metadata
                server = ComfyUIServer(**server_data)

                # Detect model type and get defaults
                model_type = detect_model_type(request.model or "unknown")

                # Create new generated content
                new_content = gallery_manager.create_generated_content(
                    content_type="video",
                    url=result_url,
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt or "",
                    server_id=request.server_id,
                    server_name=server.name,
                    model_name=request.model or "unknown",
                    model_type=model_type,
                    generation_params=request.params or {}
                )

                # Add to clip gallery
                return await gallery_manager.add_generated_content(
                    db=db,
                    clip_id=request.clip_id,
                    new_content=new_content,
                    content_type="video"
                )
            
            raise GenerationError("video", "No result URL returned from server")
        
        else:
            raise ValidationError("Invalid generation type. Must be 'image' or 'video'")
            
    except Exception as e:
        logging.error(f"Error in generation: {str(e)}")
        raise ServerError(f"Generation failed: {str(e)}")

# Batch Generation
@api_router.post("/generate/batch")
async def generate_batch(
    clip_ids: List[str],
    server_id: str,
    generation_type: str,
    prompt: Optional[str] = None,
    negative_prompt: Optional[str] = "",
    model: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    loras: Optional[List[Dict[str, Any]]] = None
):
    """Generate content for multiple clips simultaneously"""
    from services.batch_generator import batch_generator

    if not clip_ids:
        raise ValidationError("No clip IDs provided")

    if generation_type not in ["image", "video"]:
        raise ValidationError("Invalid generation type. Must be 'image' or 'video'")

    # Build generation parameters
    generation_params = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "model": model,
        "generation_params": params or {},
        "loras": loras or []
    }

    # Start batch generation
    batch_info = await batch_generator.generate_batch(
        db=db,
        clip_ids=clip_ids,
        server_id=server_id,
        generation_type=generation_type,
        params=generation_params
    )

    return batch_info

@api_router.get("/generate/batch/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status of a batch generation job"""
    from services.batch_generator import batch_generator

    batch_status = batch_generator.get_batch_status(batch_id)
    if "error" in batch_status and batch_status["error"] == "Batch not found":
        raise ResourceNotFoundError("Batch", batch_id)

    return batch_status

@api_router.get("/generate/batches")
async def list_batches():
    """List all batch generation jobs"""
    from services.batch_generator import batch_generator
    return {"batches": batch_generator.list_batches()}

# Style Templates
@api_router.post("/style-templates", response_model=StyleTemplate)
async def create_style_template(template_data: StyleTemplateCreate):
    """Create a new style template"""
    template_dict = template_data.dict()
    template = StyleTemplate(**template_dict)

    await db.style_templates.insert_one(template.dict())
    return template

@api_router.get("/style-templates", response_model=List[StyleTemplate])
async def list_style_templates(category: Optional[str] = None, public_only: bool = False):
    """List all style templates"""
    query = {}
    if category:
        query["category"] = category
    if public_only:
        query["is_public"] = True

    templates = await db.style_templates.find(query).sort("use_count", -1).to_list(100)
    return [StyleTemplate(**t) for t in templates]

@api_router.get("/style-templates/{template_id}", response_model=StyleTemplate)
async def get_style_template(template_id: str):
    """Get a specific style template"""
    template_data = await db.style_templates.find_one({"id": template_id})
    if not template_data:
        raise ResourceNotFoundError("Template", template_id)
    return StyleTemplate(**template_data)

@api_router.put("/style-templates/{template_id}", response_model=StyleTemplate)
async def update_style_template(template_id: str, template_data: StyleTemplateCreate):
    """Update a style template"""
    update_dict = template_data.dict()
    update_dict["updated_at"] = datetime.now(timezone.utc)

    result = await db.style_templates.update_one(
        {"id": template_id},
        {"$set": update_dict}
    )

    if result.matched_count == 0:
        raise ResourceNotFoundError("Template", template_id)

    updated_template = await db.style_templates.find_one({"id": template_id})
    return StyleTemplate(**updated_template)

@api_router.delete("/style-templates/{template_id}")
async def delete_style_template(template_id: str):
    """Delete a style template"""
    result = await db.style_templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise ResourceNotFoundError("Template", template_id)
    return {"message": "Template deleted successfully"}

@api_router.post("/style-templates/{template_id}/use")
async def use_style_template(template_id: str):
    """Increment use count for a template"""
    result = await db.style_templates.update_one(
        {"id": template_id},
        {"$inc": {"use_count": 1}}
    )
    if result.matched_count == 0:
        raise ResourceNotFoundError("Template", template_id)
    return {"message": "Use count incremented"}

# Export Endpoints
@api_router.get("/projects/{project_id}/export/fcpxml")
async def export_final_cut_pro(project_id: str):
    """Export project to Final Cut Pro XML format"""
    from services.export_service import export_service
    from fastapi.responses import Response

    try:
        xml_content = await export_service.export_final_cut_pro(db, project_id)
        return Response(
            content=xml_content,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename=project_{project_id}.fcpxml"}
        )
    except ValueError as e:
        # Export service raises ValueError for "Project not found"
        raise ProjectNotFoundError(project_id)

@api_router.get("/projects/{project_id}/export/edl")
async def export_premiere_edl(project_id: str):
    """Export project to Adobe Premiere EDL format"""
    from services.export_service import export_service
    from fastapi.responses import Response

    try:
        edl_content = await export_service.export_premiere_edl(db, project_id)
        return Response(
            content=edl_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=project_{project_id}.edl"}
        )
    except ValueError as e:
        # Export service raises ValueError for "Project not found"
        raise ProjectNotFoundError(project_id)

@api_router.get("/projects/{project_id}/export/resolve")
async def export_davinci_resolve(project_id: str):
    """Export project to DaVinci Resolve format"""
    from services.export_service import export_service
    from fastapi.responses import Response

    try:
        xml_content = await export_service.export_davinci_resolve(db, project_id)
        return Response(
            content=xml_content,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename=project_{project_id}_resolve.xml"}
        )
    except ValueError as e:
        # Export service raises ValueError for "Project not found"
        raise ProjectNotFoundError(project_id)

@api_router.get("/projects/{project_id}/export/json")
async def export_json(project_id: str):
    """Export complete project data to JSON"""
    from services.export_service import export_service

    try:
        json_data = await export_service.export_json(db, project_id)
        return json_data
    except ValueError as e:
        # Export service raises ValueError for "Project not found"
        raise ProjectNotFoundError(project_id)

# Character Manager Endpoints
@api_router.post("/characters", response_model=Character)
async def create_character(character_data: CharacterCreate):
    """Create a new character for consistent generation"""
    character = Character(**character_data.dict())
    await db.characters.insert_one(character.dict())
    logger.info(f"Created character: {character.id} for project: {character.project_id}")
    return character

@api_router.get("/characters", response_model=List[Character])
async def list_characters(project_id: Optional[str] = None):
    """List all characters, optionally filtered by project"""
    query = {"project_id": project_id} if project_id else {}
    characters = await db.characters.find(query).to_list(100)
    return [Character(**char) for char in characters]

@api_router.get("/characters/{character_id}", response_model=Character)
async def get_character(character_id: str):
    """Get a specific character"""
    character_data = await db.characters.find_one({"id": character_id})
    if not character_data:
        raise ResourceNotFoundError("Character", character_id)
    return Character(**character_data)

@api_router.put("/characters/{character_id}", response_model=Character)
async def update_character(character_id: str, character_data: CharacterCreate):
    """Update a character"""
    update_dict = character_data.dict()
    update_dict["updated_at"] = datetime.now(timezone.utc)

    result = await db.characters.update_one(
        {"id": character_id},
        {"$set": update_dict}
    )

    if result.matched_count == 0:
        raise ResourceNotFoundError("Character", character_id)

    updated_character = await db.characters.find_one({"id": character_id})
    return Character(**updated_character)

@api_router.delete("/characters/{character_id}")
async def delete_character(character_id: str):
    """Delete a character"""
    result = await db.characters.delete_one({"id": character_id})
    if result.deleted_count == 0:
        raise ResourceNotFoundError("Character", character_id)
    return {"message": "Character deleted successfully"}

@api_router.post("/characters/{character_id}/apply/{clip_id}")
async def apply_character_to_clip(character_id: str, clip_id: str):
    """Apply character settings to a clip's generation prompt"""
    # Get character
    character_data = await db.characters.find_one({"id": character_id})
    if not character_data:
        raise ResourceNotFoundError("Character", character_id)

    character = Character(**character_data)

    # Get clip
    clip_data = await db.clips.find_one({"id": clip_id})
    if not clip_data:
        raise ClipNotFoundError(clip_id)

    clip = Clip(**clip_data)

    # Build enhanced prompt with character details
    character_prompt = f"{character.trigger_words} {character.name}"
    if character.description:
        character_prompt += f", {character.description}"
    if character.style_notes:
        character_prompt += f". Style: {character.style_notes}"

    # Update clip prompts
    updated_image_prompt = f"{character_prompt}. {clip.image_prompt or ''}".strip()
    updated_video_prompt = f"{character_prompt}. {clip.video_prompt or ''}".strip()

    await db.clips.update_one(
        {"id": clip_id},
        {"$set": {
            "image_prompt": updated_image_prompt,
            "video_prompt": updated_video_prompt,
            "character_id": character_id
        }}
    )

    logger.info(f"Applied character {character_id} to clip {clip_id}")
    return {
        "message": "Character applied to clip",
        "image_prompt": updated_image_prompt,
        "video_prompt": updated_video_prompt
    }

# Character Generation Endpoints

@api_router.post("/characters/{character_id}/generate")
async def generate_character_samples(
    character_id: str,
    server_id: str,
    prompt: Optional[str] = "",
    samples: int = 4,
    model: Optional[str] = None
):
    """Generate sample images for a character using their configured method"""
    # Ensure database is connected
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Get character
    character_data = await db.characters.find_one({"id": character_id})
    if not character_data:
        raise ResourceNotFoundError("Character", character_id)
    
    character = Character(**character_data)
    
    # Get server
    server_data = await db.comfyui_servers.find_one({"id": server_id})
    if not server_data:
        raise ServerNotFoundError(server_id)
    
    server = ComfyUIServer(**server_data)
    client = ComfyUIClient(server)
    
    # Check if server is online
    if not await client.check_connection():
        raise ServiceUnavailableError("ComfyUI", "Server is offline")
    
    # Build character prompt
    character_prompt = prompt
    if character.trigger_words:
        character_prompt += f" {character.trigger_words}"
    if character.description:
        character_prompt += f", {character.description}"
    if not character_prompt.strip():
        character_prompt = f"portrait of {character.name}, high quality, detailed"
    
    results = []
    
    # Generate samples based on character's method
    if character.generation_method == "ip_adapter" and character.reference_images:
        # Use IP-Adapter with reference images
        reference_image = character.reference_images[0]
        for i in range(samples):
            sample_prompt = f"{character_prompt}, variation {i+1}"
            result_url = await client.generate_character_with_ip_adapter(
                sample_prompt, reference_image, model, character.generation_params
            )
            if result_url:
                results.append({"url": result_url, "prompt": sample_prompt, "method": "ip_adapter"})
    
    elif character.generation_method == "reactor" and character.face_image:
        # Use Reactor with face image
        for i in range(samples):
            sample_prompt = f"{character_prompt}, variation {i+1}"
            result_url = await client.generate_character_with_reactor(
                sample_prompt, character.face_image, None, model, character.generation_params
            )
            if result_url:
                results.append({"url": result_url, "prompt": sample_prompt, "method": "reactor"})
    
    elif character.generation_method == "instantid" and character.face_image:
        # Use InstantID with face image
        for i in range(samples):
            sample_prompt = f"{character_prompt}, variation {i+1}"
            result_url = await client.generate_character_with_instantid(
                sample_prompt, character.face_image, None, model, character.generation_params
            )
            if result_url:
                results.append({"url": result_url, "prompt": sample_prompt, "method": "instantid"})
    
    else:
        # Fall back to standard generation
        for i in range(samples):
            sample_prompt = f"{character_prompt}, variation {i+1}"
            result_url = await client.generate_image(
                sample_prompt, "low quality, blurry", model, character.generation_params, []
            )
            if result_url:
                results.append({"url": result_url, "prompt": sample_prompt, "method": "standard"})
    
    return {
        "character_id": character_id,
        "character_name": character.name,
        "method": character.generation_method,
        "samples": results,
        "total_generated": len(results)
    }

@api_router.post("/characters/train-lora")
async def train_character_lora(
    character_id: str,
    training_images: List[str],
    training_params: Optional[Dict[str, Any]] = None
):
    """Train a custom LoRA for a character (placeholder for future implementation)"""
    # Ensure database is connected
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Get character
    character_data = await db.characters.find_one({"id": character_id})
    if not character_data:
        raise ResourceNotFoundError("Character", character_id)
    
    # This is a placeholder for future LoRA training implementation
    # For now, just return success with training info
    return {
        "message": "LoRA training feature coming soon",
        "character_id": character_id,
        "training_images_count": len(training_images),
        "status": "planned",
        "notes": "This will integrate with automatic LoRA training workflows"
    }

# FaceFusion Integration Endpoints

@api_router.post("/facefusion/enhance-face")
async def enhance_character_face(
    character_id: str,
    image_url: str,
    enhancement_model: str = "gfpgan_1.4",
    facefusion_url: str = "http://localhost:7870"
):
    """Enhance character face using FaceFusion"""
    # Ensure database is connected
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Get character
    character_data = await db.characters.find_one({"id": character_id})
    if not character_data:
        raise ResourceNotFoundError("Character", character_id)
    
    # Initialize FaceFusion client
    client = FaceFusionClient(facefusion_url)
    
    # Check connection
    if not await client.check_connection():
        raise ServiceUnavailableError("FaceFusion", "FaceFusion server is not accessible")
    
    # Convert URL to local path
    if image_url.startswith(f"{API}/"):
        image_path = UPLOADS_DIR / image_url.replace(f"{API}/", "")
    else:
        raise ValueError("Invalid image URL")
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")
    
    # Enhance face
    enhanced_path = await client.enhance_face(str(image_path), enhancement_model)
    
    if not enhanced_path:
        raise HTTPException(status_code=500, detail="Face enhancement failed")
    
    # Return enhanced image URL
    enhanced_url = f"{API}/uploads/{enhanced_path.split('uploads/')[-1]}"
    
    return {
        "character_id": character_id,
        "original_image": image_url,
        "enhanced_image": enhanced_url,
        "enhancement_model": enhancement_model,
        "message": "Face enhanced successfully"
    }

@api_router.post("/facefusion/adjust-face-age")
async def adjust_character_face_age(
    character_id: str,
    image_url: str,
    target_age: int,
    facefusion_url: str = "http://localhost:7870"
):
    """Adjust character face age using FaceFusion"""
    # Ensure database is connected
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Validate age
    if not (0 <= target_age <= 100):
        raise HTTPException(status_code=400, detail="Age must be between 0 and 100")
    
    # Get character
    character_data = await db.characters.find_one({"id": character_id})
    if not character_data:
        raise ResourceNotFoundError("Character", character_id)
    
    # Initialize FaceFusion client
    client = FaceFusionClient(facefusion_url)
    
    # Check connection
    if not await client.check_connection():
        raise ServiceUnavailableError("FaceFusion", "FaceFusion server is not accessible")
    
    # Convert URL to local path
    if image_url.startswith(f"{API}/"):
        image_path = UPLOADS_DIR / image_url.replace(f"{API}/", "")
    else:
        raise ValueError("Invalid image URL")
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")
    
    # Adjust face age
    adjusted_path = await client.adjust_face_age(str(image_path), target_age)
    
    if not adjusted_path:
        raise HTTPException(status_code=500, detail="Face age adjustment failed")
    
    # Return adjusted image URL
    adjusted_url = f"{API}/uploads/{adjusted_path.split('uploads/')[-1]}"
    
    return {
        "character_id": character_id,
        "original_image": image_url,
        "adjusted_image": adjusted_url,
        "target_age": target_age,
        "message": "Face age adjusted successfully"
    }

@api_router.post("/facefusion/swap-face")
async def swap_character_face(
    character_id: str,
    source_face_url: str,
    target_image_url: str,
    facefusion_url: str = "http://localhost:7870"
):
    """Swap character face using FaceFusion"""
    # Ensure database is connected
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Get character
    character_data = await db.characters.find_one({"id": character_id})
    if not character_data:
        raise ResourceNotFoundError("Character", character_id)
    
    # Initialize FaceFusion client
    client = FaceFusionClient(facefusion_url)
    
    # Check connection
    if not await client.check_connection():
        raise ServiceUnavailableError("FaceFusion", "FaceFusion server is not accessible")
    
    # Convert URLs to local paths
    def url_to_path(url: str) -> Path:
        if url.startswith(f"{API}/"):
            return UPLOADS_DIR / url.replace(f"{API}/", "")
        else:
            raise ValueError("Invalid image URL")
    
    source_path = url_to_path(source_face_url)
    target_path = url_to_path(target_image_url)
    
    if not source_path.exists():
        raise HTTPException(status_code=404, detail="Source face image not found")
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Target image not found")
    
    # Swap face
    swapped_path = await client.swap_face(str(source_path), str(target_path))
    
    if not swapped_path:
        raise HTTPException(status_code=500, detail="Face swap failed")
    
    # Return swapped image URL
    swapped_url = f"{API}/uploads/{swapped_path.split('uploads/')[-1]}"
    
    return {
        "character_id": character_id,
        "source_face": source_face_url,
        "target_image": target_image_url,
        "swapped_image": swapped_url,
        "message": "Face swapped successfully"
    }

@api_router.get("/facefusion/status")
async def check_facefusion_status(facefusion_url: str = "http://localhost:7870"):
    """Check FaceFusion server status"""
    client = FaceFusionClient(facefusion_url)
    is_online = await client.check_connection()
    
    return {
        "facefusion_url": facefusion_url,
        "is_online": is_online,
        "status": "online" if is_online else "offline",
        "message": "FaceFusion server is accessible" if is_online else "FaceFusion server is not accessible"
    }

@api_router.post("/facefusion/batch-process")
async def batch_process_character_faces(
    character_id: str,
    operations: List[Dict[str, Any]],
    facefusion_url: str = "http://localhost:7870"
):
    """Batch process character faces with multiple FaceFusion operations"""
    # Ensure database is connected
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Get character
    character_data = await db.characters.find_one({"id": character_id})
    if not character_data:
        raise ResourceNotFoundError("Character", character_id)
    
    # Initialize FaceFusion client
    client = FaceFusionClient(facefusion_url)
    
    # Check connection
    if not await client.check_connection():
        raise ServiceUnavailableError("FaceFusion", "FaceFusion server is not accessible")
    
    results = []
    
    for operation in operations:
        op_type = operation.get("type")
        image_url = operation.get("image_url")
        
        if not image_url:
            results.append({
                "operation": operation,
                "success": False,
                "error": "Missing image_url"
            })
            continue
        
        # Convert URL to local path
        if image_url.startswith(f"{API}/"):
            image_path = UPLOADS_DIR / image_url.replace(f"{API}/", "")
        else:
            results.append({
                "operation": operation,
                "success": False,
                "error": "Invalid image URL"
            })
            continue
        
        if not image_path.exists():
            results.append({
                "operation": operation,
                "success": False,
                "error": "Image file not found"
            })
            continue
        
        try:
            if op_type == "enhance":
                model = operation.get("enhancement_model", "gfpgan_1.4")
                result_path = await client.enhance_face(str(image_path), model)
                if result_path:
                    result_url = f"{API}/uploads/{result_path.split('uploads/')[-1]}"
                    results.append({
                        "operation": operation,
                        "success": True,
                        "result_url": result_url
                    })
                else:
                    results.append({
                        "operation": operation,
                        "success": False,
                        "error": "Enhancement failed"
                    })
            
            elif op_type == "age_adjust":
                target_age = operation.get("target_age", 25)
                result_path = await client.adjust_face_age(str(image_path), target_age)
                if result_path:
                    result_url = f"{API}/uploads/{result_path.split('uploads/')[-1]}"
                    results.append({
                        "operation": operation,
                        "success": True,
                        "result_url": result_url
                    })
                else:
                    results.append({
                        "operation": operation,
                        "success": False,
                        "error": "Age adjustment failed"
                    })
            
            else:
                results.append({
                    "operation": operation,
                    "success": False,
                    "error": f"Unsupported operation type: {op_type}"
                })
        
        except Exception as e:
            results.append({
                "operation": operation,
                "success": False,
                "error": str(e)
            })
    
    return {
        "character_id": character_id,
        "total_operations": len(operations),
        "successful_operations": sum(1 for r in results if r.get("success")),
        "results": results
    }

# Queue Management Endpoints
@api_router.post("/queue/jobs")
async def add_to_queue(
    clip_id: str,
    project_id: str,
    generation_type: str,
    prompt: str,
    server_id: Optional[str] = None,
    negative_prompt: Optional[str] = "",
    model: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    loras: Optional[List[Dict[str, Any]]] = None,
    priority: int = 0
):
    """Add a generation job to the smart queue"""
    import uuid
    from services.queue_manager import queue_manager

    job_id = str(uuid.uuid4())
    job = await queue_manager.add_job(
        job_id=job_id,
        clip_id=clip_id,
        project_id=project_id,
        generation_type=generation_type,
        prompt=prompt,
        negative_prompt=negative_prompt,
        model=model,
        params=params,
        loras=loras,
        priority=priority,
        preferred_server_id=server_id
    )

    return {
        "job_id": job.id,
        "status": job.status,
        "message": "Job added to queue"
    }

@api_router.get("/queue/status")
async def get_queue_status():
    """Get overall queue status"""
    from services.queue_manager import queue_manager
    return queue_manager.get_queue_status()

@api_router.get("/queue/jobs")
async def get_all_queue_jobs(status: Optional[str] = None):
    """Get all queue jobs, optionally filtered by status"""
    from services.queue_manager import queue_manager
    if status:
        jobs = queue_manager.get_jobs_by_status(status)
    else:
        jobs = queue_manager.get_all_jobs()
    return jobs

@api_router.get("/queue/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a specific job"""
    from services.queue_manager import queue_manager
    job_status = queue_manager.get_job_status(job_id)
    if not job_status:
        raise ResourceNotFoundError("Job", job_id)
    return job_status

@api_router.get("/queue/projects/{project_id}/jobs")
async def get_project_queue(project_id: str):
    """Get all queued jobs for a project"""
    from services.queue_manager import queue_manager
    jobs = queue_manager.get_project_jobs(project_id)
    return {"jobs": jobs}

@api_router.post("/queue/servers/{server_id}/register")
async def register_server_for_queue(
    server_id: str,
    server_name: str,
    is_online: bool = True,
    max_concurrent: int = 1
):
    """Register a server with the queue manager"""
    from services.queue_manager import queue_manager
    await queue_manager.register_server(
        server_id=server_id,
        server_name=server_name,
        is_online=is_online,
        max_concurrent=max_concurrent
    )
    return {"message": "Server registered successfully"}

@api_router.get("/queue/servers/{server_id}/next")
async def get_next_job_for_server(server_id: str):
    """Get the next job for a server to process"""
    from services.queue_manager import queue_manager
    job = await queue_manager.get_next_job(server_id)
    if not job:
        return {"message": "No jobs available"}

    return {
        "job_id": job.id,
        "clip_id": job.clip_id,
        "generation_type": job.generation_type,
        "prompt": job.prompt,
        "negative_prompt": job.negative_prompt,
        "model": job.model,
        "params": job.params,
        "loras": job.loras
    }

@api_router.post("/queue/jobs/{job_id}/complete")
async def complete_job(
    job_id: str,
    success: bool,
    result_url: Optional[str] = None,
    error: Optional[str] = None
):
    """Mark a job as completed"""
    from services.queue_manager import queue_manager
    await queue_manager.complete_job(
        job_id=job_id,
        success=success,
        result_url=result_url,
        error=error
    )
    return {"message": "Job status updated"}

# Configure structured logging
from utils.logging_config import setup_logging, get_logger
logger = setup_logging()

# Add CORS middleware with environment-based configuration BEFORE mounting routers
from config import config as app_config

# Configure CORS to allow requests from the frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],  # Specify allowed headers
)

# Add logging and performance middleware
from utils.logging_middleware import LoggingMiddleware
from utils.performance_middleware import PerformanceMiddleware

app.add_middleware(LoggingMiddleware, logger=get_logger("request"))
app.add_middleware(PerformanceMiddleware)

async def find_best_civitai_match_mongodb(server_model_name: str, db_conn, fallback: bool = False) -> dict:
    """
    Find best matching Civitai model from MongoDB database.
    
    Args:
        server_model_name: Name of the model from the ComfyUI server
        db_conn: Database connection
        fallback: If True, use lower threshold for matching
    
    Returns:
        Best matching dict or None if no match found
    """
    import re
    from difflib import SequenceMatcher
    
    def clean_model_name(name: str) -> str:
        """Clean model name by removing extensions and common prefixes"""
        name = re.sub(r'\.(safetensors|ckpt|pth|pt)$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^(sd|stable-diffusion|sd-|sdxl|sd_xl)_?', '', name, flags=re.IGNORECASE)
        name = re.sub(r'_v\d+(-\d+)?(_lightning)?(_bakedvae)?', '', name, flags=re.IGNORECASE)
        name = re.sub(r'(-\d+)+$', '', name)
        name = re.sub(r'[-_]+', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip().lower()
    
    server_name_clean = clean_model_name(server_model_name)
    server_name_original = server_model_name.lower().strip()
    
    print(f"Searching MongoDB for: '{server_name_clean}' (original: '{server_model_name}')")  # Debug
    
    # Strategy 1: Exact name match
    exact_match = await db_conn.database_models.find_one({
        "source": "civitai_sdxl",
        "name": {"$regex": f"^{re.escape(server_model_name)}$", "$options": "i"}
    })
    
    if exact_match:
        print(f"Found exact match in MongoDB: '{exact_match['name']}'")  # Debug
        return exact_match["civitai_info"]
    
    # Strategy 2: Search for cleaned name match
    cleaned_match = await db_conn.database_models.find_one({
        "source": "civitai_sdxl",
        "name": {"$regex": server_name_clean, "$options": "i"}
    })
    
    if cleaned_match:
        print(f"Found cleaned match in MongoDB: '{cleaned_match['name']}'")  # Debug
        return cleaned_match["civitai_info"]
    
    # Strategy 3: Fuzzy search with multiple candidates
    candidates = await db_conn.database_models.find({
        "source": "civitai_sdxl",
        "$or": [
            {"name": {"$regex": server_name_clean, "$options": "i"}},
            {"civitai_info.description": {"$regex": server_name_clean, "$options": "i"}},
            {"civitai_info.tags": {"$in": [server_name_clean]}}
        ]
    }).to_list(length=20)
    
    best_match = None
    best_score = 0.0
    
    # Define thresholds based on fallback mode
    high_threshold = 0.85 if not fallback else 0.7
    medium_threshold = 0.7 if not fallback else 0.5
    
    for doc in candidates:
        civitai_info = doc["civitai_info"]
        model_name = civitai_info.get("name", "")
        model_name_clean = clean_model_name(model_name)
        
        # Calculate similarity score
        similarity = SequenceMatcher(None, server_name_clean, model_name_clean).ratio()
        
        # Check for substring matches
        if server_name_clean in model_name_clean:
            similarity = max(similarity, 0.9)
        elif model_name_clean in server_name_clean:
            similarity = max(similarity, 0.8)
        
        # Update best match
        if similarity > best_score:
            best_score = similarity
            best_match = civitai_info
    
    # Apply minimum threshold
    min_threshold = medium_threshold if not fallback else 0.3
    if best_score < min_threshold:
        print(f"No match found above threshold {min_threshold}. Best score was {best_score}")  # Debug
        return None
    
    if best_match:
        print(f"Best match: '{best_match.get('name')}' with score {best_score:.3f}")  # Debug
        return best_match
    
    return None


def find_best_civitai_match_local(server_model_name: str, civitai_database: list, fallback: bool = False) -> dict:
    """
    Find best matching Civitai model from local JSON database.
    
    Args:
        server_model_name: Name of the model from the ComfyUI server
        civitai_database: List of models from the local JSON file
        fallback: If True, use lower threshold for matching
    
    Returns:
        Best matching dict or None if no match found
    """
    import re
    from difflib import SequenceMatcher
    
    def clean_model_name(name: str) -> str:
        """Clean model name by removing extensions and common prefixes"""
        name = re.sub(r'\.(safetensors|ckpt|pth|pt)$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^(sd|stable-diffusion|sd-|sdxl|sd_xl)_?', '', name, flags=re.IGNORECASE)
        name = re.sub(r'_v\d+(-\d+)?(_lightning)?(_bakedvae)?', '', name, flags=re.IGNORECASE)
        name = re.sub(r'(-\d+)+$', '', name)
        name = re.sub(r'[-_]+', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip().lower()
    
    server_name_clean = clean_model_name(server_model_name)
    server_name_original = server_model_name.lower().strip()
    
    print(f"Searching local database for: '{server_name_clean}' (original: '{server_model_name}')")  # Debug
    
    best_match = None
    best_score = 0.0
    match_details = []
    
    # Define thresholds based on fallback mode
    exact_threshold = 1.0
    high_threshold = 0.85 if not fallback else 0.7
    medium_threshold = 0.7 if not fallback else 0.5
    low_threshold = 0.5 if not fallback else 0.3
    
    for model in civitai_database:
        model_name = model.get("name", "")
        model_name_clean = clean_model_name(model_name)
        model_name_lower = model_name.lower()
        
        score = 0.0
        reason = ""
        
        # Strategy 1: Exact name match (highest priority)
        if server_name_clean == model_name_clean or server_name_original == model_name_lower:
            score = 1.0
            reason = "exact_name_match"
            print(f"Found exact match: '{model_name}'")  # Debug
        
        # Strategy 2: Check if model names are substrings
        elif server_name_clean in model_name_clean:
            score = 0.9
            reason = "server_name_in_model_name"
        elif model_name_clean in server_name_clean:
            score = 0.8
            reason = "model_name_in_server_name"
        
        # Strategy 3: Check for filename matches in model versions
        if score < 0.8 and "modelVersions" in model:
            for version in model["modelVersions"]:
                if "files" in version:
                    for file_info in version["files"]:
                        filename = file_info.get("name", "")
                        filename_clean = clean_model_name(filename)
                        
                        if server_name_clean == filename_clean or server_name_original == filename.lower():
                            score = max(score, 0.95)
                            reason = "filename_exact_match"
                        elif server_name_clean in filename_clean:
                            score = max(score, 0.85)
                            reason = "server_name_in_filename"
                        elif filename_clean in server_name_clean:
                            score = max(score, 0.75)
                            reason = "filename_in_server_name"
        
        # Strategy 4: Fuzzy matching using SequenceMatcher
        if score < 0.7:
            similarity = SequenceMatcher(None, server_name_clean, model_name_clean).ratio()
            if similarity > high_threshold:
                score = similarity
                reason = "fuzzy_high"
            elif similarity > medium_threshold:
                score = similarity
                reason = "fuzzy_medium"
        
        # Strategy 5: Contains matching (lower priority)
        if score < 0.5:
            if any(word in model_name_lower for word in server_name_clean.split() if len(word) > 2):
                score = 0.4
                reason = "contains_match"
        
        # Update best match if this score is better
        if score > best_score:
            best_score = score
            best_match = model
            match_details = [reason]
        elif score == best_score and score > 0:
            match_details.append(reason)
    
    # Apply minimum threshold
    min_threshold = low_threshold if fallback else medium_threshold
    if best_score < min_threshold:
        print(f"No match found above threshold {min_threshold}. Best score was {best_score}")  # Debug
        return None
    
    if best_match:
        print(f"Best match: '{best_match.get('name')}' with score {best_score:.3f} ({match_details[0] if match_details else 'unknown'})")  # Debug
        return best_match
    
    return None


# Mount API routers
# V1 API with versioned prefix
app.include_router(api_v1_router, prefix="/api/v1")

# Keep old API router for backward compatibility (will be removed after frontend migration)
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on startup"""
    global db, active_models_service
    logger.info("Starting application...")

    # Connect to database
    success = await db_manager.connect()
    if not success:
        logger.critical("Failed to connect to database. Application may not function properly.")
        # In production, you might want to exit here
        # raise RuntimeError("Database connection failed")
    else:
        db = db_manager.db
        # Initialize active models service
        active_models_service = ActiveModelsService(db_manager.client, db_manager.db_name)
        logger.info("Active models service initialized")
        logger.info("Application started successfully")

        # Validate OpenAI configuration (non-fatal - ComfyUI flows can still run)
        app_config.validate_openai_config()

        # Ensure local persistence directory for OpenAI videos exists
        try:
            sora_dir = Path("uploads") / "openai" / "videos"
            sora_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to ensure uploads directory for OpenAI videos: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    logger.info("Shutting down application...")
    await db_manager.disconnect()
    logger.info("Application shut down complete")