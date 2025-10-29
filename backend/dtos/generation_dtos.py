from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from .clip_dtos import GeneratedContentDTO, LoraConfigDTO


class GenerationParamsDTO(BaseModel):
    width: Optional[int] = Field(default=None, ge=64, le=4096)
    height: Optional[int] = Field(default=None, ge=64, le=4096)
    steps: Optional[int] = Field(default=None, ge=1, le=200)
    cfg: Optional[float] = Field(default=None, ge=0.1, le=30.0)
    sampler: Optional[str] = None
    scheduler: Optional[str] = None
    seed: Optional[int] = None
    video_frames: Optional[int] = Field(default=None, ge=1, le=300)
    video_fps: Optional[int] = Field(default=None, ge=1, le=120)
    motion_bucket_id: Optional[int] = Field(default=None, ge=0)
    use_custom_workflow: Optional[bool] = False
    workflow_json: Optional[str] = None
    provider: Optional[str] = Field(default=None, description="Generation provider. Use 'openai' to route to OpenAI Sora")
    input_reference_url: Optional[str] = Field(default=None, description="URL (preferably /uploads/...) to reference image for Sora first frame")
    input_reference_path: Optional[str] = Field(default=None, description="Local server path to reference image for Sora first frame")
    input_reference_mime: Optional[str] = Field(default=None, description="MIME for input_reference (image/jpeg, image/png, image/webp)")

    @validator("workflow_json")
    def validate_workflow_json(cls, value: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if value and not values.get("use_custom_workflow"):
            raise ValueError("workflow_json provided but use_custom_workflow is False")
        return value


class GenerationRequestDTO(BaseModel):
    clip_id: str
    server_id: str
    prompt: str
    negative_prompt: Optional[str] = ""
    model: Optional[str] = None
    lora: Optional[str] = None
    loras: Optional[List[LoraConfigDTO]] = Field(default_factory=list)
    generation_type: str = Field(..., pattern="^(image|video)$")
    params: Optional[GenerationParamsDTO] = None


class GenerationResponseDTO(BaseModel):
    message: str
    content: GeneratedContentDTO
    total_images: Optional[int] = None
    total_videos: Optional[int] = None


class BatchGenerationRequestDTO(BaseModel):
    clip_ids: List[str] = Field(..., min_items=1)
    server_id: str
    generation_type: str = Field(..., pattern="^(image|video)$")
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = ""
    model: Optional[str] = None
    params: Optional[GenerationParamsDTO] = None
    loras: Optional[List[LoraConfigDTO]] = Field(default_factory=list)


class BatchGenerationJobDTO(BaseModel):
    clip_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BatchGenerationStatusDTO(BaseModel):
    id: str
    status: str
    total: int
    completed: int
    failed: int
    results: List[BatchGenerationJobDTO]
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))