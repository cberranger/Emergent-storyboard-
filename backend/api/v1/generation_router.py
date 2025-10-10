"""Content generation router for API v1."""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from .dependencies import get_generation_service
from services.generation_service import GenerationService
from dtos import (
    GenerationRequestDTO,
    GenerationResponseDTO,
    BatchGenerationRequestDTO,
    BatchGenerationStatusDTO,
)

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("", response_model=GenerationResponseDTO)
async def generate_content(
    request: GenerationRequestDTO,
    service: GenerationService = Depends(get_generation_service)
):
    """Generate image or video content for a clip"""
    return await service.generate(request)


@router.post("/batch", response_model=BatchGenerationStatusDTO)
async def generate_batch(
    request: BatchGenerationRequestDTO,
    service: GenerationService = Depends(get_generation_service)
):
    """Generate content for multiple clips"""
    return await service.generate_batch(request)


@router.get("/batch/{batch_id}", response_model=BatchGenerationStatusDTO)
async def get_batch_status(
    batch_id: str,
    service: GenerationService = Depends(get_generation_service)
):
    """Get status of a batch generation job"""
    return await service.get_batch_status(batch_id)


@router.get("/batches", response_model=Dict[str, Any])
async def list_batches(service: GenerationService = Depends(get_generation_service)):
    """List all batch jobs"""
    return await service.list_batches()
