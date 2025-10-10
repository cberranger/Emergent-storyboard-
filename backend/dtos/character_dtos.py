from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


def generate_uuid() -> str:
    from uuid import uuid4

    return str(uuid4())


class CharacterCreateDTO(BaseModel):
    project_id: str
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=2000)
    reference_images: List[str] = Field(default_factory=list)
    lora: Optional[str] = Field(default=None, max_length=200)
    trigger_words: Optional[str] = Field(default="", max_length=500)
    style_notes: Optional[str] = Field(default="", max_length=2000)


class CharacterUpdateDTO(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    reference_images: Optional[List[str]] = None
    lora: Optional[str] = Field(default=None, max_length=200)
    trigger_words: Optional[str] = Field(default=None, max_length=500)
    style_notes: Optional[str] = Field(default=None, max_length=2000)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CharacterResponseDTO(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    project_id: str
    name: str
    description: Optional[str] = ""
    reference_images: List[str] = Field(default_factory=list)
    lora: Optional[str] = None
    trigger_words: Optional[str] = ""
    style_notes: Optional[str] = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CharacterListResponseDTO(BaseModel):
    characters: List[CharacterResponseDTO]
    total: int