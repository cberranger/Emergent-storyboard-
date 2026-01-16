from __future__ import annotations

import asyncio
import logging
from uuid import uuid4
from typing import Dict, List, Optional

from dtos.clip_dtos import GeneratedContentDTO
from dtos.generation_dtos import (
    BatchGenerationJobDTO,
    BatchGenerationRequestDTO,
    BatchGenerationStatusDTO,
    GenerationRequestDTO,
    GenerationResponseDTO,
)
from repositories.clip_repository import ClipRepository
from services.comfyui_service import ComfyUIClient
from services.model_config import detect_model_type, get_model_defaults
from services.project_service import ProjectService
from services.queue_manager import queue_manager
from services.gallery_manager import gallery_manager
from services.batch_generator import batch_generator
from services.openai_video_service import openai_video_service
from utils.errors import (
    ClipNotFoundError,
    GenerationError,
    ServerNotFoundError,
    ServiceUnavailableError,
    ValidationError,
)
from database import db_manager
from dtos.comfyui_dtos import ComfyUIServerDTO

logger = logging.getLogger(__name__)


class GenerationService:
    """Coordinates generation workflows across services and repositories."""

    def __init__(
        self,
        clip_repository: ClipRepository,
        project_service: ProjectService,
    ):
        self._clips = clip_repository
        self._projects = project_service

    async def generate(self, payload: GenerationRequestDTO) -> GenerationResponseDTO:
        db = await self._get_db()
        clip = await self._clips.find_by_id(payload.clip_id)
        if not clip:
            raise ClipNotFoundError(payload.clip_id)

        # Normalize parameters and provider detection
        params = payload.params.model_dump() if payload.params else {}
        generation_params = params or get_model_defaults(payload.model or "unknown")
        provider = (params.get("provider") or "").lower()
        model_lower = (payload.model or "unknown").lower()

        # OpenAI/Sora path: bypass ComfyUI server lookup
        if payload.generation_type == "video" and (provider == "openai" or model_lower.startswith("sora")):
            result_url = await openai_video_service.generate_video_to_local(
                model=payload.model or "sora-2",
                prompt=payload.prompt,
                params=generation_params,
            )

            if not result_url:
                raise GenerationError(payload.generation_type, "No result URL returned from OpenAI")

            model_type = detect_model_type(payload.model or "sora-2")
            new_content = gallery_manager.create_generated_content(
                content_type="video",
                url=result_url,
                prompt=payload.prompt,
                negative_prompt=payload.negative_prompt or "",
                server_id="openai",
                server_name="OpenAI Sora",
                model_name=payload.model or "sora-2",
                model_type=model_type,
                generation_params=generation_params,
            )

            response_data = await gallery_manager.add_generated_content(
                db=db,
                clip_id=payload.clip_id,
                new_content=new_content,
                content_type="video",
            )

            return GenerationResponseDTO(
                message=response_data["message"],
                content=GeneratedContentDTO(**response_data["content"]),
                total_images=response_data.get("total_images"),
                total_videos=response_data.get("total_videos"),
            )

        # Default ComfyUI path (existing behavior)
        server_data = await db.comfyui_servers.find_one({"id": payload.server_id})
        if not server_data:
            raise ServerNotFoundError(payload.server_id)

        server = ComfyUIServerDTO(**server_data)

        client = ComfyUIClient(server)

        if not await client.check_connection():
            raise ServiceUnavailableError("ComfyUI", "Server is offline")

        result_url = None
        if payload.generation_type == "image":
            result_url = await client.generate_image(
                prompt=payload.prompt,
                negative_prompt=payload.negative_prompt or "",
                model=payload.model,
                params=generation_params,
                loras=[l.model_dump() for l in payload.loras] if payload.loras else [],
            )
        elif payload.generation_type == "video":
            result_url = await client.generate_video(
                prompt=payload.prompt,
                negative_prompt=payload.negative_prompt or "",
                model=payload.model,
                params=generation_params,
                loras=[l.model_dump() for l in payload.loras] if payload.loras else [],
            )
        else:
            raise ValidationError("Invalid generation type. Must be 'image' or 'video'")

        if not result_url:
            raise GenerationError(payload.generation_type, "No result URL returned from server")

        model_type = detect_model_type(payload.model or "unknown")
        new_content = gallery_manager.create_generated_content(
            content_type=payload.generation_type,
            url=result_url,
            prompt=payload.prompt,
            negative_prompt=payload.negative_prompt or "",
            server_id=payload.server_id,
            server_name=server.name,
            model_name=payload.model or "unknown",
            model_type=model_type,
            generation_params=generation_params,
        )

        response_data = await gallery_manager.add_generated_content(
            db=db,
            clip_id=payload.clip_id,
            new_content=new_content,
            content_type=payload.generation_type,
        )

        return GenerationResponseDTO(
            message=response_data["message"],
            content=GeneratedContentDTO(**response_data["content"]),
            total_images=response_data.get("total_images"),
            total_videos=response_data.get("total_videos"),
        )

    async def generate_batch(self, payload: BatchGenerationRequestDTO) -> BatchGenerationStatusDTO:
        db = await self._get_db()

        batch_info = await batch_generator.generate_batch(
            db=db,
            clip_ids=payload.clip_ids,
            server_id=payload.server_id,
            generation_type=payload.generation_type,
            params={
                "prompt": payload.prompt,
                "negative_prompt": payload.negative_prompt,
                "model": payload.model,
                "generation_params": payload.params.model_dump() if payload.params else {},
                "loras": [l.model_dump() for l in payload.loras] if payload.loras else [],
            },
        )

        return BatchGenerationStatusDTO(
            id=batch_info["id"],
            status=batch_info["status"],
            total=batch_info["total"],
            completed=batch_info["completed"],
            failed=batch_info["failed"],
            results=[
                BatchGenerationJobDTO(**job) if isinstance(job, dict) else BatchGenerationJobDTO(
                    clip_id="unknown",
                    status="failed",
                    error=str(job),
                )
                for job in batch_info.get("results", [])
            ],
            started_at=batch_info["started_at"],
            updated_at=batch_info["updated_at"],
        )

    async def get_batch_status(self, batch_id: str) -> BatchGenerationStatusDTO:
        status = await batch_generator.get_batch_status(batch_id)
        if "error" in status and status["error"] == "Batch not found":
            raise ValidationError(f"Batch {batch_id} not found")

        return BatchGenerationStatusDTO(
            id=status["id"],
            status=status["status"],
            total=status["total"],
            completed=status["completed"],
            failed=status["failed"],
            results=[
                BatchGenerationJobDTO(**job) if isinstance(job, dict) else BatchGenerationJobDTO(
                    clip_id="unknown",
                    status="failed",
                    error=str(job),
                )
                for job in status.get("results", [])
            ],
            started_at=status["started_at"],
            updated_at=status["updated_at"],
        )

    async def queue_generation(self, payload: GenerationRequestDTO, priority: int = 0) -> Dict:
        clip = await self._clips.find_by_id(payload.clip_id)
        if not clip:
            raise ClipNotFoundError(payload.clip_id)

        scene = await self._projects.get_scene(clip["scene_id"])
        project_id = scene.project_id

        job = await queue_manager.add_job(
            job_id=str(uuid4()),
            clip_id=payload.clip_id,
            project_id=project_id,
            generation_type=payload.generation_type,
            prompt=payload.prompt,
            negative_prompt=payload.negative_prompt or "",
            model=payload.model,
            params=payload.params.model_dump() if payload.params else {},
            loras=[l.model_dump() for l in payload.loras] if payload.loras else [],
            priority=priority,
            preferred_server_id=payload.server_id,
        )
        return {"job_id": job.id, "status": job.status, "message": "Job added to queue"}

    # -------------------------------------------------------------------------
    # Queue Management
    # -------------------------------------------------------------------------
    async def add_to_queue(self, job_request: Any) -> Dict:
        """Add a generation job to the smart queue"""
        from services.queue_manager import queue_manager

        job = await queue_manager.add_job(
            clip_id=job_request.clip_id,
            generation_type=job_request.generation_type,
            prompt=job_request.prompt,
            negative_prompt=job_request.negative_prompt if hasattr(job_request, 'negative_prompt') else None,
            model=job_request.model if hasattr(job_request, 'model') else None,
            params=job_request.params.model_dump() if hasattr(job_request, 'params') and job_request.params else {},
            loras=job_request.loras if hasattr(job_request, 'loras') else [],
            priority=job_request.priority if hasattr(job_request, 'priority') else 0,
            preferred_server_id=job_request.server_id if hasattr(job_request, 'server_id') else None,
        )

        return {
            "job_id": job.id,
            "status": job.status,
            "queue_position": job.queue_position if hasattr(job, 'queue_position') else None,
            "estimated_start_time": job.estimated_start_time if hasattr(job, 'estimated_start_time') else None,
        }

    async def get_queue_status(self) -> Dict:
        """Get overall queue status"""
        from services.queue_manager import queue_manager

        status = await queue_manager.get_queue_status()
        return {
            "total_jobs": status.get("total_jobs", 0),
            "pending_jobs": status.get("pending_jobs", 0),
            "running_jobs": status.get("running_jobs", 0),
            "completed_jobs": status.get("completed_jobs", 0),
            "failed_jobs": status.get("failed_jobs", 0),
            "active_servers": status.get("active_servers", 0),
        }

    async def get_job_status(self, job_id: str) -> Dict:
        """Get status of a specific job"""
        from services.queue_manager import queue_manager

        job = await queue_manager.get_job(job_id)
        if not job:
            raise ResourceNotFoundError("Job", job_id)

        return {
            "job_id": job.id,
            "clip_id": job.clip_id,
            "status": job.status,
            "generation_type": job.generation_type,
            "created_at": job.created_at,
            "started_at": job.started_at if hasattr(job, 'started_at') else None,
            "completed_at": job.completed_at if hasattr(job, 'completed_at') else None,
            "result_url": job.result_url if hasattr(job, 'result_url') else None,
            "error": job.error if hasattr(job, 'error') else None,
            "server_id": job.server_id if hasattr(job, 'server_id') else None,
        }

    async def get_all_jobs(self, status: str = None) -> List[Dict]:
        """Get all queued jobs with optional status filter"""
        from services.queue_manager import queue_manager
        
        all_jobs = queue_manager.get_all_jobs()
        
        if status and status != 'all':
            all_jobs = [j for j in all_jobs if j.status == status]
        
        return [
            {
                "id": j.id,
                "clip_id": j.clip_id,
                "project_id": j.project_id,
                "status": j.status,
                "generation_type": j.generation_type,
                "priority": j.priority,
                "created_at": j.created_at.isoformat() if hasattr(j.created_at, 'isoformat') else j.created_at,
                "started_at": j.started_at.isoformat() if j.started_at and hasattr(j.started_at, 'isoformat') else j.started_at,
                "completed_at": j.completed_at.isoformat() if j.completed_at and hasattr(j.completed_at, 'isoformat') else j.completed_at,
                "result_url": j.result_url,
                "error": j.error,
                "server_id": j.server_id,
                "retry_count": j.retry_count,
            }
            for j in all_jobs
        ]

    async def get_project_jobs(self, project_id: str) -> Dict:
        """Get all queued jobs for a project"""
        from services.queue_manager import queue_manager

        # First get all scenes in the project
        db = await self._get_db()
        scenes = await db.scenes.find({"project_id": project_id}).to_list(None)
        scene_ids = [s["id"] for s in scenes]

        # Get all clips in those scenes
        clips = []
        for scene_id in scene_ids:
            scene_clips = await db.clips.find({"scene_id": scene_id}).to_list(None)
            clips.extend(scene_clips)
        clip_ids = [c["id"] for c in clips]

        # Get jobs for those clips
        all_jobs = await queue_manager.get_all_jobs()
        project_jobs = [j for j in all_jobs if j.clip_id in clip_ids]

        return {
            "project_id": project_id,
            "total_jobs": len(project_jobs),
            "jobs": [
                {
                    "job_id": j.id,
                    "clip_id": j.clip_id,
                    "status": j.status,
                    "generation_type": j.generation_type,
                    "created_at": j.created_at,
                }
                for j in project_jobs
            ],
        }

    async def register_server(self, server_id: str, registration: Any) -> None:
        """Register a server with the queue manager"""
        from services.queue_manager import queue_manager

        await queue_manager.register_server(
            server_id=server_id,
            capabilities=registration.capabilities if hasattr(registration, 'capabilities') else [],
            max_concurrent_jobs=registration.max_concurrent_jobs if hasattr(registration, 'max_concurrent_jobs') else 1,
        )

    async def get_next_job(self, server_id: str) -> Optional[Dict]:
        """Get the next job for a server to process"""
        from services.queue_manager import queue_manager

        job = await queue_manager.get_next_job_for_server(server_id)
        if not job:
            return None

        return {
            "job_id": job.id,
            "clip_id": job.clip_id,
            "generation_type": job.generation_type,
            "prompt": job.prompt,
            "negative_prompt": job.negative_prompt if hasattr(job, 'negative_prompt') else None,
            "model": job.model if hasattr(job, 'model') else None,
            "params": job.params if hasattr(job, 'params') else {},
            "loras": job.loras if hasattr(job, 'loras') else [],
        }

    async def complete_job(
        self, job_id: str, success: bool, result_url: Optional[str] = None, error: Optional[str] = None
    ) -> None:
        """Mark a job as completed"""
        from services.queue_manager import queue_manager

        await queue_manager.complete_job(
            job_id=job_id, success=success, result_url=result_url, error=error
        )

    async def retry_job(self, job_id: str) -> None:
        """Retry a failed or cancelled job"""
        from services.queue_manager import queue_manager
        
        await queue_manager.retry_job(job_id)

    async def cancel_job(self, job_id: str) -> None:
        """Cancel a pending or processing job"""
        from services.queue_manager import queue_manager
        
        await queue_manager.cancel_job(job_id)

    async def delete_job(self, job_id: str) -> None:
        """Delete a job from the queue"""
        from services.queue_manager import queue_manager
        
        await queue_manager.delete_job(job_id)

    async def clear_jobs(self, status: Optional[str] = None) -> int:
        """Clear jobs from the queue with optional status filter"""
        from services.queue_manager import queue_manager
        
        return await queue_manager.clear_jobs(status)

    # -------------------------------------------------------------------------
    # Batch Generation Tracking
    # -------------------------------------------------------------------------
    async def list_batches(self) -> Dict:
        """List all batch jobs"""
        batches = await batch_generator.list_batches()

        return {
            "total": len(batches),
            "batches": [
                {
                    "batch_id": b["id"],
                    "status": b.get("status", "pending"),
                    "total_jobs": b.get("total", 0),
                    "created_at": b.get("started_at"),
                }
                for b in batches
            ],
        }

    @staticmethod
    async def _get_db():
        if db_manager.db is None:
            connected = await db_manager.connect()
            if not connected:
                raise ServiceUnavailableError("Database", "Unable to connect")
        return db_manager.db
