import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone
from pathlib import Path


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.projects = MagicMock()
    db.scenes = MagicMock()
    db.clips = MagicMock()
    db.comfyui_servers = MagicMock()
    db.generation_batches = MagicMock()
    db.characters = MagicMock()
    return db


@pytest.fixture
def mock_clip_repository():
    repo = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.find_many = AsyncMock()
    repo.list_by_scene = AsyncMock()
    repo.list_by_project = AsyncMock()
    repo.create = AsyncMock()
    repo.update_by_id = AsyncMock()
    repo.update_prompts = AsyncMock()
    repo.update_timeline_position = AsyncMock()
    return repo


@pytest.fixture
def mock_project_repository():
    repo = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.list_projects = AsyncMock()
    repo.create = AsyncMock()
    repo.update_project = AsyncMock()
    return repo


@pytest.fixture
def mock_scene_repository():
    repo = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.list_by_project = AsyncMock()
    repo.create = AsyncMock()
    repo.update_scene = AsyncMock()
    repo._collection = MagicMock()
    return repo


@pytest.fixture
def mock_comfyui_repository():
    repo = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.list_servers = AsyncMock()
    repo.create = AsyncMock()
    repo.update_server = AsyncMock()
    return repo


@pytest.fixture
def sample_clip():
    return {
        "id": "clip-123",
        "scene_id": "scene-456",
        "name": "Test Clip",
        "lyrics": "Test lyrics",
        "length": 5.0,
        "timeline_position": 0.0,
        "order": 1,
        "image_prompt": "A beautiful landscape",
        "video_prompt": "A moving landscape",
        "generated_images": [],
        "generated_videos": [],
        "selected_image_id": None,
        "selected_video_id": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_project():
    return {
        "id": "project-789",
        "name": "Test Project",
        "description": "Test description",
        "music_file_path": None,
        "music_duration": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_scene():
    return {
        "id": "scene-456",
        "project_id": "project-789",
        "name": "Test Scene",
        "description": "Test scene description",
        "lyrics": "Test lyrics",
        "order": 1,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_server():
    return {
        "id": "server-001",
        "name": "Test Server",
        "url": "http://localhost:8188",
        "server_type": "standard",
        "api_key": None,
        "endpoint_id": None,
        "is_online": True
    }


@pytest.fixture
def sample_generation_params():
    return {
        "width": 512,
        "height": 512,
        "steps": 20,
        "cfg": 8.0,
        "seed": 42,
        "sampler": "euler"
    }


@pytest.fixture
def temp_uploads_dir(tmp_path):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    return uploads
