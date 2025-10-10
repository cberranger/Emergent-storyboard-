from __future__ import annotations

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from database import get_database
from repositories.clip_repository import ClipRepository
from repositories.comfyui_repository import ComfyUIRepository
from repositories.project_repository import ProjectRepository
from repositories.scene_repository import SceneRepository
from services.comfyui_service import ComfyUIService
from services.generation_service import GenerationService
from services.media_service import MediaService
from services.project_service import ProjectService


async def get_db() -> AsyncIOMotorDatabase:
    return await get_database()


async def get_project_service(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ProjectService:
    project_repo = ProjectRepository(db.projects)
    scene_repo = SceneRepository(db.scenes)
    clip_repo = ClipRepository(db.clips)
    return ProjectService(project_repo, scene_repo, clip_repo)


async def get_comfyui_service(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ComfyUIService:
    repository = ComfyUIRepository(db.comfyui_servers)
    return ComfyUIService(repository)


async def get_media_service(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> MediaService:
    project_repo = ProjectRepository(db.projects)
    from pathlib import Path

    uploads_dir = Path("uploads")
    return MediaService(project_repo, uploads_dir)


async def get_generation_service(
    db: AsyncIOMotorDatabase = Depends(get_db),
    project_service: ProjectService = Depends(get_project_service),
) -> GenerationService:
    clip_repo = ClipRepository(db.clips)
    return GenerationService(clip_repo, project_service)