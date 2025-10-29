import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from services.generation_service import GenerationService
from services.project_service import ProjectService
from services.media_service import MediaService
from services.export_service import ExportService
from services.openai_video_service import OpenAIVideoService
from services.queue_manager import QueueManager
from services.gallery_manager import GalleryManager
from services.batch_generator import BatchGenerator


class TestServicesIntegration:
    """Integration tests for all service modules"""
    
    async def test_generation_service_basic_flow(self, mock_clip_repository, mock_project_repository):
        service = GenerationService(mock_clip_repository, mock_project_repository)
        assert service is not None
        assert service._clips == mock_clip_repository
        assert service._projects == mock_project_repository
    
    async def test_project_service_basic_flow(self, mock_project_repository, mock_scene_repository, mock_clip_repository):
        service = ProjectService(mock_project_repository, mock_scene_repository, mock_clip_repository)
        assert service is not None
        assert service._projects == mock_project_repository
        assert service._scenes == mock_scene_repository
        assert service._clips == mock_clip_repository
    
    async def test_media_service_basic_flow(self, mock_project_repository, temp_uploads_dir):
        service = MediaService(mock_project_repository, temp_uploads_dir)
        assert service is not None
        assert service._projects == mock_project_repository
        assert service._uploads_dir == temp_uploads_dir
    
    def test_export_service_basic_flow(self):
        service = ExportService()
        assert service is not None
    
    def test_openai_video_service_basic_flow(self):
        service = OpenAIVideoService(api_key="test-key")
        assert service is not None
        assert service._api_key == "test-key"
    
    def test_queue_manager_basic_flow(self):
        manager = QueueManager()
        assert manager is not None
        assert len(manager.queue) == 0
        assert len(manager.processing_jobs) == 0
    
    def test_gallery_manager_basic_flow(self):
        manager = GalleryManager()
        assert manager is not None
    
    def test_batch_generator_basic_flow(self):
        generator = BatchGenerator()
        assert generator is not None
        assert len(generator.active_batches) == 0
