import os
from typing import List


class Config:
    """Application configuration"""

    # File Upload Configuration
    MAX_MUSIC_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB

    ALLOWED_MUSIC_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/mp3"}
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}

    # Logging Configuration
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.environ.get("LOG_FORMAT", "json")
    LOG_FILE = os.environ.get("LOG_FILE", "backend.log")
    LOG_MAX_BYTES = int(os.environ.get("LOG_MAX_BYTES", str(10 * 1024 * 1024)))
    LOG_BACKUP_COUNT = int(os.environ.get("LOG_BACKUP_COUNT", "5"))
    ENABLE_CONSOLE_LOG = os.environ.get("ENABLE_CONSOLE_LOG", "true").lower() == "true"

    # OpenAI / Sora configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_DEFAULT_VIDEO_MODEL = os.environ.get("OPENAI_DEFAULT_VIDEO_MODEL", "sora-2")

    # JWT Authentication
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "development-secret-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30

    @staticmethod
    def validate_openai_config():
        """Validate OpenAI configuration on startup"""
        if not Config.OPENAI_API_KEY:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                "OPENAI_API_KEY not configured. Sora video generation will be unavailable. "
                "Set OPENAI_API_KEY environment variable to enable Sora integration."
            )

    # CORS Configuration (fully neutralized - never block)
    CORS_ALLOW_ORIGINS = ["*"]
    CORS_ALLOW_ORIGIN_REGEX = ".*"
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]
    CORS_EXPOSE_HEADERS = ["*"]
    CORS_MAX_AGE = 600  # Cache preflight requests for 10 minutes

    @staticmethod
    def get_cors_origins() -> List[str]:
        """Always allow all origins."""
        return ["*"]


config = Config()
