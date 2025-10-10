from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


def generate_uuid() -> str:
    from uuid import uuid4

    return str(uuid4())


class SceneCreateDTO(BaseModel):
    project_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=2000)
    lyrics: Optional[str] = Field(default="", max_length=5000)
    order: int = Field(default=0, ge=0)


class SceneUpdateDTO(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    lyrics: Optional[str] = Field(default=None, max_length=5000)
    order: Optional[int] = Field(default=None, ge=0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SceneResponseDTO(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    project_id: str
    name: str
    description: Optional[str] = ""
    lyrics: Optional[str] = ""
    order: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SceneListResponseDTO(BaseModel):
    scenes: List[SceneResponseDTO]
    total: int