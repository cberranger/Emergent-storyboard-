from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import database manager
from database import db_manager, get_database

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

# Create the main app without a prefix
app = FastAPI()

# Create a router without prefix (will be added when mounting)
api_router = APIRouter()

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

class ComfyUIServerInfo(BaseModel):
    server: ComfyUIServer
    models: List[Model] = []
    loras: List[Model] = []
    is_online: bool = False

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    music_file_path: Optional[str] = None
    music_duration: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""

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

# API Routes

@api_router.get("/")
async def root():
    return {"message": "StoryCanvas API is running", "status": "healthy"}

@api_router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {}
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
async def add_comfyui_server(server_data: ComfyUIServerCreate):
    server_dict = server_data.dict()
    
    # Auto-detect RunPod serverless
    if "runpod.ai" in server_dict["url"]:
        server_dict["server_type"] = "runpod"
        # Extract endpoint ID from URL
        if "/v2/" in server_dict["url"]:
            endpoint_id = server_dict["url"].split("/v2/")[-1].split("/")[0]
            server_dict["endpoint_id"] = endpoint_id
    
    server = ComfyUIServer(**server_dict)
    await db.comfyui_servers.insert_one(server.dict())
    return server

@api_router.get("/comfyui/servers", response_model=List[ComfyUIServer])
async def get_comfyui_servers():
    servers = await db.comfyui_servers.find().to_list(100)
    return [ComfyUIServer(**server) for server in servers]

@api_router.get("/comfyui/servers/{server_id}/info", response_model=ComfyUIServerInfo)
async def get_server_info(server_id: str):
    server_data = await db.comfyui_servers.find_one({"id": server_id})
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

# Project Management
@api_router.post("/projects", response_model=Project)
async def create_project(project_data: ProjectCreate):
    project_dict = project_data.dict()
    project = Project(**project_dict)
    await db.projects.insert_one(project.dict())
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(100)
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    from utils.errors import ProjectNotFoundError

    project_data = await db.projects.find_one({"id": project_id})
    if not project_data:
        raise ProjectNotFoundError(project_id)
    return Project(**project_data)

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
async def get_server_workflows(server_id: str):
    """Get available workflows from ComfyUI server"""
    server_data = await db.comfyui_servers.find_one({"id": server_id})
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
async def get_model_presets(model_name: str):
    """Get available presets for a specific model"""
    model_type = detect_model_type(model_name)
    model_config = MODEL_DEFAULTS.get(model_type)
    
    if not model_config:
        raise ResourceNotFoundError("Model", model)
    
    presets = {}
    for preset_name, preset_config in model_config.items():
        if isinstance(preset_config, dict):
            presets[preset_name] = preset_config
    
    return {
        "model_name": model_name,
        "model_type": model_type,
        "presets": presets
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mount API routers
# V1 API with versioned prefix
app.include_router(api_v1_router, prefix="/api/v1")

# Keep old API router for backward compatibility (will be removed after frontend migration)
app.include_router(api_router, prefix="/api")

# Add CORS middleware with environment-based configuration
from config import config as app_config

try:
    allowed_origins = app_config.get_cors_origins()
    logger.info(f"CORS allowed origins: {allowed_origins}")
except ValueError as e:
    logger.critical(f"CORS configuration error: {e}")
    raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=app_config.CORS_ALLOW_CREDENTIALS,
    allow_methods=app_config.CORS_ALLOW_METHODS,
    allow_headers=app_config.CORS_ALLOW_HEADERS,
    max_age=app_config.CORS_MAX_AGE,
)

@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on startup"""
    global db
    logger.info("Starting application...")

    # Connect to database
    success = await db_manager.connect()
    if not success:
        logger.critical("Failed to connect to database. Application may not function properly.")
        # In production, you might want to exit here
        # raise RuntimeError("Database connection failed")
    else:
        db = db_manager.db
        logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    logger.info("Shutting down application...")
    await db_manager.disconnect()
    logger.info("Application shut down complete")