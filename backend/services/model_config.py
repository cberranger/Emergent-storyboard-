from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid

from dtos.inference_config_dtos import (
    ModelConfigurationDTO,
    ModelConfigurationCreateDTO,
    ModelConfigurationUpdateDTO,
)
from repositories.inference_configuration_repository import ModelConfigurationRepository

MODEL_DEFAULTS: Dict[str, Dict[str, Any]] = {
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
            "video_frames": 14,
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
            "video_frames": 25,
        },
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
            "video_frames": 14,
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
            "video_frames": 25,
        },
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
            "video_frames": 14,
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
            "video_frames": 25,
        },
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
            "video_frames": 14,
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
            "video_frames": 25,
        },
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
            "text_encoder": "clip_l.safetensors",
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
            "text_encoder": "clip_l.safetensors",
        },
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
            "lightning_lora": "wan2.2_i2v_lightx2v_4steps_lora_v1",
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
            "text_encoder": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        },
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
            "video_frames": 14,
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
            "video_frames": 25,
        },
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
            "specializes_in": "text_rendering",
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
            "specializes_in": "text_rendering",
        },
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
            "specializes_in": "image_editing",
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
        },
    },
}


def detect_model_type(model_name: str) -> Optional[str]:
    model_name_lower = model_name.lower()

    if "flux" in model_name_lower:
        if "dev" in model_name_lower:
            return "flux_dev"
        if "krea" in model_name_lower:
            return "flux_krea"
        return "flux_dev"

    if "sdxl" in model_name_lower or "xl" in model_name_lower:
        return "sdxl"

    if "pony" in model_name_lower:
        return "pony"

    if "wan" in model_name_lower:
        if "2.2" in model_name_lower or "22" in model_name_lower:
            return "wan_2_2"
        return "wan_2_1"

    if "hidream" in model_name_lower:
        return "hidream"

    if "qwen" in model_name_lower:
        if "edit" in model_name_lower:
            return "qwen_edit"
        return "qwen_image"

    if "sd15" in model_name_lower or "1.5" in model_name_lower:
        return "wan_2_1"

    return "sdxl"


def get_model_defaults(model_name: str, preset: str = "fast") -> Dict[str, Any]:
    model_type = detect_model_type(model_name)
    model_config = MODEL_DEFAULTS.get(model_type or "sdxl", MODEL_DEFAULTS["sdxl"])
    return model_config.get(preset, model_config.get("fast", model_config.get("quality", {})))


class ModelConfigurationService:
    """Service for managing model configurations"""

    def __init__(self, repository: ModelConfigurationRepository):
        self.repository = repository

    async def create_configuration(
        self, config_data: ModelConfigurationCreateDTO
    ) -> ModelConfigurationDTO:
        """Create a new model configuration"""
        config_dict = config_data.model_dump()
        config_dict["id"] = str(uuid.uuid4())
        config_dict["created_at"] = datetime.now(timezone.utc)
        config_dict["updated_at"] = datetime.now(timezone.utc)

        created = await self.repository.create(config_dict)
        return ModelConfigurationDTO(**created)

    async def get_configuration(self, config_id: str) -> Optional[ModelConfigurationDTO]:
        """Get a configuration by ID"""
        config = await self.repository.find_by_id(config_id)
        return ModelConfigurationDTO(**config) if config else None

    async def get_configurations_by_model(self, model_id: str) -> List[ModelConfigurationDTO]:
        """Get all configurations for a specific model"""
        configs = await self.repository.find_by_model_id(model_id)
        return [ModelConfigurationDTO(**config) for config in configs]

    async def get_configurations_by_base_model(
        self, base_model: str
    ) -> List[ModelConfigurationDTO]:
        """Get all global configurations for a base model type"""
        configs = await self.repository.find_by_base_model(base_model)
        return [ModelConfigurationDTO(**config) for config in configs]

    async def update_configuration(
        self, config_id: str, update_data: ModelConfigurationUpdateDTO
    ) -> Optional[ModelConfigurationDTO]:
        """Update a configuration"""
        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.now(timezone.utc)

        updated = await self.repository.update_by_id(config_id, update_dict)
        return ModelConfigurationDTO(**updated) if updated else None

    async def delete_configuration(self, config_id: str) -> bool:
        """Delete a configuration"""
        return await self.repository.delete_by_id(config_id)

    async def get_default_configuration(
        self, model_id: Optional[str] = None, base_model: Optional[str] = None
    ) -> Optional[ModelConfigurationDTO]:
        """Get the default configuration for a model or base model type"""
        if model_id:
            config = await self.repository.find_default_by_model(model_id)
            if config:
                return ModelConfigurationDTO(**config)

        if base_model:
            config = await self.repository.find_default_by_base_model(base_model)
            if config:
                return ModelConfigurationDTO(**config)

        return None