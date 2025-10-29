"""Test queue management endpoints"""
import pytest
from services.queue_manager import queue_manager
from services.generation_service import GenerationService
from repositories.clip_repository import ClipRepository
from services.project_service import ProjectService
import asyncio


@pytest.fixture(autouse=True)
def reset_queue():
    """Reset queue before each test"""
    queue_manager.queue.clear()
    queue_manager.processing_jobs.clear()
    queue_manager.server_loads.clear()
    yield


@pytest.mark.asyncio
async def test_add_and_retry_job():
    """Test adding a job and retrying it"""
    job = await queue_manager.add_job(
        job_id="test-job-1",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test prompt",
        negative_prompt="",
        priority=1
    )
    
    assert job.id == "test-job-1"
    assert job.status == "queued"
    
    job.status = "failed"
    job.error = "Test error"
    queue_manager.processing_jobs[job.id] = job
    queue_manager.queue.remove(job)
    
    await queue_manager.retry_job("test-job-1")
    
    assert job.status == "queued"
    assert job.error is None
    assert job.retry_count == 1
    assert job in queue_manager.queue


@pytest.mark.asyncio
async def test_cancel_job():
    """Test cancelling a queued job"""
    job = await queue_manager.add_job(
        job_id="test-job-2",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test prompt",
        negative_prompt="",
        priority=1
    )
    
    assert job.status == "queued"
    
    await queue_manager.cancel_job("test-job-2")
    
    assert job.status == "cancelled"
    assert job not in queue_manager.queue


@pytest.mark.asyncio
async def test_delete_job():
    """Test deleting a job"""
    job = await queue_manager.add_job(
        job_id="test-job-3",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test prompt",
        negative_prompt="",
        priority=1
    )
    
    assert len(queue_manager.queue) == 1
    
    await queue_manager.delete_job("test-job-3")
    
    assert len(queue_manager.queue) == 0


@pytest.mark.asyncio
async def test_clear_jobs_with_status():
    """Test clearing jobs with status filter"""
    job1 = await queue_manager.add_job(
        job_id="test-job-4",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test prompt 1",
        negative_prompt="",
        priority=1
    )
    
    job2 = await queue_manager.add_job(
        job_id="test-job-5",
        clip_id="clip-2",
        project_id="proj-1",
        generation_type="image",
        prompt="test prompt 2",
        negative_prompt="",
        priority=1
    )
    
    job2.status = "completed"
    job2.completed_at = None
    queue_manager.processing_jobs[job2.id] = job2
    queue_manager.queue.remove(job2)
    
    assert len(queue_manager.queue) == 1
    assert len(queue_manager.processing_jobs) == 1
    
    deleted_count = await queue_manager.clear_jobs("completed")
    
    assert deleted_count == 1
    assert len(queue_manager.queue) == 1
    assert len(queue_manager.processing_jobs) == 0


@pytest.mark.asyncio
async def test_clear_all_jobs():
    """Test clearing all jobs without filter"""
    await queue_manager.add_job(
        job_id="test-job-6",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test prompt 1",
        negative_prompt="",
        priority=1
    )
    
    await queue_manager.add_job(
        job_id="test-job-7",
        clip_id="clip-2",
        project_id="proj-1",
        generation_type="image",
        prompt="test prompt 2",
        negative_prompt="",
        priority=1
    )
    
    assert len(queue_manager.queue) == 2
    
    deleted_count = await queue_manager.clear_jobs()
    
    assert deleted_count == 2
    assert len(queue_manager.queue) == 0
    assert len(queue_manager.processing_jobs) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
