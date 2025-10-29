import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from services.project_service import ProjectService
from dtos.project_dtos import ProjectCreateDTO
from dtos.scene_dtos import SceneCreateDTO, SceneUpdateDTO
from dtos.clip_dtos import ClipCreateDTO, ClipUpdateDTO, ClipTimelineUpdateDTO
from utils.errors import ProjectNotFoundError, SceneNotFoundError, ClipNotFoundError, ValidationError


class TestProjectService:
    
    @pytest.fixture
    def service(self, mock_project_repository, mock_scene_repository, mock_clip_repository):
        return ProjectService(mock_project_repository, mock_scene_repository, mock_clip_repository)
    
    async def test_create_project(self, service, mock_project_repository):
        mock_project_repository.create.return_value = None
        
        payload = ProjectCreateDTO(
            name="Test Project",
            description="Test description"
        )
        
        result = await service.create_project(payload)
        
        assert result.name == "Test Project"
        assert result.description == "Test description"
        assert result.id is not None
        mock_project_repository.create.assert_called_once()
    
    async def test_list_projects(self, service, mock_project_repository, sample_project):
        mock_project_repository.list_projects.return_value = [sample_project]
        
        result = await service.list_projects()
        
        assert result.total == 1
        assert len(result.projects) == 1
        assert result.projects[0].name == "Test Project"
    
    async def test_get_project(self, service, mock_project_repository, sample_project):
        mock_project_repository.find_by_id.return_value = sample_project
        
        result = await service.get_project("project-789")
        
        assert result.id == "project-789"
        assert result.name == "Test Project"
    
    async def test_get_project_not_found(self, service, mock_project_repository):
        mock_project_repository.find_by_id.return_value = None
        
        with pytest.raises(ProjectNotFoundError):
            await service.get_project("nonexistent")
    
    async def test_create_scene(self, service, mock_project_repository, mock_scene_repository, sample_project):
        mock_project_repository.find_by_id.return_value = sample_project
        mock_scene_repository.create.return_value = None
        
        payload = SceneCreateDTO(
            project_id="project-789",
            name="Test Scene",
            description="Scene description",
            order=1
        )
        
        result = await service.create_scene(payload)
        
        assert result.name == "Test Scene"
        assert result.project_id == "project-789"
        assert result.id is not None
        mock_scene_repository.create.assert_called_once()
    
    async def test_create_scene_project_not_found(self, service, mock_project_repository):
        mock_project_repository.find_by_id.return_value = None
        
        payload = SceneCreateDTO(
            project_id="nonexistent",
            name="Test Scene",
            order=1
        )
        
        with pytest.raises(ProjectNotFoundError):
            await service.create_scene(payload)
    
    async def test_list_project_scenes(self, service, mock_project_repository, mock_scene_repository, sample_project, sample_scene):
        mock_project_repository.find_by_id.return_value = sample_project
        mock_scene_repository.list_by_project.return_value = [sample_scene]
        
        result = await service.list_project_scenes("project-789")
        
        assert result.total == 1
        assert len(result.scenes) == 1
        assert result.scenes[0].name == "Test Scene"
    
    async def test_get_scene(self, service, mock_scene_repository, sample_scene):
        mock_scene_repository.find_by_id.return_value = sample_scene
        
        result = await service.get_scene("scene-456")
        
        assert result.id == "scene-456"
        assert result.name == "Test Scene"
    
    async def test_get_scene_not_found(self, service, mock_scene_repository):
        mock_scene_repository.find_by_id.return_value = None
        
        with pytest.raises(SceneNotFoundError):
            await service.get_scene("nonexistent")
    
    async def test_update_scene(self, service, mock_scene_repository, sample_scene):
        updated_scene = sample_scene.copy()
        updated_scene["name"] = "Updated Scene"
        mock_scene_repository.update_scene.return_value = updated_scene
        
        payload = SceneUpdateDTO(name="Updated Scene")
        result = await service.update_scene("scene-456", payload)
        
        assert result.name == "Updated Scene"
        mock_scene_repository.update_scene.assert_called_once()
    
    async def test_create_clip(self, service, mock_scene_repository, mock_clip_repository, sample_scene):
        mock_scene_repository.find_by_id.return_value = sample_scene
        mock_clip_repository.create.return_value = None
        
        payload = ClipCreateDTO(
            scene_id="scene-456",
            name="Test Clip",
            length=5.0,
            timeline_position=0.0,
            order=1
        )
        
        result = await service.create_clip(payload)
        
        assert result.name == "Test Clip"
        assert result.scene_id == "scene-456"
        assert result.length == 5.0
        mock_clip_repository.create.assert_called_once()
    
    async def test_create_clip_scene_not_found(self, service, mock_scene_repository):
        mock_scene_repository.find_by_id.return_value = None
        
        payload = ClipCreateDTO(
            scene_id="nonexistent",
            name="Test Clip",
            length=5.0,
            timeline_position=0.0,
            order=1
        )
        
        with pytest.raises(SceneNotFoundError):
            await service.create_clip(payload)
    
    async def test_list_scene_clips(self, service, mock_scene_repository, mock_clip_repository, sample_scene, sample_clip):
        mock_scene_repository.find_by_id.return_value = sample_scene
        mock_clip_repository.list_by_scene.return_value = [sample_clip]
        
        result = await service.list_scene_clips("scene-456")
        
        assert len(result) == 1
        assert result[0].name == "Test Clip"
    
    async def test_get_clip(self, service, mock_clip_repository, sample_clip):
        mock_clip_repository.find_by_id.return_value = sample_clip
        
        result = await service.get_clip("clip-123")
        
        assert result.id == "clip-123"
        assert result.name == "Test Clip"
    
    async def test_get_clip_not_found(self, service, mock_clip_repository):
        mock_clip_repository.find_by_id.return_value = None
        
        with pytest.raises(ClipNotFoundError):
            await service.get_clip("nonexistent")
    
    async def test_update_clip(self, service, mock_clip_repository, sample_clip):
        updated_clip = sample_clip.copy()
        updated_clip["name"] = "Updated Clip"
        
        mock_clip_repository.find_by_id.return_value = sample_clip
        mock_clip_repository.update_by_id.return_value = updated_clip
        
        payload = ClipUpdateDTO(name="Updated Clip")
        result = await service.update_clip("clip-123", payload)
        
        assert result.name == "Updated Clip"
        mock_clip_repository.update_by_id.assert_called_once()
    
    async def test_update_clip_no_fields(self, service, mock_clip_repository, sample_clip):
        mock_clip_repository.find_by_id.return_value = sample_clip
        
        payload = ClipUpdateDTO()
        
        with pytest.raises(ValidationError):
            await service.update_clip("clip-123", payload)
    
    async def test_update_clip_prompts(self, service, mock_clip_repository, sample_clip):
        updated_clip = sample_clip.copy()
        updated_clip["image_prompt"] = "new image prompt"
        updated_clip["video_prompt"] = "new video prompt"
        
        mock_clip_repository.update_prompts.return_value = updated_clip
        
        result = await service.update_clip_prompts("clip-123", "new image prompt", "new video prompt")
        
        assert result.image_prompt == "new image prompt"
        assert result.video_prompt == "new video prompt"
    
    async def test_update_clip_timeline_position(self, service, mock_clip_repository, sample_clip):
        mock_clip_repository.find_by_id.return_value = sample_clip
        mock_clip_repository.find_many.return_value = [sample_clip]
        
        updated_clip = sample_clip.copy()
        updated_clip["timeline_position"] = 5.0
        mock_clip_repository.update_timeline_position.return_value = updated_clip
        
        payload = ClipTimelineUpdateDTO(position=5.0)
        result = await service.update_clip_timeline_position("clip-123", payload)
        
        assert result["clip_id"] == "clip-123"
        assert result["new_position"] == 5.0
        mock_clip_repository.update_timeline_position.assert_called_once()
    
    async def test_update_clip_timeline_overlap(self, service, mock_clip_repository, sample_clip):
        clip1 = sample_clip.copy()
        clip2 = sample_clip.copy()
        clip2["id"] = "clip-456"
        clip2["timeline_position"] = 3.0
        clip2["length"] = 5.0
        
        mock_clip_repository.find_by_id.return_value = clip1
        mock_clip_repository.find_many.return_value = [clip1, clip2]
        
        payload = ClipTimelineUpdateDTO(position=4.0)
        
        with pytest.raises(ValidationError):
            await service.update_clip_timeline_position("clip-123", payload)
    
    async def test_analyze_scene_timeline(self, service, mock_scene_repository, mock_clip_repository, sample_scene, sample_clip):
        mock_scene_repository.find_by_id.return_value = sample_scene
        
        clip1 = sample_clip.copy()
        clip2 = sample_clip.copy()
        clip2["id"] = "clip-456"
        clip2["timeline_position"] = 10.0
        
        mock_clip_repository.find_many.return_value = [clip1, clip2]
        
        result = await service.analyze_scene_timeline("scene-456")
        
        assert result["scene_id"] == "scene-456"
        assert result["total_clips"] == 2
        assert "summary" in result
        assert "overlaps" in result
        assert "gaps" in result
    
    async def test_get_clip_gallery(self, service, mock_clip_repository, sample_clip):
        clip_with_content = sample_clip.copy()
        clip_with_content["generated_images"] = [
            {
                "id": "img-1",
                "content_type": "image",
                "url": "http://test.com/img1.png",
                "prompt": "test",
                "negative_prompt": "",
                "server_id": "server-1",
                "server_name": "Server 1",
                "model_name": "model-1",
                "model_type": "sdxl",
                "generation_params": {},
                "is_selected": True,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        clip_with_content["selected_image_id"] = "img-1"
        
        mock_clip_repository.find_by_id.return_value = clip_with_content
        
        result = await service.get_clip_gallery("clip-123")
        
        assert len(result.images) == 1
        assert result.images[0].id == "img-1"
        assert result.selected_image_id == "img-1"
