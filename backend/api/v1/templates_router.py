"""Style template router for API v1."""
from fastapi import APIRouter, Depends
from typing import List, Optional

from .dependencies import get_project_service
from services.project_service import ProjectService
from dtos import (
    StyleTemplateCreateDTO,
    StyleTemplateUpdateDTO,
    StyleTemplateResponseDTO,
    StyleTemplateListResponseDTO,
)

router = APIRouter(prefix="/style-templates", tags=["templates"])


@router.post("", response_model=StyleTemplateResponseDTO)
async def create_template(
    template_data: StyleTemplateCreateDTO,
    service: ProjectService = Depends(get_project_service)
):
    """Create a new style template"""
    return await service.create_style_template(template_data)


@router.get("", response_model=List[StyleTemplateListResponseDTO])
async def list_templates(
    project_id: Optional[str] = None,
    service: ProjectService = Depends(get_project_service)
):
    """Get all style templates, optionally filtered by project"""
    return await service.list_style_templates(project_id)


@router.get("/{template_id}", response_model=StyleTemplateResponseDTO)
async def get_template(
    template_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Get a specific style template"""
    return await service.get_style_template(template_id)


@router.put("/{template_id}", response_model=StyleTemplateResponseDTO)
async def update_template(
    template_id: str,
    template_data: StyleTemplateUpdateDTO,
    service: ProjectService = Depends(get_project_service)
):
    """Update a style template"""
    return await service.update_style_template(template_id, template_data)


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Delete a style template"""
    await service.delete_style_template(template_id)
    return {"message": "Template deleted successfully"}


@router.post("/{template_id}/use")
async def use_template(
    template_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Increment use count for a template"""
    await service.increment_template_usage(template_id)
    return {"message": "Use count incremented"}
