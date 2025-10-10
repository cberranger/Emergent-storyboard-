from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field


class UploadMusicResponseDTO(BaseModel):
    message: str = "Music uploaded successfully"
    file_path: str
    duration: Optional[float] = Field(default=None, ge=0)


class UploadFaceImageResponseDTO(BaseModel):
    message: str = "Face image uploaded successfully"
    file_url: str
    file_path: str