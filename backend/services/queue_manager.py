"""Smart queue management for ComfyUI servers"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class QueuedJob:
    """Represents a job in the generation queue"""
    id: str
    clip_id: str
    project_id: str
    generation_type: str  # "image" or "video"
    prompt: str
    negative_prompt: str
    model: Optional[str]
    params: Dict[str, Any]
    loras: List[Dict[str, Any]] = field(default_factory=list)
    priority: int = 0  # Higher = more priority
    server_id: Optional[str] = None  # Assigned server
    status: str = "queued"  # queued, processing, completed, failed
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result_url: Optional[str] = None
    estimated_duration: Optional[float] = None  # seconds
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class ServerLoad:
    """Tracks server load and availability"""
    server_id: str
    server_name: str
    is_online: bool
    current_jobs: int = 0
    max_concurrent: int = 1  # Most ComfyUI servers handle 1 job at a time
    queue_length: int = 0
    average_job_time: float = 60.0  # seconds, estimated
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_completed: int = 0
    total_failed: int = 0


class QueueManager:
    """Manages smart queue distribution across ComfyUI servers"""

    def __init__(self):
        self.queue: List[QueuedJob] = []
        self.server_loads: Dict[str, ServerLoad] = {}
        self.processing_jobs: Dict[str, QueuedJob] = {}
        self._processing_lock = asyncio.Lock()

    async def add_job(
        self,
        job_id: str,
        clip_id: str,
        project_id: str,
        generation_type: str,
        prompt: str,
        negative_prompt: str = "",
        model: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        loras: Optional[List[Dict[str, Any]]] = None,
        priority: int = 0,
        preferred_server_id: Optional[str] = None
    ) -> QueuedJob:
        """
        Add a job to the queue

        Args:
            job_id: Unique job ID
            clip_id: Clip to generate for
            project_id: Project ID
            generation_type: "image" or "video"
            prompt: Generation prompt
            negative_prompt: Negative prompt
            model: Model to use
            params: Generation parameters
            loras: LoRA configurations
            priority: Job priority (higher = sooner)
            preferred_server_id: Preferred server (if available)

        Returns:
            QueuedJob object
        """
        job = QueuedJob(
            id=job_id,
            clip_id=clip_id,
            project_id=project_id,
            generation_type=generation_type,
            prompt=prompt,
            negative_prompt=negative_prompt,
            model=model,
            params=params or {},
            loras=loras or [],
            priority=priority,
            server_id=preferred_server_id
        )

        # Estimate job duration based on type
        if generation_type == "video":
            job.estimated_duration = 120.0  # 2 minutes for video
        else:
            job.estimated_duration = 30.0  # 30 seconds for image

        async with self._processing_lock:
            self.queue.append(job)
            # Sort by priority (highest first), then by creation time
            self.queue.sort(key=lambda j: (-j.priority, j.created_at))

        logger.info(f"Added job {job_id} to queue (priority: {priority})")
        return job

    async def register_server(
        self,
        server_id: str,
        server_name: str,
        is_online: bool,
        max_concurrent: int = 1
    ):
        """Register or update a server's status"""
        if server_id not in self.server_loads:
            self.server_loads[server_id] = ServerLoad(
                server_id=server_id,
                server_name=server_name,
                is_online=is_online,
                max_concurrent=max_concurrent
            )
        else:
            load = self.server_loads[server_id]
            load.is_online = is_online
            load.max_concurrent = max_concurrent
            load.last_heartbeat = datetime.now(timezone.utc)

        logger.info(f"Registered server {server_name} ({server_id}): online={is_online}")

    def _get_best_server(self, job: QueuedJob) -> Optional[str]:
        """
        Select the best server for a job based on load balancing

        Returns:
            Server ID or None if no server available
        """
        # If job has preferred server and it's available, use it
        if job.server_id and job.server_id in self.server_loads:
            load = self.server_loads[job.server_id]
            if load.is_online and load.current_jobs < load.max_concurrent:
                return job.server_id

        # Find server with lowest load
        available_servers = [
            (server_id, load)
            for server_id, load in self.server_loads.items()
            if load.is_online and load.current_jobs < load.max_concurrent
        ]

        if not available_servers:
            return None

        # Score servers based on multiple factors
        def score_server(server_tuple) -> float:
            server_id, load = server_tuple
            # Lower score = better
            score = 0.0

            # Current load (0-100 points)
            load_ratio = load.current_jobs / load.max_concurrent
            score += load_ratio * 100

            # Queue length (0-50 points)
            score += min(load.queue_length * 5, 50)

            # Failure rate (0-30 points)
            if load.total_completed + load.total_failed > 0:
                failure_rate = load.total_failed / (load.total_completed + load.total_failed)
                score += failure_rate * 30

            return score

        # Sort by score (lowest first)
        available_servers.sort(key=score_server)
        best_server_id = available_servers[0][0]

        return best_server_id

    async def get_next_job(self, server_id: str) -> Optional[QueuedJob]:
        """
        Get the next job for a specific server

        Args:
            server_id: Server requesting work

        Returns:
            QueuedJob or None if no work available
        """
        async with self._processing_lock:
            # Find first job that can run on this server
            for i, job in enumerate(self.queue):
                if job.status != "queued":
                    continue

                # Check if this server is suitable
                if job.server_id and job.server_id != server_id:
                    # Job wants a specific different server
                    continue

                # Assign job to this server
                job.server_id = server_id
                job.status = "processing"
                job.started_at = datetime.now(timezone.utc)

                # Remove from queue and add to processing
                self.queue.pop(i)
                self.processing_jobs[job.id] = job

                # Update server load
                if server_id in self.server_loads:
                    self.server_loads[server_id].current_jobs += 1
                    self.server_loads[server_id].queue_length = len(
                        [j for j in self.queue if j.server_id == server_id]
                    )

                logger.info(f"Assigned job {job.id} to server {server_id}")
                return job

            return None

    async def assign_pending_jobs(self):
        """Assign jobs to available servers (call periodically)"""
        async with self._processing_lock:
            for job in list(self.queue):
                if job.status != "queued":
                    continue

                best_server = self._get_best_server(job)
                if best_server:
                    job.server_id = best_server
                    logger.info(f"Pre-assigned job {job.id} to server {best_server}")

    async def complete_job(
        self,
        job_id: str,
        success: bool,
        result_url: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        Mark a job as completed

        Args:
            job_id: Job ID
            success: Whether job succeeded
            result_url: Result URL if successful
            error: Error message if failed
        """
        async with self._processing_lock:
            job = self.processing_jobs.get(job_id)
            if not job:
                logger.warning(f"Attempted to complete unknown job {job_id}")
                return

            job.completed_at = datetime.now(timezone.utc)

            if success:
                job.status = "completed"
                job.result_url = result_url

                # Update server stats
                if job.server_id and job.server_id in self.server_loads:
                    load = self.server_loads[job.server_id]
                    load.current_jobs = max(0, load.current_jobs - 1)
                    load.total_completed += 1

                    # Update average job time
                    if job.started_at:
                        duration = (job.completed_at - job.started_at).total_seconds()
                        load.average_job_time = (
                            load.average_job_time * 0.8 + duration * 0.2
                        )

                logger.info(f"Job {job_id} completed successfully")
            else:
                job.error = error
                job.retry_count += 1

                # Update server stats
                if job.server_id and job.server_id in self.server_loads:
                    load = self.server_loads[job.server_id]
                    load.current_jobs = max(0, load.current_jobs - 1)
                    load.total_failed += 1

                # Retry logic
                if job.retry_count < job.max_retries:
                    logger.warning(
                        f"Job {job_id} failed (attempt {job.retry_count}), requeuing"
                    )
                    job.status = "queued"
                    job.server_id = None  # Try different server
                    job.started_at = None
                    self.queue.insert(0, job)  # High priority for retries
                else:
                    logger.error(f"Job {job_id} failed after {job.retry_count} attempts")
                    job.status = "failed"

            # Remove from processing if not retrying
            if job.status != "queued":
                del self.processing_jobs[job_id]

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a job"""
        # Check processing jobs
        if job_id in self.processing_jobs:
            job = self.processing_jobs[job_id]
            return self._job_to_dict(job)

        # Check queue
        for job in self.queue:
            if job.id == job_id:
                return self._job_to_dict(job)

        return None

    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        return {
            "queued_jobs": len(self.queue),
            "processing_jobs": len(self.processing_jobs),
            "servers": {
                server_id: {
                    "name": load.server_name,
                    "online": load.is_online,
                    "current_jobs": load.current_jobs,
                    "max_concurrent": load.max_concurrent,
                    "queue_length": load.queue_length,
                    "average_job_time": load.average_job_time,
                    "total_completed": load.total_completed,
                    "total_failed": load.total_failed
                }
                for server_id, load in self.server_loads.items()
            }
        }

    def get_project_jobs(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all jobs for a specific project"""
        jobs = []

        # Get from queue
        for job in self.queue:
            if job.project_id == project_id:
                jobs.append(self._job_to_dict(job))

        # Get from processing
        for job in self.processing_jobs.values():
            if job.project_id == project_id:
                jobs.append(self._job_to_dict(job))

        return jobs

    def _job_to_dict(self, job: QueuedJob) -> Dict[str, Any]:
        """Convert job to dictionary"""
        return {
            "id": job.id,
            "clip_id": job.clip_id,
            "project_id": job.project_id,
            "generation_type": job.generation_type,
            "status": job.status,
            "priority": job.priority,
            "server_id": job.server_id,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error": job.error,
            "result_url": job.result_url,
            "retry_count": job.retry_count,
            "estimated_duration": job.estimated_duration
        }


# Global instance
queue_manager = QueueManager()
