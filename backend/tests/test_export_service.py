import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from services.export_service import ExportService


class TestExportService:
    
    @pytest.fixture
    def service(self):
        return ExportService()
    
    @pytest.fixture
    def mock_db_with_data(self, sample_project, sample_scene, sample_clip):
        db = AsyncMock()
        
        clip_with_video = sample_clip.copy()
        clip_with_video["selected_video_id"] = "video-1"
        clip_with_video["generated_videos"] = [{
            "id": "video-1",
            "url": "http://test.com/video.mp4",
            "prompt": "test prompt",
            "model_name": "test-model"
        }]
        
        db.projects.find_one = AsyncMock(return_value=sample_project)
        db.scenes.find = MagicMock()
        db.scenes.find.return_value.sort = MagicMock()
        db.scenes.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[sample_scene])
        
        db.clips.find = MagicMock()
        db.clips.find.return_value.sort = MagicMock()
        db.clips.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[clip_with_video])
        
        return db
    
    async def test_export_final_cut_pro(self, service, mock_db_with_data):
        result = await service.export_final_cut_pro(mock_db_with_data, "project-789")
        
        assert result is not None
        assert "<fcpxml" in result
        assert "version=\"1.9\"" in result
        assert "Test Project" in result
    
    async def test_export_final_cut_pro_project_not_found(self, service):
        db = MagicMock()
        db.projects.find_one = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="Project not found"):
            await service.export_final_cut_pro(db, "nonexistent")
    
    async def test_export_premiere_edl(self, service, mock_db_with_data):
        result = await service.export_premiere_edl(mock_db_with_data, "project-789")
        
        assert result is not None
        assert "TITLE: Test Project" in result
        assert "FCM: NON-DROP FRAME" in result
    
    async def test_export_premiere_edl_project_not_found(self, service):
        db = MagicMock()
        db.projects.find_one = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="Project not found"):
            await service.export_premiere_edl(db, "nonexistent")
    
    async def test_export_davinci_resolve(self, service, mock_db_with_data):
        result = await service.export_davinci_resolve(mock_db_with_data, "project-789")
        
        assert result is not None
        assert "<resolve_timeline" in result
        assert "Test Project" in result
        assert "<track" in result
    
    async def test_export_davinci_resolve_project_not_found(self, service, mock_db_with_data):
        db = AsyncMock()
        db.projects.find_one = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="Project not found"):
            await service.export_davinci_resolve(db, "nonexistent")
    
    async def test_export_json(self, service, mock_db_with_data):
        result = await service.export_json(mock_db_with_data, "project-789")
        
        assert result is not None
        assert isinstance(result, dict)
        assert result["format"] == "storycanvas_v1"
        assert "project" in result
        assert "scenes" in result
        assert "exported_at" in result
    
    async def test_export_json_project_not_found(self, service):
        db = MagicMock()
        db.projects.find_one = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="Project not found"):
            await service.export_json(db, "nonexistent")
    
    def test_seconds_to_timecode(self, service):
        result = service._seconds_to_timecode(90.5, fps=30)
        
        assert result == "00:01:30:15"
    
    def test_seconds_to_timecode_hours(self, service):
        result = service._seconds_to_timecode(3661.0, fps=30)
        
        assert result == "01:01:01:00"
    
    async def test_export_final_cut_pro_multiple_clips(self, service, sample_project, sample_scene):
        db = MagicMock()
        
        clips = [
            {
                "id": f"clip-{i}",
                "name": f"Clip {i}",
                "timeline_position": i * 5.0,
                "length": 5.0,
                "selected_video_id": f"video-{i}",
                "generated_videos": [{
                    "id": f"video-{i}",
                    "url": f"http://test.com/video{i}.mp4",
                    "prompt": f"prompt {i}"
                }]
            }
            for i in range(3)
        ]
        
        db.projects.find_one = AsyncMock(return_value=sample_project)
        db.scenes.find = MagicMock()
        db.scenes.find.return_value.sort = MagicMock()
        db.scenes.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[sample_scene])
        
        db.clips.find = MagicMock()
        db.clips.find.return_value.sort = MagicMock()
        db.clips.find.return_value.sort.return_value.to_list = AsyncMock(return_value=clips)
        
        result = await service.export_final_cut_pro(db, "project-789")
        
        assert "Clip 0" in result
        assert "Clip 1" in result
        assert "Clip 2" in result
