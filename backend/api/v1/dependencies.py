from __future__ import annotations

from fastapi import Depends, Header
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from database import get_database
from active_models_service import ActiveModelsService
from repositories.clip_repository import ClipRepository
from repositories.comfyui_repository import ComfyUIRepository
from repositories.project_repository import ProjectRepository
from repositories.scene_repository import SceneRepository
from repositories.user_repository import UserRepository
from services.comfyui_service import ComfyUIService
from services.generation_service import GenerationService
from services.media_service import MediaService
from services.project_service import ProjectService
from services.auth_service import AuthService


async def get_db() -> AsyncIOMotorDatabase:
    return await get_database()


async def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db.users)
    return AuthService(user_repo)


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[dict]:
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")
    try:
        payload = auth_service.decode_token(token)
        if not payload or payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = await auth_service.get_user_by_id(user_id)
        return user
    except Exception:
        # Invalid token or auth service error, return None
        return None


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
    # Initialize ActiveModelsService for ComfyUIService
    from database import db_manager

    # Ensure client is available before using it
    if db_manager.client is None:
        raise HTTPException(status_code=503, detail="Database client not available")
    active_models_service = ActiveModelsService(db_manager.client, db_manager.db_name)
    return ComfyUIService(repository, active_models_service)


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
