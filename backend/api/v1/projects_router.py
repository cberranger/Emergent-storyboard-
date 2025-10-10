"""Project management router for API v1."""
from fastapi import APIRouter, Depends
from typing import List

from .dependencies import get_project_service
from services.project_service import ProjectService
from dtos import (
    ProjectCreateDTO,
    ProjectUpdateDTO,
    ProjectResponseDTO,
    ProjectListResponseDTO,
    ProjectWithScenesDTO,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponseDTO)
async def create_project(
    project_data: ProjectCreateDTO,
    service: ProjectService = Depends(get_project_service)
):
    """Create a new project"""
    return await service.create_project(project_data)


@router.get("", response_model=List[ProjectListResponseDTO])
async def list_projects(service: ProjectService = Depends(get_project_service)):
    """Get all projects"""
    return await service.list_projects()


@router.get("/{project_id}", response_model=ProjectResponseDTO)
async def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Get a specific project"""
    return await service.get_project(project_id)


@router.get("/{project_id}/with-scenes", response_model=ProjectWithScenesDTO)
async def get_project_with_scenes(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Get a project with all its scenes"""
    return await service.get_project_with_scenes(project_id)


@router.put("/{project_id}", response_model=ProjectResponseDTO)
async def update_project(
    project_id: str,
    project_data: ProjectUpdateDTO,
    service: ProjectService = Depends(get_project_service)
):
    """Update a project"""
    return await service.update_project(project_id, project_data)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Delete a project"""
    await service.delete_project(project_id)
    return {"message": "Project deleted successfully"}
