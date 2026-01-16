from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict


class ModelDTO(BaseModel):
    """Represents a model entry exposed to clients."""

    name: str
    type: str  # checkpoint, lora, vae, etc.


class ComfyUIServerCreateDTO(BaseModel):
    """Payload for registering a new ComfyUI server."""

    name: str
    url: HttpUrl
    server_type: str = Field(default="standard", pattern="^(standard|runpod)$")
    api_key: Optional[str] = None

    @field_validator("url")
    @classmethod
    def strip_trailing_slash(cls, value: HttpUrl) -> HttpUrl:
        return HttpUrl(str(value).rstrip("/"))  # type: ignore[arg-type]


class ModelDTO(BaseModel):
    """Represents a model entry exposed to clients."""

    name: str
    type: str  # checkpoint, lora, vae, etc.


class ComfyUIServerCreateDTO(BaseModel):
    """Payload for registering a new ComfyUI server."""

    name: str
    url: HttpUrl
    server_type: str = Field(default="standard", pattern="^(standard|runpod)$")
    api_key: Optional[str] = None

    @field_validator("url")
    @classmethod
    def strip_trailing_slash(cls, value: HttpUrl) -> HttpUrl:
        return HttpUrl(str(value).rstrip("/"))  # type: ignore[arg-type]


class ComfyUIServerDTO(BaseModel):
    """Represents a ComfyUI server entry stored in persistence."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    url: str
    server_type: str = "standard"
    api_key: Optional[str] = None
    endpoint_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComfyUIServerInfoDTO(BaseModel):
    """Detailed response for server info call."""

    server: ComfyUIServerDTO
    models: List[ModelDTO] = []
    loras: List[ModelDTO] = []
    is_online: bool = False


def uuid4() -> str:
    from uuid import uuid4 as _uuid4

    return str(_uuid4())
