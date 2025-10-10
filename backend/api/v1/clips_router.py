"""Clip management router for API v1."""
from fastapi import APIRouter, Depends
from typing import List

from .dependencies import get_project_service
from services.project_service import ProjectService
from dtos import (
    ClipCreateDTO,
    ClipUpdateDTO,
    ClipResponseDTO,
    ClipTimelineUpdateDTO,
    ClipGalleryResponseDTO,
)

router = APIRouter(prefix="/clips", tags=["clips"])


@router.post("", response_model=ClipResponseDTO)
async def create_clip(
    clip_data: ClipCreateDTO,
    service: ProjectService = Depends(get_project_service)
):
    """Create a new clip"""
    return await service.create_clip(clip_data)


@router.get("/scene/{scene_id}", response_model=List[ClipResponseDTO])
async def list_clips_by_scene(
    scene_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Get all clips for a scene"""
    return await service.list_clips(scene_id)


@router.get("/{clip_id}", response_model=ClipResponseDTO)
async def get_clip(
    clip_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Get a specific clip"""
    return await service.get_clip(clip_id)


@router.get("/{clip_id}/gallery", response_model=ClipGalleryResponseDTO)
async def get_clip_gallery(
    clip_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Get clip gallery with all generated content"""
    return await service.get_clip_gallery(clip_id)


@router.put("/{clip_id}", response_model=ClipResponseDTO)
async def update_clip(
    clip_id: str,
    clip_data: ClipUpdateDTO,
    service: ProjectService = Depends(get_project_service)
):
    """Update a clip"""
    return await service.update_clip(clip_id, clip_data)


@router.put("/{clip_id}/timeline-position")
async def update_clip_timeline_position(
    clip_id: str,
    position_data: ClipTimelineUpdateDTO,
    check_overlap: bool = True,
    service: ProjectService = Depends(get_project_service)
):
    """Update clip timeline position with overlap detection"""
    return await service.update_clip_timeline_position(
        clip_id, position_data.position, check_overlap
    )


@router.put("/{clip_id}/prompts")
async def update_clip_prompts(
    clip_id: str,
    image_prompt: str = "",
    video_prompt: str = "",
    service: ProjectService = Depends(get_project_service)
):
    """Update clip prompts"""
    return await service.update_clip_prompts(clip_id, image_prompt, video_prompt)


@router.delete("/{clip_id}")
async def delete_clip(
    clip_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Delete a clip"""
    await service.delete_clip(clip_id)
    return {"message": "Clip deleted successfully"}
