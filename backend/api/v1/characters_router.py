"""Character management router for API v1."""
from fastapi import APIRouter, Depends
from typing import List, Optional

from .dependencies import get_project_service
from services.project_service import ProjectService
from dtos import (
    CharacterCreateDTO,
    CharacterUpdateDTO,
    CharacterResponseDTO,
    CharacterListResponseDTO,
)

router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("", response_model=CharacterResponseDTO)
async def create_character(
    character_data: CharacterCreateDTO,
    service: ProjectService = Depends(get_project_service)
):
    """Create a new character for consistent generation"""
    return await service.create_character(character_data)


@router.get("", response_model=List[CharacterListResponseDTO])
async def list_characters(
    project_id: Optional[str] = None,
    service: ProjectService = Depends(get_project_service)
):
    """Get all characters, optionally filtered by project"""
    return await service.list_characters(project_id)


@router.get("/{character_id}", response_model=CharacterResponseDTO)
async def get_character(
    character_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Get a specific character"""
    return await service.get_character(character_id)


@router.put("/{character_id}", response_model=CharacterResponseDTO)
async def update_character(
    character_id: str,
    character_data: CharacterUpdateDTO,
    service: ProjectService = Depends(get_project_service)
):
    """Update a character"""
    return await service.update_character(character_id, character_data)


@router.delete("/{character_id}")
async def delete_character(
    character_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Delete a character"""
    await service.delete_character(character_id)
    return {"message": "Character deleted successfully"}


@router.post("/{character_id}/apply/{clip_id}")
async def apply_character_to_clip(
    character_id: str,
    clip_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Apply character settings to a clip's generation prompt"""
    return await service.apply_character_to_clip(character_id, clip_id)
