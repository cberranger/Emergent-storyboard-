"""Test queue service integration"""
import pytest
from services.queue_manager import queue_manager
from services.generation_service import GenerationService
from unittest.mock import Mock


@pytest.fixture(autouse=True)
def reset_queue():
    """Reset queue before each test"""
    queue_manager.queue.clear()
    queue_manager.processing_jobs.clear()
    queue_manager.server_loads.clear()
    yield


@pytest.fixture
def generation_service():
    """Create a generation service with mocked dependencies"""
    clip_repo = Mock()
    project_service = Mock()
    return GenerationService(clip_repo, project_service)


@pytest.mark.asyncio
async def test_get_all_jobs_returns_list(generation_service):
    """Test that get_all_jobs returns a list"""
    job1 = await queue_manager.add_job(
        job_id="test-1",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test",
        negative_prompt="",
        priority=1
    )
    
    job2 = await queue_manager.add_job(
        job_id="test-2",
        clip_id="clip-2",
        project_id="proj-1",
        generation_type="video",
        prompt="test2",
        negative_prompt="",
        priority=0
    )
    
    result = await generation_service.get_all_jobs()
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(job, dict) for job in result)
    assert all('id' in job for job in result)
    assert all('status' in job for job in result)


@pytest.mark.asyncio
async def test_get_all_jobs_with_status_filter(generation_service):
    """Test status filtering"""
    job1 = await queue_manager.add_job(
        job_id="test-3",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test",
        negative_prompt="",
        priority=1
    )
    
    job2 = await queue_manager.add_job(
        job_id="test-4",
        clip_id="clip-2",
        project_id="proj-1",
        generation_type="video",
        prompt="test2",
        negative_prompt="",
        priority=0
    )
    
    job2.status = "completed"
    queue_manager.processing_jobs[job2.id] = job2
    queue_manager.queue.remove(job2)
    
    result = await generation_service.get_all_jobs(status="queued")
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['id'] == "test-3"
    assert result[0]['status'] == "queued"


@pytest.mark.asyncio
async def test_retry_job_service(generation_service):
    """Test retry through service"""
    job = await queue_manager.add_job(
        job_id="test-5",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test",
        negative_prompt="",
        priority=1
    )
    
    job.status = "failed"
    job.error = "Test error"
    queue_manager.processing_jobs[job.id] = job
    queue_manager.queue.remove(job)
    
    await generation_service.retry_job("test-5")
    
    assert job.status == "queued"
    assert job.error is None
    assert job in queue_manager.queue


@pytest.mark.asyncio
async def test_cancel_job_service(generation_service):
    """Test cancel through service"""
    job = await queue_manager.add_job(
        job_id="test-6",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test",
        negative_prompt="",
        priority=1
    )
    
    await generation_service.cancel_job("test-6")
    
    assert job.status == "cancelled"
    assert job not in queue_manager.queue


@pytest.mark.asyncio
async def test_delete_job_service(generation_service):
    """Test delete through service"""
    job = await queue_manager.add_job(
        job_id="test-7",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test",
        negative_prompt="",
        priority=1
    )
    
    await generation_service.delete_job("test-7")
    
    assert len(queue_manager.queue) == 0


@pytest.mark.asyncio
async def test_clear_jobs_service(generation_service):
    """Test clear through service"""
    await queue_manager.add_job(
        job_id="test-8",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test",
        negative_prompt="",
        priority=1
    )
    
    job2 = await queue_manager.add_job(
        job_id="test-9",
        clip_id="clip-2",
        project_id="proj-1",
        generation_type="video",
        prompt="test2",
        negative_prompt="",
        priority=0
    )
    
    job2.status = "completed"
    queue_manager.processing_jobs[job2.id] = job2
    queue_manager.queue.remove(job2)
    
    deleted_count = await generation_service.clear_jobs("completed")
    
    assert deleted_count == 1
    assert len(queue_manager.queue) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
