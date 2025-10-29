"""ComfyUI server management router for API v1."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from .dependencies import get_comfyui_service, get_current_user_optional
from services.comfyui_service import ComfyUIService
from dtos import (
    ComfyUIServerCreateDTO,
    ComfyUIServerDTO,
    ComfyUIServerInfoDTO,
)

router = APIRouter(prefix="/comfyui", tags=["comfyui"])


@router.post("/servers", response_model=ComfyUIServerDTO)
async def create_server(
    server_data: ComfyUIServerCreateDTO,
    service: ComfyUIService = Depends(get_comfyui_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Register a new ComfyUI server"""
    return await service.create_server(server_data)


@router.get("/servers", response_model=List[ComfyUIServerDTO])
async def list_servers(
    service: ComfyUIService = Depends(get_comfyui_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Get all registered ComfyUI servers"""
    return await service.list_servers()


@router.get("/servers/{server_id}/info", response_model=ComfyUIServerInfoDTO)
async def get_server_info(
    server_id: str,
    service: ComfyUIService = Depends(get_comfyui_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Get detailed information about a ComfyUI server including models and status"""
    return await service.get_server_info(server_id)


@router.put("/servers/{server_id}", response_model=ComfyUIServerDTO)
async def update_server(
    server_id: str,
    server_data: ComfyUIServerCreateDTO,
    service: ComfyUIService = Depends(get_comfyui_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Update a ComfyUI server configuration"""
    return await service.update_server(server_id, server_data)


@router.delete("/servers/{server_id}")
async def delete_server(
    server_id: str,
    service: ComfyUIService = Depends(get_comfyui_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Delete a ComfyUI server"""
    await service.delete_server(server_id)
    return {"message": "Server deleted successfully"}
