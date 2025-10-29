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

    # CORS Configuration
    @staticmethod
    def get_cors_origins() -> List[str]:
        """Get allowed CORS origins from environment"""
        env_origins = os.environ.get('CORS_ORIGINS', '')

        if env_origins:
            # Split comma-separated origins
            origins = [origin.strip() for origin in env_origins.split(',')]
            return origins

        # Safe defaults for development
        if os.environ.get('ENVIRONMENT', 'development') == 'development':
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://0.0.0.0:3000",
                "*"
            ]

        # Production MUST set CORS_ORIGINS explicitly
        raise ValueError(
            "CORS_ORIGINS environment variable must be set in production. "
            "Example: CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com"
        )

    # Security headers
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
    CORS_MAX_AGE = 600  # Cache preflight requests for 10 minutes


config = Config()
