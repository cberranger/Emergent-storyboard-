"""Scene management router for API v1."""
from fastapi import APIRouter, Depends
from typing import List

from .dependencies import get_project_service
from services.project_service import ProjectService
from dtos import (
    SceneCreateDTO,
    SceneUpdateDTO,
    SceneResponseDTO,
    SceneListResponseDTO,
)

router = APIRouter(prefix="/scenes", tags=["scenes"])


@router.post("", response_model=SceneResponseDTO)
async def create_scene(
    scene_data: SceneCreateDTO,
    service: ProjectService = Depends(get_project_service)
):
    """Create a new scene"""
    return await service.create_scene(scene_data)


@router.get("/project/{project_id}", response_model=List[SceneListResponseDTO])
async def list_scenes_by_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Get all scenes for a project"""
    return await service.list_scenes(project_id)


@router.get("/{scene_id}", response_model=SceneResponseDTO)
async def get_scene(
    scene_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Get a specific scene"""
    return await service.get_scene(scene_id)


@router.put("/{scene_id}", response_model=SceneResponseDTO)
async def update_scene(
    scene_id: str,
    scene_data: SceneUpdateDTO,
    service: ProjectService = Depends(get_project_service)
):
    """Update a scene"""
    return await service.update_scene(scene_id, scene_data)


@router.delete("/{scene_id}")
async def delete_scene(
    scene_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Delete a scene"""
    await service.delete_scene(scene_id)
    return {"message": "Scene deleted successfully"}


@router.get("/{scene_id}/timeline-analysis")
async def analyze_scene_timeline(
    scene_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """
    Analyze timeline for a scene - detect overlaps, gaps, and provide suggestions
    """
    return await service.analyze_timeline(scene_id)
