import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import uuid4

from services.generation_service import GenerationService
from dtos.generation_dtos import GenerationRequestDTO, GenerationParamsDTO, LoraConfigDTO, BatchGenerationRequestDTO
from dtos.clip_dtos import GeneratedContentDTO
from utils.errors import ClipNotFoundError, ServerNotFoundError, ServiceUnavailableError, ValidationError


class TestGenerationService:
    
    @pytest.fixture
    def service(self, mock_clip_repository, mock_project_repository):
        return GenerationService(mock_clip_repository, mock_project_repository)
    
    @pytest.fixture
    def mock_comfyui_client(self):
        client = AsyncMock()
        client.check_connection = AsyncMock(return_value=True)
        client.generate_image = AsyncMock(return_value="http://test.com/image.png")
        client.generate_video = AsyncMock(return_value="http://test.com/video.mp4")
        return client
    
    async def test_generate_image_success(self, service, mock_clip_repository, sample_clip, sample_server, mock_comfyui_client, mock_db):
        mock_clip_repository.find_by_id.return_value = sample_clip
        
        with patch('services.generation_service.db_manager') as mock_db_manager, \
             patch('services.generation_service.ComfyUIClient', return_value=mock_comfyui_client), \
             patch('services.generation_service.gallery_manager') as mock_gallery:
            
            mock_db_manager.db = mock_db
            mock_db.comfyui_servers.find_one = AsyncMock(return_value=sample_server)
            
            mock_content = GeneratedContentDTO(
                id="content-123",
                content_type="image",
                url="http://test.com/image.png",
                prompt="test prompt",
                negative_prompt="",
                server_id="server-001",
                server_name="Test Server",
                model_name="test-model",
                model_type="sdxl",
                generation_params={},
                is_selected=False,
                created_at=datetime.now(timezone.utc)
            )
            
            mock_gallery.create_generated_content.return_value = mock_content
            mock_gallery.add_generated_content.return_value = {
                "message": "Image generated successfully",
                "content": mock_content.model_dump(),
                "total_images": 1
            }
            
            payload = GenerationRequestDTO(
                clip_id="clip-123",
                server_id="server-001",
                generation_type="image",
                prompt="test prompt",
                negative_prompt="",
                model="test-model",
                params=GenerationParamsDTO(width=512, height=512),
                loras=[]
            )
            
            result = await service.generate(payload)
            
            assert result.message == "Image generated successfully"
            assert result.content.url == "http://test.com/image.png"
            mock_comfyui_client.generate_image.assert_called_once()
    
    async def test_generate_clip_not_found(self, service, mock_clip_repository):
        mock_clip_repository.find_by_id.return_value = None
        
        payload = GenerationRequestDTO(
            clip_id="nonexistent",
            server_id="server-001",
            generation_type="image",
            prompt="test",
            model="test-model"
        )
        
        with pytest.raises(ClipNotFoundError):
            await service.generate(payload)
    
    async def test_generate_server_not_found(self, service, mock_clip_repository, sample_clip, mock_db):
        mock_clip_repository.find_by_id.return_value = sample_clip
        
        with patch('services.generation_service.db_manager') as mock_db_manager:
            mock_db_manager.db = mock_db
            mock_db.comfyui_servers.find_one = AsyncMock(return_value=None)
            
            payload = GenerationRequestDTO(
                clip_id="clip-123",
                server_id="nonexistent",
                generation_type="image",
                prompt="test",
                model="test-model"
            )
            
            with pytest.raises(ServerNotFoundError):
                await service.generate(payload)
    
    async def test_generate_server_offline(self, service, mock_clip_repository, sample_clip, sample_server, mock_db):
        mock_clip_repository.find_by_id.return_value = sample_clip
        
        offline_client = AsyncMock()
        offline_client.check_connection = AsyncMock(return_value=False)
        
        with patch('services.generation_service.db_manager') as mock_db_manager, \
             patch('services.generation_service.ComfyUIClient', return_value=offline_client):
            
            mock_db_manager.db = mock_db
            mock_db.comfyui_servers.find_one = AsyncMock(return_value=sample_server)
            
            payload = GenerationRequestDTO(
                clip_id="clip-123",
                server_id="server-001",
                generation_type="image",
                prompt="test",
                model="test-model"
            )
            
            with pytest.raises(ServiceUnavailableError):
                await service.generate(payload)
    
    async def test_generate_video_success(self, service, mock_clip_repository, sample_clip, sample_server, mock_comfyui_client, mock_db):
        mock_clip_repository.find_by_id.return_value = sample_clip
        
        with patch('services.generation_service.db_manager') as mock_db_manager, \
             patch('services.generation_service.ComfyUIClient', return_value=mock_comfyui_client), \
             patch('services.generation_service.gallery_manager') as mock_gallery:
            
            mock_db_manager.db = mock_db
            mock_db.comfyui_servers.find_one = AsyncMock(return_value=sample_server)
            
            mock_content = GeneratedContentDTO(
                id="content-456",
                content_type="video",
                url="http://test.com/video.mp4",
                prompt="test video prompt",
                negative_prompt="",
                server_id="server-001",
                server_name="Test Server",
                model_name="test-model",
                model_type="svd",
                generation_params={},
                is_selected=False,
                created_at=datetime.now(timezone.utc)
            )
            
            mock_gallery.create_generated_content.return_value = mock_content
            mock_gallery.add_generated_content.return_value = {
                "message": "Video generated successfully",
                "content": mock_content.model_dump(),
                "total_videos": 1
            }
            
            payload = GenerationRequestDTO(
                clip_id="clip-123",
                server_id="server-001",
                generation_type="video",
                prompt="test video prompt",
                model="test-model"
            )
            
            result = await service.generate(payload)
            
            assert result.message == "Video generated successfully"
            assert result.content.url == "http://test.com/video.mp4"
            mock_comfyui_client.generate_video.assert_called_once()
    
    async def test_generate_openai_video(self, service, mock_clip_repository, sample_clip, mock_db):
        mock_clip_repository.find_by_id.return_value = sample_clip
        
        with patch('services.generation_service.db_manager') as mock_db_manager, \
             patch('services.generation_service.openai_video_service') as mock_openai, \
             patch('services.generation_service.gallery_manager') as mock_gallery:
            
            mock_db_manager.db = mock_db
            mock_openai.generate_video_to_local.return_value = "/uploads/openai/videos/test.mp4"
            
            mock_content = GeneratedContentDTO(
                id="content-789",
                content_type="video",
                url="/uploads/openai/videos/test.mp4",
                prompt="sora test",
                negative_prompt="",
                server_id="openai",
                server_name="OpenAI Sora",
                model_name="sora-2",
                model_type="sora",
                generation_params={},
                is_selected=False,
                created_at=datetime.now(timezone.utc)
            )
            
            mock_gallery.create_generated_content.return_value = mock_content
            mock_gallery.add_generated_content.return_value = {
                "message": "Video generated successfully",
                "content": mock_content.model_dump(),
                "total_videos": 1
            }
            
            payload = GenerationRequestDTO(
                clip_id="clip-123",
                server_id="openai",
                generation_type="video",
                prompt="sora test",
                model="sora-2",
                params=GenerationParamsDTO(provider="openai")
            )
            
            result = await service.generate(payload)
            
            assert result.message == "Video generated successfully"
            assert "openai" in result.content.url
            mock_openai.generate_video_to_local.assert_called_once()
    
    async def test_generate_batch(self, service, mock_db):
        with patch('services.generation_service.db_manager') as mock_db_manager, \
             patch('services.generation_service.batch_generator') as mock_batch:
            
            mock_db_manager.db = mock_db
            
            batch_info = {
                "id": "batch-123",
                "status": "processing",
                "total": 3,
                "completed": 0,
                "failed": 0,
                "results": [],
                "started_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            mock_batch.generate_batch.return_value = batch_info
            
            payload = BatchGenerationRequestDTO(
                clip_ids=["clip-1", "clip-2", "clip-3"],
                server_id="server-001",
                generation_type="image",
                prompt="batch test",
                model="test-model"
            )
            
            result = await service.generate_batch(payload)
            
            assert result.id == "batch-123"
            assert result.total == 3
            assert result.status == "processing"
            mock_batch.generate_batch.assert_called_once()
    
    async def test_queue_generation(self, service, mock_clip_repository, sample_clip):
        mock_clip_repository.find_by_id.return_value = sample_clip
        
        mock_scene = MagicMock()
        mock_scene.project_id = "project-789"
        service._projects.get_scene = AsyncMock(return_value=mock_scene)
        
        with patch('services.generation_service.queue_manager') as mock_queue:
            mock_job = MagicMock()
            mock_job.id = "job-123"
            mock_job.status = "queued"
            mock_queue.add_job = AsyncMock(return_value=mock_job)
            
            payload = GenerationRequestDTO(
                clip_id="clip-123",
                server_id="server-001",
                generation_type="image",
                prompt="test",
                model="test-model"
            )
            
            result = await service.queue_generation(payload, priority=5)
            
            assert result["job_id"] == "job-123"
            assert result["status"] == "queued"
            mock_queue.add_job.assert_called_once()
    
    def test_get_batch_status(self, service):
        with patch('services.generation_service.batch_generator') as mock_batch:
            batch_status = {
                "id": "batch-123",
                "status": "completed",
                "total": 3,
                "completed": 3,
                "failed": 0,
                "results": [
                    {"clip_id": "clip-1", "status": "completed"},
                    {"clip_id": "clip-2", "status": "completed"},
                    {"clip_id": "clip-3", "status": "completed"}
                ],
                "started_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            mock_batch.get_batch_status.return_value = batch_status
            
            result = service.get_batch_status("batch-123")
            
            assert result.id == "batch-123"
            assert result.status == "completed"
            assert result.total == 3
            assert result.completed == 3
    
    def test_get_batch_status_not_found(self, service):
        with patch('services.generation_service.batch_generator') as mock_batch:
            mock_batch.get_batch_status.return_value = {"error": "Batch not found"}
            
            with pytest.raises(ValidationError):
                service.get_batch_status("nonexistent")
    
    async def test_generate_with_loras(self, service, mock_clip_repository, sample_clip, sample_server, mock_comfyui_client, mock_db):
        mock_clip_repository.find_by_id.return_value = sample_clip
        
        with patch('services.generation_service.db_manager') as mock_db_manager, \
             patch('services.generation_service.ComfyUIClient', return_value=mock_comfyui_client), \
             patch('services.generation_service.gallery_manager') as mock_gallery:
            
            mock_db_manager.db = mock_db
            mock_db.comfyui_servers.find_one = AsyncMock(return_value=sample_server)
            
            mock_content = GeneratedContentDTO(
                id="content-123",
                content_type="image",
                url="http://test.com/image.png",
                prompt="test prompt",
                negative_prompt="",
                server_id="server-001",
                server_name="Test Server",
                model_name="test-model",
                model_type="sdxl",
                generation_params={},
                is_selected=False,
                created_at=datetime.now(timezone.utc)
            )
            
            mock_gallery.create_generated_content.return_value = mock_content
            mock_gallery.add_generated_content.return_value = {
                "message": "Image generated successfully",
                "content": mock_content.model_dump(),
                "total_images": 1
            }
            
            loras = [
                LoraConfigDTO(name="lora1", strength=0.8),
                LoraConfigDTO(name="lora2", strength=0.5)
            ]
            
            payload = GenerationRequestDTO(
                clip_id="clip-123",
                server_id="server-001",
                generation_type="image",
                prompt="test prompt",
                model="test-model",
                loras=loras
            )
            
            result = await service.generate(payload)
            
            assert result.message == "Image generated successfully"
            call_args = mock_comfyui_client.generate_image.call_args
            assert len(call_args.kwargs['loras']) == 2
