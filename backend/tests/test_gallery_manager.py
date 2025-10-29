import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from services.gallery_manager import GalleryManager
from dtos.clip_dtos import GeneratedContentDTO
from utils.errors import ClipNotFoundError


class TestGalleryManager:
    
    @pytest.fixture
    def gallery_manager(self):
        return GalleryManager()
    
    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.clips = MagicMock()
        return db
    
    @pytest.fixture
    def sample_generated_content(self):
        return GeneratedContentDTO(
            id="content-123",
            content_type="image",
            url="http://test.com/image.png",
            prompt="test prompt",
            negative_prompt="test negative",
            server_id="server-001",
            server_name="Test Server",
            model_name="test-model",
            model_type="sdxl",
            generation_params={"width": 512, "height": 512},
            is_selected=False,
            created_at=datetime.now(timezone.utc)
        )
    
    def test_initialize_clip_fields(self, gallery_manager):
        clip_data = {
            "id": "clip-123",
            "name": "Test Clip"
        }
        
        result = gallery_manager.initialize_clip_fields(clip_data)
        
        assert "generated_images" in result
        assert "generated_videos" in result
        assert "selected_image_id" in result
        assert "selected_video_id" in result
        assert result["generated_images"] == []
        assert result["generated_videos"] == []
    
    async def test_add_generated_content_image(self, gallery_manager, mock_db, sample_clip, sample_generated_content):
        mock_db.clips.find_one = AsyncMock(return_value=sample_clip)
        mock_db.clips.update_one = AsyncMock()
        
        result = await gallery_manager.add_generated_content(
            db=mock_db,
            clip_id="clip-123",
            new_content=sample_generated_content,
            content_type="image"
        )
        
        assert result["message"] == "Image generated successfully"
        assert result["content"]["id"] == "content-123"
        assert result["total_images"] == 1
        mock_db.clips.update_one.assert_called_once()
    
    async def test_add_generated_content_video(self, gallery_manager, mock_db, sample_clip):
        video_content = GeneratedContentDTO(
            id="video-123",
            content_type="video",
            url="http://test.com/video.mp4",
            prompt="test video",
            negative_prompt="",
            server_id="server-001",
            server_name="Test Server",
            model_name="test-model",
            model_type="svd",
            generation_params={},
            is_selected=False,
            created_at=datetime.now(timezone.utc)
        )
        
        mock_db.clips.find_one = AsyncMock(return_value=sample_clip)
        mock_db.clips.update_one = AsyncMock()
        
        result = await gallery_manager.add_generated_content(
            db=mock_db,
            clip_id="clip-123",
            new_content=video_content,
            content_type="video"
        )
        
        assert result["message"] == "Video generated successfully"
        assert result["content"]["id"] == "video-123"
        assert result["total_videos"] == 1
    
    async def test_add_generated_content_clip_not_found(self, gallery_manager, mock_db, sample_generated_content):
        mock_db.clips.find_one = AsyncMock(return_value=None)
        
        with pytest.raises(ClipNotFoundError):
            await gallery_manager.add_generated_content(
                db=mock_db,
                clip_id="nonexistent",
                new_content=sample_generated_content,
                content_type="image"
            )
    
    async def test_add_generated_content_auto_select_first(self, gallery_manager, mock_db, sample_clip, sample_generated_content):
        mock_db.clips.find_one = AsyncMock(return_value=sample_clip)
        mock_db.clips.update_one = AsyncMock()
        
        result = await gallery_manager.add_generated_content(
            db=mock_db,
            clip_id="clip-123",
            new_content=sample_generated_content,
            content_type="image"
        )
        
        call_args = mock_db.clips.update_one.call_args
        update_data = call_args[0][1]["$set"]
        
        assert update_data["selected_image_id"] == "content-123"
    
    async def test_add_generated_content_invalid_type(self, gallery_manager, mock_db, sample_clip, sample_generated_content):
        sample_generated_content.content_type = "invalid"
        
        mock_db.clips.find_one = AsyncMock(return_value=sample_clip)
        
        with pytest.raises(ValueError):
            await gallery_manager.add_generated_content(
                db=mock_db,
                clip_id="clip-123",
                new_content=sample_generated_content,
                content_type="invalid"
            )
    
    async def test_select_content_image(self, gallery_manager, mock_db):
        clip_with_images = {
            "id": "clip-123",
            "generated_images": [
                {
                    "id": "img-1",
                    "content_type": "image",
                    "url": "http://test.com/img1.png",
                    "is_selected": True
                },
                {
                    "id": "img-2",
                    "content_type": "image",
                    "url": "http://test.com/img2.png",
                    "is_selected": False
                }
            ]
        }
        
        mock_db.clips.find_one = AsyncMock(return_value=clip_with_images)
        mock_db.clips.update_one = AsyncMock()
        
        result = await gallery_manager.select_content(
            db=mock_db,
            clip_id="clip-123",
            content_id="img-2",
            content_type="image"
        )
        
        assert result["message"] == "Selected image updated successfully"
        mock_db.clips.update_one.assert_called_once()
    
    async def test_select_content_video(self, gallery_manager, mock_db):
        clip_with_videos = {
            "id": "clip-123",
            "generated_videos": [
                {
                    "id": "vid-1",
                    "content_type": "video",
                    "url": "http://test.com/vid1.mp4",
                    "is_selected": False
                },
                {
                    "id": "vid-2",
                    "content_type": "video",
                    "url": "http://test.com/vid2.mp4",
                    "is_selected": False
                }
            ]
        }
        
        mock_db.clips.find_one = AsyncMock(return_value=clip_with_videos)
        mock_db.clips.update_one = AsyncMock()
        
        result = await gallery_manager.select_content(
            db=mock_db,
            clip_id="clip-123",
            content_id="vid-2",
            content_type="video"
        )
        
        assert result["message"] == "Selected video updated successfully"
    
    async def test_select_content_clip_not_found(self, gallery_manager, mock_db):
        mock_db.clips.find_one = AsyncMock(return_value=None)
        
        with pytest.raises(ClipNotFoundError):
            await gallery_manager.select_content(
                db=mock_db,
                clip_id="nonexistent",
                content_id="content-123",
                content_type="image"
            )
    
    def test_create_generated_content(self, gallery_manager):
        content = gallery_manager.create_generated_content(
            content_type="image",
            url="http://test.com/image.png",
            prompt="test prompt",
            negative_prompt="test negative",
            server_id="server-001",
            server_name="Test Server",
            model_name="test-model",
            model_type="sdxl",
            generation_params={"width": 512}
        )
        
        assert isinstance(content, GeneratedContentDTO)
        assert content.content_type == "image"
        assert content.url == "http://test.com/image.png"
        assert content.prompt == "test prompt"
        assert content.server_id == "server-001"
        assert content.is_selected is False
    
    async def test_add_generated_content_multiple_images(self, gallery_manager, mock_db):
        clip_with_images = {
            "id": "clip-123",
            "scene_id": "scene-456",
            "name": "Test Clip",
            "length": 5.0,
            "timeline_position": 0.0,
            "order": 1,
            "generated_images": [
                {
                    "id": "img-1",
                    "content_type": "image",
                    "url": "http://test.com/img1.png",
                    "prompt": "test",
                    "negative_prompt": "",
                    "server_id": "server-001",
                    "server_name": "Server",
                    "model_name": "model",
                    "model_type": "sdxl",
                    "generation_params": {},
                    "is_selected": True,
                    "created_at": datetime.now(timezone.utc)
                }
            ],
            "selected_image_id": "img-1",
            "generated_videos": [],
            "selected_video_id": None
        }
        
        new_content = GeneratedContentDTO(
            id="img-2",
            content_type="image",
            url="http://test.com/img2.png",
            prompt="test 2",
            negative_prompt="",
            server_id="server-001",
            server_name="Server",
            model_name="model",
            model_type="sdxl",
            generation_params={},
            is_selected=False,
            created_at=datetime.now(timezone.utc)
        )
        
        mock_db.clips.find_one = AsyncMock(return_value=clip_with_images)
        mock_db.clips.update_one = AsyncMock()
        
        result = await gallery_manager.add_generated_content(
            db=mock_db,
            clip_id="clip-123",
            new_content=new_content,
            content_type="image"
        )
        
        assert result["total_images"] == 2
        
        call_args = mock_db.clips.update_one.call_args
        update_data = call_args[0][1]["$set"]
        assert update_data["selected_image_id"] == "img-1"
