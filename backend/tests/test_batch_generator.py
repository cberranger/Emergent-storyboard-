import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from services.batch_generator import BatchGenerator


class TestBatchGenerator:
    
    @pytest.fixture
    def batch_generator(self):
        return BatchGenerator()
    
    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.comfyui_servers = MagicMock()
        db.clips = MagicMock()
        return db
    
    @pytest.fixture
    def mock_client(self):
        client = AsyncMock()
        client.check_connection = AsyncMock(return_value=True)
        client.generate_image = AsyncMock(return_value="http://test.com/image.png")
        client.generate_video = AsyncMock(return_value="http://test.com/video.mp4")
        return client
    
    async def test_generate_batch_images(self, batch_generator, mock_db, mock_client, sample_server):
        clip1 = {
            "id": "clip-1",
            "image_prompt": "test prompt 1"
        }
        clip2 = {
            "id": "clip-2",
            "image_prompt": "test prompt 2"
        }
        
        mock_db.comfyui_servers.find_one = AsyncMock(return_value=sample_server)
        mock_db.clips.find_one = AsyncMock(side_effect=[clip1, clip2])
        
        with patch('dtos.comfyui_dtos.ComfyUIServerDTO', return_value=MagicMock()), \
             patch('services.comfyui_service.ComfyUIClient', return_value=mock_client), \
             patch('services.gallery_manager.gallery_manager') as mock_gallery:
            
            mock_gallery.create_generated_content = MagicMock()
            mock_gallery.add_generated_content = AsyncMock(return_value={"message": "success"})
            
            result = await batch_generator.generate_batch(
                db=mock_db,
                clip_ids=["clip-1", "clip-2"],
                server_id="server-001",
                generation_type="image",
                params={
                    "prompt": "default prompt",
                    "model": "test-model"
                }
            )
            
            assert result["status"] == "completed"
            assert result["total"] == 2
            assert result["completed"] >= 0
            assert len(result["results"]) == 2
    
    async def test_generate_batch_server_not_found(self, batch_generator, mock_db):
        mock_db.comfyui_servers.find_one = AsyncMock(return_value=None)
        
        result = await batch_generator.generate_batch(
            db=mock_db,
            clip_ids=["clip-1"],
            server_id="nonexistent",
            generation_type="image",
            params={}
        )
        
        assert result["status"] == "failed"
        assert "error" in result
    
    async def test_generate_batch_server_offline(self, batch_generator, mock_db, sample_server):
        offline_client = AsyncMock()
        offline_client.check_connection = AsyncMock(return_value=False)
        
        mock_db.comfyui_servers.find_one = AsyncMock(return_value=sample_server)
        
        with patch('dtos.comfyui_dtos.ComfyUIServerDTO', return_value=MagicMock()), \
             patch('services.comfyui_service.ComfyUIClient', return_value=offline_client):
            
            result = await batch_generator.generate_batch(
                db=mock_db,
                clip_ids=["clip-1"],
                server_id="server-001",
                generation_type="image",
                params={}
            )
            
            assert result["status"] == "failed"
            assert "offline" in result["error"].lower()
    
    def test_get_batch_status(self, batch_generator):
        batch_generator.active_batches["batch-123"] = {
            "id": "batch-123",
            "status": "processing",
            "total": 3,
            "completed": 1,
            "failed": 0,
            "results": []
        }
        
        status = batch_generator.get_batch_status("batch-123")
        
        assert status["id"] == "batch-123"
        assert status["status"] == "processing"
        assert status["total"] == 3
    
    def test_get_batch_status_not_found(self, batch_generator):
        status = batch_generator.get_batch_status("nonexistent")
        
        assert "error" in status
        assert "not found" in status["error"].lower()
    
    def test_list_batches(self, batch_generator):
        batch_generator.active_batches["batch-1"] = {
            "id": "batch-1",
            "status": "completed"
        }
        batch_generator.active_batches["batch-2"] = {
            "id": "batch-2",
            "status": "processing"
        }
        
        batches = batch_generator.list_batches()
        
        assert len(batches) == 2
    
    def test_clear_completed_batches(self, batch_generator):
        batch_generator.active_batches["batch-1"] = {
            "id": "batch-1",
            "status": "completed"
        }
        batch_generator.active_batches["batch-2"] = {
            "id": "batch-2",
            "status": "processing"
        }
        batch_generator.active_batches["batch-3"] = {
            "id": "batch-3",
            "status": "failed"
        }
        
        count = batch_generator.clear_completed_batches()
        
        assert count == 2
        assert len(batch_generator.active_batches) == 1
        assert "batch-2" in batch_generator.active_batches
