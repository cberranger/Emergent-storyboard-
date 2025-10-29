import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from services.queue_manager import QueueManager, QueuedJob, ServerLoad


class TestQueueManager:
    
    @pytest.fixture
    def queue_manager(self):
        return QueueManager()
    
    @pytest.fixture
    def sample_job_params(self):
        return {
            "job_id": "job-123",
            "clip_id": "clip-456",
            "project_id": "project-789",
            "generation_type": "image",
            "prompt": "test prompt",
            "negative_prompt": "test negative",
            "model": "test-model",
            "params": {"width": 512, "height": 512},
            "loras": [],
            "priority": 0
        }
    
    async def test_add_job(self, queue_manager, sample_job_params):
        job = await queue_manager.add_job(**sample_job_params)
        
        assert job.id == "job-123"
        assert job.clip_id == "clip-456"
        assert job.status == "queued"
        assert len(queue_manager.queue) == 1
    
    async def test_add_job_with_priority(self, queue_manager, sample_job_params):
        low_priority_params = sample_job_params.copy()
        low_priority_params["job_id"] = "job-low"
        low_priority_params["priority"] = 0
        
        high_priority_params = sample_job_params.copy()
        high_priority_params["job_id"] = "job-high"
        high_priority_params["priority"] = 10
        
        await queue_manager.add_job(**low_priority_params)
        await queue_manager.add_job(**high_priority_params)
        
        assert queue_manager.queue[0].id == "job-high"
        assert queue_manager.queue[1].id == "job-low"
    
    async def test_register_server(self, queue_manager):
        await queue_manager.register_server(
            server_id="server-001",
            server_name="Test Server",
            is_online=True,
            max_concurrent=2
        )
        
        assert "server-001" in queue_manager.server_loads
        assert queue_manager.server_loads["server-001"].is_online is True
        assert queue_manager.server_loads["server-001"].max_concurrent == 2
    
    async def test_get_next_job(self, queue_manager, sample_job_params):
        await queue_manager.register_server("server-001", "Test Server", True)
        await queue_manager.add_job(**sample_job_params)
        
        job = await queue_manager.get_next_job("server-001")
        
        assert job is not None
        assert job.id == "job-123"
        assert job.status == "processing"
        assert len(queue_manager.queue) == 0
        assert "job-123" in queue_manager.processing_jobs
    
    async def test_get_next_job_no_jobs(self, queue_manager):
        await queue_manager.register_server("server-001", "Test Server", True)
        
        job = await queue_manager.get_next_job("server-001")
        
        assert job is None
    
    async def test_get_next_job_preferred_server(self, queue_manager, sample_job_params):
        await queue_manager.register_server("server-001", "Server 1", True)
        await queue_manager.register_server("server-002", "Server 2", True)
        
        sample_job_params["server_id"] = "server-002"
        await queue_manager.add_job(**sample_job_params)
        
        job = await queue_manager.get_next_job("server-001")
        assert job is None
        
        job = await queue_manager.get_next_job("server-002")
        assert job is not None
        assert job.id == "job-123"
    
    async def test_complete_job_success(self, queue_manager, sample_job_params):
        await queue_manager.register_server("server-001", "Test Server", True)
        await queue_manager.add_job(**sample_job_params)
        
        job = await queue_manager.get_next_job("server-001")
        assert job is not None
        
        await queue_manager.complete_job(
            job_id="job-123",
            success=True,
            result_url="http://test.com/result.png"
        )
        
        assert "job-123" not in queue_manager.processing_jobs
        assert queue_manager.server_loads["server-001"].total_completed == 1
        assert queue_manager.server_loads["server-001"].current_jobs == 0
    
    async def test_complete_job_failure_with_retry(self, queue_manager, sample_job_params):
        await queue_manager.register_server("server-001", "Test Server", True)
        await queue_manager.add_job(**sample_job_params)
        
        job = await queue_manager.get_next_job("server-001")
        
        await queue_manager.complete_job(
            job_id="job-123",
            success=False,
            error="Test error"
        )
        
        assert len(queue_manager.queue) == 1
        assert queue_manager.queue[0].id == "job-123"
        assert queue_manager.queue[0].status == "queued"
        assert queue_manager.queue[0].retry_count == 1
    
    async def test_complete_job_failure_max_retries(self, queue_manager, sample_job_params):
        await queue_manager.register_server("server-001", "Test Server", True)
        await queue_manager.add_job(**sample_job_params)
        
        job = await queue_manager.get_next_job("server-001")
        
        for i in range(3):
            await queue_manager.complete_job("job-123", success=False, error="Test error")
            if i < 2:
                job = await queue_manager.get_next_job("server-001")
        
        assert "job-123" not in queue_manager.processing_jobs
        assert len(queue_manager.queue) == 0
        assert queue_manager.server_loads["server-001"].total_failed == 3
    
    def test_get_job_status(self, queue_manager, sample_job_params):
        import asyncio
        
        async def add_job():
            await queue_manager.add_job(**sample_job_params)
        
        asyncio.run(add_job())
        
        status = queue_manager.get_job_status("job-123")
        
        assert status is not None
        assert status["id"] == "job-123"
        assert status["status"] == "queued"
    
    def test_get_job_status_not_found(self, queue_manager):
        status = queue_manager.get_job_status("nonexistent")
        
        assert status is None
    
    def test_get_queue_status(self, queue_manager):
        import asyncio
        
        async def setup():
            await queue_manager.register_server("server-001", "Test Server", True)
            await queue_manager.add_job(
                job_id="job-1",
                clip_id="clip-1",
                project_id="project-1",
                generation_type="image",
                prompt="test",
                negative_prompt="",
                model="test"
            )
        
        asyncio.run(setup())
        
        status = queue_manager.get_queue_status()
        
        assert status["queued_jobs"] == 1
        assert status["processing_jobs"] == 0
        assert "servers" in status
        assert "server-001" in status["servers"]
    
    def test_get_all_jobs(self, queue_manager):
        import asyncio
        
        async def add_jobs():
            await queue_manager.add_job(
                job_id="job-1",
                clip_id="clip-1",
                project_id="project-1",
                generation_type="image",
                prompt="test",
                negative_prompt="",
                model="test"
            )
            await queue_manager.add_job(
                job_id="job-2",
                clip_id="clip-2",
                project_id="project-1",
                generation_type="video",
                prompt="test",
                negative_prompt="",
                model="test"
            )
        
        asyncio.run(add_jobs())
        
        jobs = queue_manager.get_all_jobs()
        
        assert len(jobs) == 2
    
    def test_get_jobs_by_status(self, queue_manager):
        import asyncio
        
        async def add_jobs():
            await queue_manager.register_server("server-001", "Test Server", True)
            await queue_manager.add_job(
                job_id="job-1",
                clip_id="clip-1",
                project_id="project-1",
                generation_type="image",
                prompt="test",
                negative_prompt="",
                model="test"
            )
            await queue_manager.get_next_job("server-001")
        
        asyncio.run(add_jobs())
        
        queued = queue_manager.get_jobs_by_status("queued")
        processing = queue_manager.get_jobs_by_status("processing")
        
        assert len(queued) == 0
        assert len(processing) == 1
    
    def test_get_project_jobs(self, queue_manager):
        import asyncio
        
        async def add_jobs():
            await queue_manager.add_job(
                job_id="job-1",
                clip_id="clip-1",
                project_id="project-A",
                generation_type="image",
                prompt="test",
                negative_prompt="",
                model="test"
            )
            await queue_manager.add_job(
                job_id="job-2",
                clip_id="clip-2",
                project_id="project-B",
                generation_type="image",
                prompt="test",
                negative_prompt="",
                model="test"
            )
        
        asyncio.run(add_jobs())
        
        project_jobs = queue_manager.get_project_jobs("project-A")
        
        assert len(project_jobs) == 1
        assert project_jobs[0]["project_id"] == "project-A"
    
    async def test_retry_job(self, queue_manager, sample_job_params):
        await queue_manager.register_server("server-001", "Test Server", True)
        await queue_manager.add_job(**sample_job_params)
        
        job = await queue_manager.get_next_job("server-001")
        await queue_manager.complete_job("job-123", success=False, error="Test error")
        
        job = queue_manager.queue[0]
        job.status = "failed"
        
        await queue_manager.retry_job("job-123")
        
        assert queue_manager.queue[0].status == "queued"
        assert queue_manager.queue[0].error is None
    
    async def test_cancel_job_queued(self, queue_manager, sample_job_params):
        await queue_manager.add_job(**sample_job_params)
        
        await queue_manager.cancel_job("job-123")
        
        assert len(queue_manager.queue) == 0
    
    async def test_cancel_job_processing(self, queue_manager, sample_job_params):
        await queue_manager.register_server("server-001", "Test Server", True)
        await queue_manager.add_job(**sample_job_params)
        
        job = await queue_manager.get_next_job("server-001")
        await queue_manager.cancel_job("job-123")
        
        assert "job-123" not in queue_manager.processing_jobs
        assert queue_manager.server_loads["server-001"].current_jobs == 0
    
    async def test_delete_job(self, queue_manager, sample_job_params):
        await queue_manager.add_job(**sample_job_params)
        
        await queue_manager.delete_job("job-123")
        
        assert len(queue_manager.queue) == 0
    
    async def test_clear_jobs(self, queue_manager, sample_job_params):
        await queue_manager.add_job(**sample_job_params)
        
        params2 = sample_job_params.copy()
        params2["job_id"] = "job-456"
        await queue_manager.add_job(**params2)
        
        count = await queue_manager.clear_jobs()
        
        assert count == 2
        assert len(queue_manager.queue) == 0
    
    async def test_clear_jobs_with_status(self, queue_manager, sample_job_params):
        await queue_manager.register_server("server-001", "Test Server", True)
        await queue_manager.add_job(**sample_job_params)
        
        params2 = sample_job_params.copy()
        params2["job_id"] = "job-456"
        await queue_manager.add_job(**params2)
        
        await queue_manager.get_next_job("server-001")
        
        count = await queue_manager.clear_jobs(status="queued")
        
        assert count == 1
        assert len(queue_manager.queue) == 0
        assert len(queue_manager.processing_jobs) == 1
    
    async def test_assign_pending_jobs(self, queue_manager, sample_job_params):
        await queue_manager.register_server("server-001", "Test Server", True)
        await queue_manager.add_job(**sample_job_params)
        
        await queue_manager.assign_pending_jobs()
        
        assert queue_manager.queue[0].server_id == "server-001"
