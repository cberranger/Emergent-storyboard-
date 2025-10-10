from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .clip_dtos import LoraConfigDTO


def generate_uuid() -> str:
    from uuid import uuid4

    return str(uuid4())


class StyleTemplateCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=2000)
    category: str = Field(default="custom", max_length=100)
    model: Optional[str] = Field(default=None, max_length=200)
    negative_prompt: Optional[str] = Field(default="", max_length=5000)
    loras: List[LoraConfigDTO] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)
    preview_url: Optional[str] = Field(default=None, max_length=1024)
    is_public: bool = False


class StyleTemplateUpdateDTO(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=200)
    negative_prompt: Optional[str] = Field(default=None, max_length=5000)
    loras: Optional[List[LoraConfigDTO]] = None
    params: Optional[Dict[str, Any]] = None
    preview_url: Optional[str] = Field(default=None, max_length=1024)
    is_public: Optional[bool] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StyleTemplateResponseDTO(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    description: Optional[str] = ""
    category: str = "custom"
    model: Optional[str] = None
    negative_prompt: Optional[str] = ""
    loras: List[LoraConfigDTO] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)
    preview_url: Optional[str] = None
    is_public: bool = False
    created_by: Optional[str] = None
    use_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StyleTemplateListResponseDTO(BaseModel):
    templates: List[StyleTemplateResponseDTO]
    total: int