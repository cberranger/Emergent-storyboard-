from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
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

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://192.168.1.10:27017')
client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
db = client[os.environ.get('DB_NAME', 'Storyboard')]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

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

class ClipVersion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version_number: int
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    image_prompt: Optional[str] = None
    video_prompt: Optional[str] = None
    generation_params: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Clip(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scene_id: str
    name: str
    lyrics: Optional[str] = ""
    length: float = 5.0  # seconds
    timeline_position: float = 0.0  # position on timeline
    order: int = 0
    # Enhanced prompting system
    image_prompt: Optional[str] = ""
    video_prompt: Optional[str] = ""
    # Gallery system
    generated_images: List[GeneratedContent] = []
    generated_videos: List[GeneratedContent] = []
    selected_image_id: Optional[str] = None
    selected_video_id: Optional[str] = None
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

# Model defaults configuration
MODEL_DEFAULTS = {
    "sdxl": {
        "steps": 30,
        "cfg": 7.0,
        "width": 1024,
        "height": 1024,
        "sampler": "euler_a",
        "scheduler": "normal"
    },
    "flux_dev": {
        "steps": 20,
        "cfg": 3.5,
        "width": 1024,
        "height": 1024,
        "sampler": "euler",
        "scheduler": "simple"
    },
    "flux_krea": {
        "steps": 4,
        "cfg": 1.0,
        "width": 1024,
        "height": 1024,
        "sampler": "euler",
        "scheduler": "simple"
    },
    "wan_2_1": {
        "steps": 25,
        "cfg": 7.5,
        "width": 512,
        "height": 512,
        "sampler": "ddim",
        "scheduler": "normal"
    },
    "wan_2_2": {
        "steps": 25,
        "cfg": 7.5,
        "width": 512,
        "height": 512,
        "sampler": "ddim",
        "scheduler": "normal"
    },
    "hidream": {
        "steps": 20,
        "cfg": 6.0,
        "width": 1024,
        "height": 1024,
        "sampler": "euler_a",
        "scheduler": "karras"
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
    elif "wan" in model_name_lower:
        if "2.2" in model_name_lower or "22" in model_name_lower:
            return "wan_2_2"
        else:
            return "wan_2_1"
    elif "hidream" in model_name_lower:
        return "hidream"
    elif "sd15" in model_name_lower or "1.5" in model_name_lower:
        return "wan_2_1"  # Use SD 1.5 defaults
    
    # Default fallback
    return "sdxl"

def get_model_defaults(model_name: str) -> Dict[str, Any]:
    """Get intelligent defaults based on model type"""
    model_type = detect_model_type(model_name)
    return MODEL_DEFAULTS.get(model_type, MODEL_DEFAULTS["sdxl"])

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
        # For RunPod, we'll just check if we can reach the API endpoint
        # A more thorough check would require submitting a test job
        if not self.server.api_key:
            return False
        
        headers = {"Authorization": f"Bearer {self.server.api_key}"}
        async with aiohttp.ClientSession() as session:
            # Try to get server health/info - RunPod doesn't have a direct health endpoint
            # so we'll consider it online if we have valid credentials
            try:
                async with session.get(f"https://api.runpod.ai/v2/{self.endpoint_id}", headers=headers, timeout=5) as response:
                    return response.status in [200, 404]  # 404 is also acceptable as it means the endpoint exists
            except:
                return True  # Assume online if we can't verify (RunPod might not have health endpoints)
    
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

# API Routes

@api_router.get("/")
async def root():
    return {"message": "StoryCanvas API is running", "status": "healthy"}

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
        raise HTTPException(status_code=404, detail="Server not found")
    
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
    project_data = await db.projects.find_one({"id": project_id})
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project_data)

@api_router.post("/projects/{project_id}/upload-music")
async def upload_music(project_id: str, file: UploadFile = File(...)):
    project_data = await db.projects.find_one({"id": project_id})
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Save the uploaded file
    file_path = UPLOADS_DIR / f"{project_id}_{file.filename}"
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
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create faces directory if it doesn't exist
    faces_dir = UPLOADS_DIR / "faces"
    faces_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    import uuid
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
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

@api_router.get("/projects/{project_id}/scenes", response_model=List[Scene])
async def get_project_scenes(project_id: str):
    scenes = await db.scenes.find({"project_id": project_id}).sort("order").to_list(100)
    return [Scene(**scene) for scene in scenes]

@api_router.get("/scenes/{scene_id}", response_model=Scene)
async def get_scene(scene_id: str):
    scene_data = await db.scenes.find_one({"id": scene_id})
    if not scene_data:
        raise HTTPException(status_code=404, detail="Scene not found")
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
        raise HTTPException(status_code=404, detail="Scene not found")
    
    return {"message": "Scene updated successfully"}

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
        raise HTTPException(status_code=404, detail="Clip not found")
    return Clip(**clip_data)

@api_router.put("/clips/{clip_id}/timeline-position")
async def update_clip_timeline_position(clip_id: str, position: float):
    result = await db.clips.update_one(
        {"id": clip_id},
        {"$set": {"timeline_position": position, "updated_at": datetime.now(timezone.utc)}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Clip not found")
    return {"message": "Timeline position updated"}

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
        raise HTTPException(status_code=404, detail="Clip not found")
    return {"message": "Prompts updated successfully"}

@api_router.get("/clips/{clip_id}/gallery")
async def get_clip_gallery(clip_id: str):
    clip_data = await db.clips.find_one({"id": clip_id})
    if not clip_data:
        raise HTTPException(status_code=404, detail="Clip not found")
    
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
        raise HTTPException(status_code=400, detail="Invalid content type")
    
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
        raise HTTPException(status_code=404, detail="Clip not found")
    
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
        raise HTTPException(status_code=404, detail="Server not found")
    
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

# Generation
@api_router.post("/generate")
async def generate_content(request: GenerationRequest):
    try:
        logging.info(f"Generation request: {request}")
        
        # Get server info
        server_data = await db.comfyui_servers.find_one({"id": request.server_id})
        if not server_data:
            raise HTTPException(status_code=404, detail="Server not found")
        
        logging.info(f"Found server: {server_data}")
        server = ComfyUIServer(**server_data)
        client = ComfyUIClient(server)
        
    except Exception as e:
        logging.error(f"Error in generate_content setup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Setup error: {str(e)}")
    
    # Check if server is online
    if not await client.check_connection():
        raise HTTPException(status_code=503, detail="ComfyUI server is offline")
    
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
                # Get server info for metadata
                server = ComfyUIServer(**server_data)
                
                # Detect model type and get defaults
                model_type = detect_model_type(request.model or "unknown")
                
                # Create new generated content
                new_content = GeneratedContent(
                    content_type="image",
                    url=result_url,
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt or "",
                    server_id=request.server_id,
                    server_name=server.name,
                    model_name=request.model or "unknown",
                    model_type=model_type,
                    generation_params=request.params or {},
                    is_selected=False
                )
                
                # Add to clip gallery
                clip_data = await db.clips.find_one({"id": request.clip_id})
                if clip_data:
                    logging.info(f"Found clip: {clip_data}")
                    
                    # Initialize clip with default values for new fields
                    if "generated_images" not in clip_data:
                        clip_data["generated_images"] = []
                    if "generated_videos" not in clip_data:
                        clip_data["generated_videos"] = []
                    if "selected_image_id" not in clip_data:
                        clip_data["selected_image_id"] = None
                    if "selected_video_id" not in clip_data:
                        clip_data["selected_video_id"] = None
                    if "image_prompt" not in clip_data:
                        clip_data["image_prompt"] = ""
                    if "video_prompt" not in clip_data:
                        clip_data["video_prompt"] = ""
                    if "updated_at" not in clip_data:
                        clip_data["updated_at"] = datetime.now(timezone.utc)
                    
                    clip = Clip(**clip_data)
                    
                    # Add to generated images
                    clip.generated_images.append(new_content)
                    
                    # If this is the first image, select it automatically
                    if len(clip.generated_images) == 1:
                        clip.selected_image_id = new_content.id
                        new_content.is_selected = True
                    
                    # Update clip
                    await db.clips.update_one(
                        {"id": request.clip_id},
                        {"$set": {
                            "generated_images": [img.dict() for img in clip.generated_images],
                            "selected_image_id": clip.selected_image_id,
                            "updated_at": datetime.now(timezone.utc)
                        }}
                    )
                    
                    return {
                        "message": "Image generated successfully", 
                        "content": new_content.dict(),
                        "total_images": len(clip.generated_images)
                    }
            
            raise HTTPException(status_code=500, detail="Failed to generate image")
        
        elif request.generation_type == "video":
            # Video generation would be implemented similarly
            raise HTTPException(status_code=501, detail="Video generation not implemented yet")
        
        else:
            raise HTTPException(status_code=400, detail="Invalid generation type")
            
    except Exception as e:
        logging.error(f"Error in generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

# Add CORS middleware - configured for LAN access  
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Allow all origins for LAN setup
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()