import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from pathlib import Path

from services.openai_video_service import OpenAIVideoService
from utils.errors import ServiceUnavailableError, GenerationError


class TestOpenAIVideoService:
    
    @pytest.fixture
    def service_with_key(self):
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            return OpenAIVideoService(api_key='test-key')
    
    @pytest.fixture
    def service_no_key(self):
        with patch.dict('os.environ', {}, clear=True):
            return OpenAIVideoService()
    
    @pytest.fixture
    def mock_video_response(self):
        video = MagicMock()
        video.id = "video-123"
        video.status = "completed"
        return video
    
    def test_init_with_api_key(self):
        service = OpenAIVideoService(api_key="test-key")
        assert service._api_key == "test-key"
        assert service._async_client is not None
    
    def test_init_without_api_key(self):
        with patch.dict('os.environ', {}, clear=True):
            service = OpenAIVideoService()
            assert service._api_key == ""
    
    def test_refresh_api_key(self, service_no_key):
        service_no_key.refresh_api_key("new-key")
        assert service_no_key._api_key == "new-key"
    
    def test_ensure_client_no_key(self, service_no_key):
        with pytest.raises(ServiceUnavailableError):
            service_no_key._ensure_client()
    
    def test_build_create_args_basic(self):
        args = OpenAIVideoService._build_create_args("sora-2", "test prompt", {})
        
        assert args["model"] == "sora-2"
        assert args["prompt"] == "test prompt"
    
    def test_build_create_args_with_size(self):
        params = {"width": 1920, "height": 1080}
        args = OpenAIVideoService._build_create_args("sora-2", "test prompt", params)
        
        assert args["size"] == "1920x1080"
    
    def test_build_create_args_with_duration(self):
        params = {"video_frames": 60, "video_fps": 30}
        args = OpenAIVideoService._build_create_args("sora-2", "test prompt", params)
        
        assert args["seconds"] == 2
    
    def test_build_create_args_with_reference_path(self):
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=b"fake image data")):
            
            params = {"input_reference_path": "uploads/test.jpg"}
            args = OpenAIVideoService._build_create_args("sora-2", "test prompt", params)
            
            assert "input_reference" in args
    
    async def test_create(self, service_with_key, mock_video_response):
        with patch.object(service_with_key._async_client.videos, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_video_response
            
            result = await service_with_key.create("sora-2", "test prompt", {})
            
            assert result.id == "video-123"
            mock_create.assert_called_once()
    
    async def test_create_and_poll(self, service_with_key, mock_video_response):
        with patch.object(service_with_key._async_client.videos, 'create_and_poll', new_callable=AsyncMock) as mock_poll:
            mock_poll.return_value = mock_video_response
            
            result = await service_with_key.create_and_poll("sora-2", "test prompt", {})
            
            assert result.id == "video-123"
            mock_poll.assert_called_once()
    
    async def test_retrieve(self, service_with_key, mock_video_response):
        with patch.object(service_with_key._async_client.videos, 'retrieve', new_callable=AsyncMock) as mock_retrieve:
            mock_retrieve.return_value = mock_video_response
            
            result = await service_with_key.retrieve("video-123")
            
            assert result.id == "video-123"
            mock_retrieve.assert_called_once_with("video-123")
    
    async def test_list(self, service_with_key):
        mock_list = [MagicMock(id="video-1"), MagicMock(id="video-2")]
        
        with patch.object(service_with_key._async_client.videos, 'list', new_callable=AsyncMock) as mock_list_videos:
            mock_list_videos.return_value = mock_list
            
            result = await service_with_key.list()
            
            assert len(result) == 2
            mock_list_videos.assert_called_once()
    
    async def test_delete(self, service_with_key):
        with patch.object(service_with_key._async_client.videos, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = {"deleted": True}
            
            result = await service_with_key.delete("video-123")
            
            assert result["deleted"] is True
            mock_delete.assert_called_once_with("video-123")
    
    async def test_download_content(self, service_with_key):
        mock_content = MagicMock()
        
        with patch.object(service_with_key._async_client.videos, 'download_content', new_callable=AsyncMock) as mock_download:
            mock_download.return_value = mock_content
            
            result = await service_with_key.download_content("video-123", variant="video")
            
            assert result == mock_content
            mock_download.assert_called_once()
    
    async def test_generate_video_to_local_success(self, service_with_key, mock_video_response):
        mock_content = MagicMock()
        mock_content.write_to_file = MagicMock()
        
        with patch.object(service_with_key, 'create_and_poll', new_callable=AsyncMock) as mock_create, \
             patch.object(service_with_key, 'download_content', new_callable=AsyncMock) as mock_download, \
             patch('pathlib.Path.mkdir'), \
             patch('asyncio.to_thread', new_callable=AsyncMock) as mock_thread:
            
            mock_create.return_value = mock_video_response
            mock_download.return_value = mock_content
            
            result = await service_with_key.generate_video_to_local("sora-2", "test prompt", {})
            
            assert "/uploads/openai/videos/video-123.mp4" in result
            mock_create.assert_called_once()
            mock_download.assert_called_once()
    
    async def test_generate_video_to_local_not_completed(self, service_with_key):
        mock_video = MagicMock()
        mock_video.status = "processing"
        mock_video.id = "video-123"
        
        with patch.object(service_with_key, 'create_and_poll', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_video
            
            with pytest.raises(GenerationError):
                await service_with_key.generate_video_to_local("sora-2", "test prompt", {})
    
    async def test_generate_video_to_local_no_video_id(self, service_with_key):
        mock_video = MagicMock()
        mock_video.status = "completed"
        mock_video.id = None
        
        with patch.object(service_with_key, 'create_and_poll', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_video
            
            with pytest.raises(GenerationError):
                await service_with_key.generate_video_to_local("sora-2", "test prompt", {})
    
    async def test_generate_video_to_local_with_params(self, service_with_key, mock_video_response):
        mock_content = MagicMock()
        mock_content.write_to_file = MagicMock()
        
        params = {
            "width": 1920,
            "height": 1080,
            "video_frames": 60,
            "video_fps": 30
        }
        
        with patch.object(service_with_key, 'create_and_poll', new_callable=AsyncMock) as mock_create, \
             patch.object(service_with_key, 'download_content', new_callable=AsyncMock) as mock_download, \
             patch('pathlib.Path.mkdir'), \
             patch('asyncio.to_thread', new_callable=AsyncMock):
            
            mock_create.return_value = mock_video_response
            mock_download.return_value = mock_content
            
            result = await service_with_key.generate_video_to_local("sora-2", "test prompt", params)
            
            assert result is not None
            call_args = mock_create.call_args
            assert call_args.kwargs["params"] == params
