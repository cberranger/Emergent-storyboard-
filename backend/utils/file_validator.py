"""File upload validation utilities"""
import logging
import shutil
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException
from config import config

logger = logging.getLogger(__name__)


class FileValidator:
    """Validates uploaded files for size, type, and disk space"""

    @staticmethod
    async def validate_file_size(file: UploadFile, max_size: int, file_type: str) -> None:
        """
        Validate file size without loading entire file into memory

        Args:
            file: UploadFile instance
            max_size: Maximum allowed size in bytes
            file_type: Type description for error messages (e.g., "music", "image")

        Raises:
            HTTPException: If file exceeds max size
        """
        # Read file in chunks to check size
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks

        # Reset file pointer
        await file.seek(0)

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            file_size += len(chunk)

            if file_size > max_size:
                await file.seek(0)  # Reset for potential future use
                max_size_mb = max_size / (1024 * 1024)
                raise HTTPException(
                    status_code=413,
                    detail=f"{file_type.capitalize()} file size exceeds maximum allowed size of {max_size_mb:.1f}MB"
                )

        # Reset file pointer for actual processing
        await file.seek(0)
        logger.info(f"File size validation passed: {file.filename} ({file_size / 1024 / 1024:.2f}MB)")

    @staticmethod
    def validate_file_type(file: UploadFile, allowed_types: set, file_type: str) -> None:
        """
        Validate file content type

        Args:
            file: UploadFile instance
            allowed_types: Set of allowed MIME types
            file_type: Type description for error messages

        Raises:
            HTTPException: If file type not allowed
        """
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {file_type} file type. Allowed types: {', '.join(allowed_types)}"
            )

        logger.info(f"File type validation passed: {file.filename} ({file.content_type})")

    @staticmethod
    def check_disk_space(path: Path, required_bytes: int) -> Tuple[bool, str]:
        """
        Check if sufficient disk space is available

        Args:
            path: Path to check disk space
            required_bytes: Required space in bytes

        Returns:
            (has_space, message)
        """
        try:
            stat = shutil.disk_usage(path)
            available_bytes = stat.free

            if available_bytes < required_bytes:
                required_mb = required_bytes / (1024 * 1024)
                available_mb = available_bytes / (1024 * 1024)
                return False, f"Insufficient disk space. Required: {required_mb:.1f}MB, Available: {available_mb:.1f}MB"

            return True, "Sufficient disk space available"

        except Exception as e:
            logger.error(f"Error checking disk space: {e}")
            return True, "Could not verify disk space"  # Allow upload if check fails

    @staticmethod
    async def validate_music_file(file: UploadFile) -> None:
        """Validate music file upload"""
        # Check file type
        FileValidator.validate_file_type(file, config.ALLOWED_MUSIC_TYPES, "music")

        # Check file size
        await FileValidator.validate_file_size(file, config.MAX_MUSIC_SIZE, "music")

    @staticmethod
    async def validate_image_file(file: UploadFile) -> None:
        """Validate image file upload"""
        # Check file type
        FileValidator.validate_file_type(file, config.ALLOWED_IMAGE_TYPES, "image")

        # Check file size
        await FileValidator.validate_file_size(file, config.MAX_IMAGE_SIZE, "image")

    @staticmethod
    async def validate_video_file(file: UploadFile) -> None:
        """Validate video file upload"""
        # Check file type
        FileValidator.validate_file_type(file, config.ALLOWED_VIDEO_TYPES, "video")

        # Check file size
        await FileValidator.validate_file_size(file, config.MAX_VIDEO_SIZE, "video")

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = Path(filename).name

        # Remove or replace dangerous characters
        dangerous_chars = ['..', '/', '\\', '\x00', '<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # Ensure filename is not empty
        if not filename or filename == '_':
            filename = 'unnamed_file'

        return filename


file_validator = FileValidator()
