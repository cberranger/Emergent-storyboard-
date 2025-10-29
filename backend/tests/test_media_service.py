import pytest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch
from pathlib import Path
from fastapi import UploadFile

from services.media_service import MediaService
from utils.errors import ProjectNotFoundError, InsufficientStorageError


class TestMediaService:
    
    @pytest.fixture
    def service(self, mock_project_repository, temp_uploads_dir):
        return MediaService(mock_project_repository, temp_uploads_dir)
    
    @pytest.fixture
    def mock_music_file(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test_music.mp3"
        file.file = MagicMock()
        file.content_type = "audio/mpeg"
        return file
    
    @pytest.fixture
    def mock_image_file(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test_face.jpg"
        file.file = MagicMock()
        file.content_type = "image/jpeg"
        return file
    
    async def test_upload_music_success(self, service, mock_project_repository, sample_project, mock_music_file):
        mock_project_repository.find_by_id.return_value = sample_project
        mock_project_repository.update_project.return_value = sample_project
        
        with patch('services.media_service.file_validator') as mock_validator, \
             patch('shutil.copyfileobj'), \
             patch('builtins.open', mock_open()):
            
            mock_validator.validate_music_file = AsyncMock()
            mock_validator.check_disk_space.return_value = (True, "Sufficient space")
            mock_validator.sanitize_filename.return_value = "test_music.mp3"
            
            result = await service.upload_music("project-789", mock_music_file)
            
            assert result.file_path is not None
            assert "test_music.mp3" in result.file_path
            mock_project_repository.update_project.assert_called_once()
    
    async def test_upload_music_project_not_found(self, service, mock_project_repository, mock_music_file):
        mock_project_repository.find_by_id.return_value = None
        
        with pytest.raises(ProjectNotFoundError):
            await service.upload_music("nonexistent", mock_music_file)
    
    async def test_upload_music_insufficient_space(self, service, mock_project_repository, sample_project, mock_music_file):
        mock_project_repository.find_by_id.return_value = sample_project
        
        with patch('services.media_service.file_validator') as mock_validator:
            mock_validator.validate_music_file = AsyncMock()
            mock_validator.check_disk_space.return_value = (False, "Insufficient space")
            
            with pytest.raises(InsufficientStorageError):
                await service.upload_music("project-789", mock_music_file)
    
    async def test_upload_face_image_success(self, service, mock_image_file):
        with patch('services.media_service.file_validator') as mock_validator, \
             patch('shutil.copyfileobj'), \
             patch('builtins.open', mock_open()):
            
            mock_validator.validate_image_file = AsyncMock()
            mock_validator.check_disk_space.return_value = (True, "Sufficient space")
            mock_validator.sanitize_filename.return_value = "test_face.jpg"
            
            result = await service.upload_face_image(mock_image_file)
            
            assert result.file_url is not None
            assert "/uploads/faces/" in result.file_url
            assert result.file_path is not None
    
    async def test_upload_face_image_insufficient_space(self, service, mock_image_file):
        with patch('services.media_service.file_validator') as mock_validator:
            mock_validator.validate_image_file = AsyncMock()
            mock_validator.check_disk_space.return_value = (False, "Insufficient space")
            
            with pytest.raises(InsufficientStorageError):
                await service.upload_face_image(mock_image_file)
    
    async def test_upload_music_validates_file(self, service, mock_project_repository, sample_project, mock_music_file):
        mock_project_repository.find_by_id.return_value = sample_project
        
        with patch('services.media_service.file_validator') as mock_validator, \
             patch('shutil.copyfileobj'), \
             patch('builtins.open', mock_open()):
            
            mock_validator.validate_music_file = AsyncMock()
            mock_validator.check_disk_space.return_value = (True, "Sufficient space")
            mock_validator.sanitize_filename.return_value = "test_music.mp3"
            
            await service.upload_music("project-789", mock_music_file)
            
            mock_validator.validate_music_file.assert_called_once_with(mock_music_file)
    
    async def test_upload_face_image_validates_file(self, service, mock_image_file):
        with patch('services.media_service.file_validator') as mock_validator, \
             patch('shutil.copyfileobj'), \
             patch('builtins.open', mock_open()):
            
            mock_validator.validate_image_file = AsyncMock()
            mock_validator.check_disk_space.return_value = (True, "Sufficient space")
            mock_validator.sanitize_filename.return_value = "test_face.jpg"
            
            await service.upload_face_image(mock_image_file)
            
            mock_validator.validate_image_file.assert_called_once_with(mock_image_file)
