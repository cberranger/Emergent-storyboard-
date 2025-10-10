from __future__ import annotations

import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from config import config as app_config
from dtos.media_dtos import UploadFaceImageResponseDTO, UploadMusicResponseDTO
from repositories.project_repository import ProjectRepository
from utils.errors import InsufficientStorageError, ProjectNotFoundError
from utils.file_validator import file_validator

logger = logging.getLogger(__name__)


class MediaService:
    """Handles media upload flows (music, face images, miscellaneous assets)."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        uploads_dir: Path,
    ):
        self._projects = project_repository
        self._uploads_dir = uploads_dir
        self._uploads_dir.mkdir(exist_ok=True)

    async def upload_music(self, project_id: str, file: UploadFile) -> UploadMusicResponseDTO:
        project = await self._projects.find_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)

        await file_validator.validate_music_file(file)

        has_space, message = file_validator.check_disk_space(self._uploads_dir, app_config.MAX_MUSIC_SIZE)
        if not has_space:
            logger.error("Insufficient storage for music upload: %s", message)
            raise InsufficientStorageError(app_config.MAX_MUSIC_SIZE / (1024 * 1024), 0)

        safe_filename = file_validator.sanitize_filename(file.filename)
        file_path = self._uploads_dir / f"{project_id}_{safe_filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        updates = {
            "music_file_path": str(file_path),
            "updated_at": datetime.now(timezone.utc),
        }
        await self._projects.update_project(project_id, updates)

        return UploadMusicResponseDTO(file_path=str(file_path))

    async def upload_face_image(self, file: UploadFile) -> UploadFaceImageResponseDTO:
        await file_validator.validate_image_file(file)

        has_space, message = file_validator.check_disk_space(self._uploads_dir, app_config.MAX_IMAGE_SIZE)
        if not has_space:
            logger.error("Insufficient storage for face upload: %s", message)
            raise InsufficientStorageError(app_config.MAX_IMAGE_SIZE / (1024 * 1024), 0)

        faces_dir = self._uploads_dir / "faces"
        faces_dir.mkdir(exist_ok=True)

        safe_filename = file_validator.sanitize_filename(file.filename)
        extension = safe_filename.split(".")[-1] if "." in safe_filename else "jpg"
        unique_filename = f"face_{datetime.now(timezone.utc).timestamp():.0f}_{safe_filename}"
        file_path = faces_dir / unique_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return UploadFaceImageResponseDTO(
            file_url=f"/uploads/faces/{unique_filename}",
            file_path=str(file_path),
        )