from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

from .scene_dtos import SceneResponseDTO  # Forward reference safeguard


def generate_uuid() -> str:
    from uuid import uuid4

    return str(uuid4())


class ProjectCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=2000)


class ProjectUpdateDTO(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    music_file_path: Optional[str] = Field(default=None, max_length=1024)
    music_duration: Optional[float] = Field(default=None, ge=0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectResponseDTO(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    description: Optional[str] = ""
    music_file_path: Optional[str] = None
    music_duration: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectWithScenesDTO(ProjectResponseDTO):
    scenes: List[SceneResponseDTO] = []


class ProjectListResponseDTO(BaseModel):
    projects: List[ProjectResponseDTO]
    total: int