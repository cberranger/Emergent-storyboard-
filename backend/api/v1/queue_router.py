"""Queue management router for API v1."""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from .dependencies import get_generation_service
from services.generation_service import GenerationService
from dtos import (
    QueueJobRequestDTO,
    QueueJobResponseDTO,
    QueueStatusDTO,
    QueueServerRegistrationDTO,
)

router = APIRouter(prefix="/queue", tags=["queue"])


@router.post("/jobs", response_model=QueueJobResponseDTO)
async def add_to_queue(
    job_request: QueueJobRequestDTO,
    service: GenerationService = Depends(get_generation_service)
):
    """Add a generation job to the smart queue"""
    return await service.add_to_queue(job_request)


@router.get("/jobs")
async def get_all_jobs(
    status: str = None,
    service: GenerationService = Depends(get_generation_service)
):
    """Get all queued jobs with optional status filter"""
    return await service.get_all_jobs(status)


@router.get("/status", response_model=QueueStatusDTO)
async def get_queue_status(service: GenerationService = Depends(get_generation_service)):
    """Get overall queue status"""
    return await service.get_queue_status()


@router.get("/jobs/{job_id}", response_model=QueueJobResponseDTO)
async def get_job_status(
    job_id: str,
    service: GenerationService = Depends(get_generation_service)
):
    """Get status of a specific job"""
    return await service.get_job_status(job_id)


@router.get("/projects/{project_id}/jobs", response_model=Dict[str, Any])
async def get_project_queue(
    project_id: str,
    service: GenerationService = Depends(get_generation_service)
):
    """Get all queued jobs for a project"""
    return await service.get_project_jobs(project_id)


@router.post("/servers/{server_id}/register")
async def register_server_for_queue(
    server_id: str,
    registration: QueueServerRegistrationDTO,
    service: GenerationService = Depends(get_generation_service)
):
    """Register a server with the queue manager"""
    await service.register_server(server_id, registration)
    return {"message": "Server registered successfully"}


@router.get("/servers/{server_id}/next")
async def get_next_job_for_server(
    server_id: str,
    service: GenerationService = Depends(get_generation_service)
):
    """Get the next job for a server to process"""
    return await service.get_next_job(server_id)


@router.post("/jobs/{job_id}/complete")
async def complete_job(
    job_id: str,
    success: bool,
    result_url: str = None,
    error: str = None,
    service: GenerationService = Depends(get_generation_service)
):
    """Mark a job as completed"""
    await service.complete_job(job_id, success, result_url, error)
    return {"message": "Job status updated"}
