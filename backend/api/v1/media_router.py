"""Media upload router for API v1."""
from fastapi import APIRouter, Depends, UploadFile, File

from .dependencies import get_media_service
from services.media_service import MediaService
from dtos import UploadMusicResponseDTO, UploadFaceImageResponseDTO

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/projects/{project_id}/upload-music", response_model=UploadMusicResponseDTO)
async def upload_music(
    project_id: str,
    file: UploadFile = File(...),
    service: MediaService = Depends(get_media_service)
):
    """Upload music file for a project"""
    return await service.upload_music(project_id, file)


@router.post("/upload-face-image", response_model=UploadFaceImageResponseDTO)
async def upload_face_image(
    file: UploadFile = File(...),
    service: MediaService = Depends(get_media_service)
):
    """Upload face image for character/reactor use"""
    return await service.upload_face_image(file)
