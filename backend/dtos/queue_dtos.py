from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueueJobRequestDTO(BaseModel):
    clip_id: str
    project_id: str
    generation_type: str = Field(..., pattern="^(image|video)$")
    prompt: str
    negative_prompt: Optional[str] = ""
    model: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    loras: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    priority: int = 0
    server_id: Optional[str] = None


class QueueJobStatusDTO(BaseModel):
    id: str
    clip_id: str
    project_id: str
    generation_type: str
    status: str
    priority: int
    server_id: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error: Optional[str]
    result_url: Optional[str]
    retry_count: int
    estimated_duration: Optional[float]


class QueueJobResponseDTO(BaseModel):
    job_id: str
    status: str
    message: str = "Job added to queue"


class QueueServerRegistrationDTO(BaseModel):
    server_id: str
    server_name: str
    is_online: bool = True
    max_concurrent: int = Field(default=1, ge=1)


class QueueStatusDTO(BaseModel):
    queued_jobs: int
    processing_jobs: int
    servers: Dict[str, Dict[str, Any]]