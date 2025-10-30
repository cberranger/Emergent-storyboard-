"""
End-to-end integration tests for critical workflows
Tests use real MongoDB instance (test database) and verify API v1 endpoints
"""
import pytest
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from unittest.mock import AsyncMock

from services.project_service import ProjectService
from services.queue_manager import QueueManager
from repositories.project_repository import ProjectRepository
from repositories.scene_repository import SceneRepository
from repositories.clip_repository import ClipRepository
from repositories.queue_repository import QueueRepository
from dtos import (
    ProjectCreateDTO,
    SceneCreateDTO,
    ClipCreateDTO,
)


@pytest.fixture(scope="function")
async def test_db():
    """Create test MongoDB instance"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['storyboard_test']
    
    yield db
    
    await db['projects'].delete_many({})
    await db['scenes'].delete_many({})
    await db['clips'].delete_many({})
    await db['queue_jobs'].delete_many({})
    client.close()


@pytest.fixture
async def repositories(test_db):
    """Create repository instances with test database"""
    return {
        'project': ProjectRepository(test_db['projects']),
        'scene': SceneRepository(test_db['scenes']),
        'clip': ClipRepository(test_db['clips']),
        'queue': QueueRepository(test_db['queue_jobs']),
    }


@pytest.fixture
async def project_service(repositories):
    """Create project service with test repositories"""
    return ProjectService(
        repositories['project'],
        repositories['scene'],
        repositories['clip']
    )


class TestProjectCreationWorkflow:
    """Test complete project creation workflow"""
    
    async def test_create_project(self, project_service):
        """Test: Create project"""
        project_data = ProjectCreateDTO(
            name="Test Movie",
            description="Integration test project"
        )
        
        project = await project_service.create_project(project_data)
        assert project.id is not None
        assert project.name == "Test Movie"
        assert project.description == "Integration test project"
    
    async def test_create_scene(self, project_service):
        """Test: Create project → Add scene"""
        project_data = ProjectCreateDTO(name="Test Project")
        project = await project_service.create_project(project_data)
        
        scene_data = SceneCreateDTO(
            project_id=project.id,
            name="Opening Scene",
            description="First scene",
            order=0
        )
        scene = await project_service.create_scene(scene_data)
        assert scene.id is not None
        assert scene.project_id == project.id
        assert scene.name == "Opening Scene"
    
    async def test_create_clip(self, project_service):
        """Test: Create project → Scene → Clip"""
        project_data = ProjectCreateDTO(name="Test Project")
        project = await project_service.create_project(project_data)
        
        scene_data = SceneCreateDTO(
            project_id=project.id,
            name="Scene 1",
            order=0
        )
        scene = await project_service.create_scene(scene_data)
        
        clip_data = ClipCreateDTO(
            scene_id=scene.id,
            name="Test Clip",
            image_prompt="A beautiful sunset",
            video_prompt="Camera pans",
            timeline_position=0.0,
            length=5.0
        )
        clip = await project_service.create_clip(clip_data)
        assert clip.id is not None
        assert clip.scene_id == scene.id
        assert clip.name == "Test Clip"


class TestQueueJobLifecycle:
    """Test queue job lifecycle: add, process, complete, retry, cancel"""
    
    async def test_queue_job_add_and_process(self, repositories):
        """Test: Add job to queue → Start processing"""
        queue_manager = QueueManager(repositories['queue'])
        await queue_manager._load_from_db()
        
        job = await queue_manager.add_job(
            job_id="job_001",
            clip_id="clip_123",
            project_id="proj_456",
            generation_type="image",
            prompt="Test prompt",
            negative_prompt="blur",
            model="test.safetensors",
            params={"width": 1024, "height": 576},
            priority=5
        )
        
        assert job.id == "job_001"
        assert len(queue_manager.queue) == 1
        
        await queue_manager.register_server("server_1", "Test Server", True, 1)
        next_job = await queue_manager.get_next_job("server_1")
        
        assert next_job is not None
        assert next_job.id == "job_001"
        assert next_job.status == "processing"
        assert len(queue_manager.processing_jobs) == 1
        assert len(queue_manager.queue) == 0
    
    async def test_queue_job_complete_success(self, repositories):
        """Test: Process job → Complete successfully"""
        queue_manager = QueueManager(repositories['queue'])
        await queue_manager._load_from_db()
        
        job = await queue_manager.add_job(
            job_id="job_002",
            clip_id="clip_456",
            project_id="proj_789",
            generation_type="video",
            prompt="Test video",
            params={}
        )
        
        await queue_manager.register_server("server_1", "Test Server", True, 1)
        next_job = await queue_manager.get_next_job("server_1")
        
        await queue_manager.complete_job(
            job.id,
            success=True,
            result_url="http://example.com/result.mp4"
        )
        
        assert job.id not in queue_manager.processing_jobs
        assert job.status == "completed"
        assert job.result_url == "http://example.com/result.mp4"
    
    async def test_queue_job_complete_failure_with_retry(self, repositories):
        """Test: Process job → Fail → Auto-retry"""
        queue_manager = QueueManager(repositories['queue'])
        await queue_manager._load_from_db()
        
        job = await queue_manager.add_job(
            job_id="job_003",
            clip_id="clip_789",
            project_id="proj_012",
            generation_type="image",
            prompt="Test fail",
            params={}
        )
        
        await queue_manager.register_server("server_1", "Test Server", True, 1)
        next_job = await queue_manager.get_next_job("server_1")
        
        await queue_manager.complete_job(
            job.id,
            success=False,
            error="GPU out of memory"
        )
        
        assert job.status in ["queued", "failed"]
        assert "GPU out of memory" in (job.error or "")
    
    async def test_queue_job_cancel(self, repositories):
        """Test: Queued job → Cancel"""
        queue_manager = QueueManager(repositories['queue'])
        await queue_manager._load_from_db()
        
        job = await queue_manager.add_job(
            job_id="job_005",
            clip_id="clip_cancel",
            project_id="proj_cancel",
            generation_type="video",
            prompt="Cancel test",
            params={}
        )
        
        assert len(queue_manager.queue) == 1
        
        await queue_manager.cancel_job(job.id)
        
        assert job.status == "cancelled"
        assert len(queue_manager.queue) == 0
    
    async def test_queue_max_retries(self, repositories):
        """Test: Job fails multiple times → Max retries reached"""
        queue_manager = QueueManager(repositories['queue'])
        await queue_manager._load_from_db()
        
        job = await queue_manager.add_job(
            job_id="job_006",
            clip_id="clip_maxretry",
            project_id="proj_maxretry",
            generation_type="image",
            prompt="Max retry test",
            params={}
        )
        
        await queue_manager.register_server("server_1", "Test Server", True, 1)
        
        for attempt in range(4):
            next_job = await queue_manager.get_next_job("server_1")
            if next_job:
                await queue_manager.complete_job(next_job.id, success=False, error=f"Attempt {attempt+1} failed")
        
        assert job.status == "failed"
        assert job.retry_count >= 3
    
    async def test_queue_priority_ordering(self, repositories):
        """Test: Jobs are processed by priority"""
        queue_manager = QueueManager(repositories['queue'])
        await queue_manager._load_from_db()
        
        low_priority = await queue_manager.add_job(
            job_id="job_low",
            clip_id="clip_1",
            project_id="proj_1",
            generation_type="image",
            prompt="Low priority",
            params={},
            priority=1
        )
        
        high_priority = await queue_manager.add_job(
            job_id="job_high",
            clip_id="clip_2",
            project_id="proj_2",
            generation_type="image",
            prompt="High priority",
            params={},
            priority=10
        )
        
        await queue_manager.register_server("server_1", "Test Server", True, 1)
        next_job = await queue_manager.get_next_job("server_1")
        
        assert next_job.id == "job_high"


class TestErrorHandlingAndRollback:
    """Test error handling and rollback scenarios"""
    
    async def test_duplicate_project_name_handling(self, project_service):
        """Test: Create project → Try duplicate name → Verify allowed"""
        project_data = ProjectCreateDTO(name="Duplicate Test")
        
        project1 = await project_service.create_project(project_data)
        assert project1.id is not None
        
        project2 = await project_service.create_project(project_data)
        assert project2.id is not None
        assert project2.id != project1.id
    
    async def test_nonexistent_project_access(self, project_service):
        """Test: Access non-existent project → Proper error"""
        with pytest.raises(Exception):
            await project_service.get_project("nonexistent_project_id")
    
    async def test_nonexistent_scene_access(self, project_service):
        """Test: Access non-existent scene → Proper error"""
        with pytest.raises(Exception):
            await project_service.get_scene("nonexistent_scene_id")
    
    async def test_nonexistent_clip_access(self, project_service):
        """Test: Access non-existent clip → Proper error"""
        with pytest.raises(Exception):
            await project_service.get_clip("nonexistent_clip_id")
    
    async def test_create_clip_without_scene(self, project_service):
        """Test: Create clip with non-existent scene → Proper error"""
        clip_data = ClipCreateDTO(
            scene_id="nonexistent_scene",
            name="Orphan Clip",
            image_prompt="Test",
            timeline_position=0.0,
            length=5.0
        )
        
        with pytest.raises(Exception):
            await project_service.create_clip(clip_data)


class TestQueueServerLoadBalancing:
    """Test queue server load balancing"""
    
    async def test_multiple_servers_load_distribution(self, repositories):
        """Test: Multiple servers → Jobs distributed"""
        queue_manager = QueueManager(repositories['queue'])
        await queue_manager._load_from_db()
        
        await queue_manager.register_server("server_1", "Server 1", True, 2)
        await queue_manager.register_server("server_2", "Server 2", True, 2)
        
        for i in range(4):
            await queue_manager.add_job(
                job_id=f"job_{i}",
                clip_id=f"clip_{i}",
                project_id="proj_1",
                generation_type="image",
                prompt=f"Job {i}",
                params={}
            )
        
        job1 = await queue_manager.get_next_job("server_1")
        job2 = await queue_manager.get_next_job("server_2")
        job3 = await queue_manager.get_next_job("server_1")
        job4 = await queue_manager.get_next_job("server_2")
        
        assert job1 is not None
        assert job2 is not None
        assert job3 is not None
        assert job4 is not None
        assert len(set([job1.id, job2.id, job3.id, job4.id])) == 4
    
    async def test_queue_with_multiple_projects(self, repositories):
        """Test: Queue jobs from multiple projects"""
        queue_manager = QueueManager(repositories['queue'])
        await queue_manager._load_from_db()
        
        for i in range(2):
            await queue_manager.add_job(
                job_id=f"proj1_job_{i}",
                clip_id=f"clip_{i}",
                project_id="project_1",
                generation_type="image",
                prompt=f"Project 1 Job {i}",
                params={}
            )
        
        for i in range(2):
            await queue_manager.add_job(
                job_id=f"proj2_job_{i}",
                clip_id=f"clip_{i}",
                project_id="project_2",
                generation_type="image",
                prompt=f"Project 2 Job {i}",
                params={}
            )
        
        project1_queue = queue_manager.get_project_jobs("project_1")
        project2_queue = queue_manager.get_project_jobs("project_2")
        
        assert len(project1_queue) == 2
        assert len(project2_queue) == 2
        
        for job_dict in project1_queue:
            assert job_dict['project_id'] == "project_1"
        
        for job_dict in project2_queue:
            assert job_dict['project_id'] == "project_2"
