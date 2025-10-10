from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


def generate_uuid() -> str:
    from uuid import uuid4

    return str(uuid4())


class LoraConfigDTO(BaseModel):
    name: str
    weight: float = 1.0


class GeneratedContentDTO(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    content_type: str = Field(..., pattern="^(image|video)$")
    url: Optional[str] = None
    prompt: str
    negative_prompt: Optional[str] = ""
    server_id: str
    server_name: str
    model_name: str
    model_type: Optional[str] = None
    generation_params: Dict[str, Any] = Field(default_factory=dict)
    is_selected: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator("url")
    def validate_url(cls, value: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if not value:
            return value

        from utils.url_validator import url_validator

        content_type = values.get("content_type", "unknown")
        if content_type == "video":
            url_validator.validate_video_url(value)
        elif content_type == "image":
            url_validator.validate_image_url(value)
        return value


class ClipVersionDTO(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    version_number: int
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    image_prompt: Optional[str] = None
    video_prompt: Optional[str] = None
    generation_params: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator("image_url")
    def validate_image_url(cls, value: Optional[str]) -> Optional[str]:
        if value:
            from utils.url_validator import url_validator

            url_validator.validate_image_url(value)
        return value

    @validator("video_url")
    def validate_video_url(cls, value: Optional[str]) -> Optional[str]:
        if value:
            from utils.url_validator import url_validator

            url_validator.validate_video_url(value)
        return value


class ClipCreateDTO(BaseModel):
    scene_id: str
    name: str = Field(..., min_length=1, max_length=200)
    lyrics: Optional[str] = Field(default="", max_length=5000)
    length: float = Field(default=5.0, gt=0)
    timeline_position: float = Field(default=0.0, ge=0)
    order: int = Field(default=0, ge=0)
    image_prompt: Optional[str] = ""
    video_prompt: Optional[str] = ""


class ClipUpdateDTO(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    lyrics: Optional[str] = Field(default=None, max_length=5000)
    length: Optional[float] = Field(default=None, gt=0)
    timeline_position: Optional[float] = Field(default=None, ge=0)
    order: Optional[int] = Field(default=None, ge=0)
    image_prompt: Optional[str] = Field(default=None)
    video_prompt: Optional[str] = Field(default=None)

    @validator("timeline_position")
    def validate_timeline_position(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value > 10000:
            raise ValueError("Timeline position exceeds maximum (10000 seconds)")
        return value


class ClipResponseDTO(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    scene_id: str
    name: str
    lyrics: Optional[str] = ""
    length: float = 5.0
    timeline_position: float = 0.0
    order: int = 0
    image_prompt: Optional[str] = ""
    video_prompt: Optional[str] = ""
    generated_images: List[GeneratedContentDTO] = Field(default_factory=list)
    generated_videos: List[GeneratedContentDTO] = Field(default_factory=list)
    selected_image_id: Optional[str] = None
    selected_video_id: Optional[str] = None
    character_id: Optional[str] = None
    versions: List[ClipVersionDTO] = Field(default_factory=list)
    active_version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClipTimelineUpdateDTO(BaseModel):
    position: float = Field(..., ge=0, le=10000)

    @validator("position")
    def normalize_position(cls, value: float) -> float:
        return round(value, 2)


class ClipGalleryResponseDTO(BaseModel):
    images: List[GeneratedContentDTO]
    videos: List[GeneratedContentDTO]
    selected_image_id: Optional[str]
    selected_video_id: Optional[str]