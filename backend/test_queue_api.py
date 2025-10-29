"""Test queue API endpoints integration"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from services.queue_manager import queue_manager


@pytest.fixture(autouse=True)
def reset_queue():
    """Reset queue before each test"""
    queue_manager.queue.clear()
    queue_manager.processing_jobs.clear()
    queue_manager.server_loads.clear()
    yield


@pytest.fixture
def client():
    """Create test client"""
    from server import app
    return TestClient(app)


def test_retry_endpoint(client):
    """Test POST /api/v1/queue/jobs/{job_id}/retry endpoint exists"""
    import asyncio
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    job = loop.run_until_complete(queue_manager.add_job(
        job_id="test-job-retry",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test",
        negative_prompt="",
        priority=1
    ))
    
    job.status = "failed"
    job.error = "Test error"
    queue_manager.processing_jobs[job.id] = job
    queue_manager.queue.remove(job)
    
    response = client.post("/api/v1/queue/jobs/test-job-retry/retry")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Job retry initiated"
    assert data["job_id"] == "test-job-retry"
    
    loop.close()


def test_cancel_endpoint(client):
    """Test POST /api/v1/queue/jobs/{job_id}/cancel endpoint exists"""
    import asyncio
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    job = loop.run_until_complete(queue_manager.add_job(
        job_id="test-job-cancel",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test",
        negative_prompt="",
        priority=1
    ))
    
    response = client.post("/api/v1/queue/jobs/test-job-cancel/cancel")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Job cancelled"
    assert data["job_id"] == "test-job-cancel"
    
    loop.close()


def test_delete_endpoint(client):
    """Test DELETE /api/v1/queue/jobs/{job_id} endpoint exists"""
    import asyncio
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    job = loop.run_until_complete(queue_manager.add_job(
        job_id="test-job-delete",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test",
        negative_prompt="",
        priority=1
    ))
    
    response = client.delete("/api/v1/queue/jobs/test-job-delete")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Job deleted"
    assert data["job_id"] == "test-job-delete"
    
    loop.close()


def test_clear_endpoint(client):
    """Test DELETE /api/v1/queue/clear endpoint exists"""
    import asyncio
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(queue_manager.add_job(
        job_id="test-job-clear-1",
        clip_id="clip-1",
        project_id="proj-1",
        generation_type="image",
        prompt="test",
        negative_prompt="",
        priority=1
    ))
    
    job2 = loop.run_until_complete(queue_manager.add_job(
        job_id="test-job-clear-2",
        clip_id="clip-2",
        project_id="proj-1",
        generation_type="image",
        prompt="test2",
        negative_prompt="",
        priority=1
    ))
    
    job2.status = "completed"
    queue_manager.processing_jobs[job2.id] = job2
    queue_manager.queue.remove(job2)
    
    response = client.delete("/api/v1/queue/clear?status=completed")
    
    assert response.status_code == 200
    data = response.json()
    assert data["deleted_count"] == 1
    assert data["status_filter"] == "completed"
    
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
