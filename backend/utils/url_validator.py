"""URL validation utilities"""
import logging
import re
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse, unquote
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class URLValidator:
    """Validates URLs for security and format"""

    # Allowed URL schemes
    ALLOWED_SCHEMES = {'http', 'https', 'file'}

    # Patterns for path traversal attacks
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\./',  # ../
        r'\.\.',   # ..
        r'%2e%2e', # URL encoded ..
        r'%252e',  # Double URL encoded .
        r'\.\.\\', # ..\ (Windows)
    ]

    @staticmethod
    def validate_url_format(url: str) -> Tuple[bool, str]:
        """
        Validate URL format

        Args:
            url: URL to validate

        Returns:
            (is_valid, error_message)
        """
        if not url:
            return False, "URL cannot be empty"

        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme and parsed.scheme not in URLValidator.ALLOWED_SCHEMES:
                return False, f"URL scheme '{parsed.scheme}' not allowed. Allowed schemes: {', '.join(URLValidator.ALLOWED_SCHEMES)}"

            # Check for scheme (relative URLs might not have scheme)
            if not parsed.scheme and not url.startswith('/'):
                return False, "URL must have a valid scheme or be a relative path"

            return True, "Valid URL"

        except Exception as e:
            logger.error(f"Error parsing URL: {e}")
            return False, f"Invalid URL format: {str(e)}"

    @staticmethod
    def check_path_traversal(url: str) -> Tuple[bool, str]:
        """
        Check for path traversal attacks

        Args:
            url: URL to check

        Returns:
            (is_safe, error_message)
        """
        # Decode URL to catch encoded traversal attempts
        decoded_url = unquote(url)
        decoded_twice = unquote(decoded_url)

        # Check against patterns
        for pattern in URLValidator.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE) or \
               re.search(pattern, decoded_url, re.IGNORECASE) or \
               re.search(pattern, decoded_twice, re.IGNORECASE):
                return False, f"Potential path traversal detected in URL"

        return True, "URL is safe"

    @staticmethod
    def sanitize_filename(url: str) -> str:
        """
        Extract and sanitize filename from URL

        Args:
            url: URL containing filename

        Returns:
            Sanitized filename
        """
        try:
            parsed = urlparse(url)
            path = Path(unquote(parsed.path))
            filename = path.name

            # Remove dangerous characters
            dangerous_chars = ['..', '/', '\\', '\x00', '<', '>', ':', '"', '|', '?', '*']
            for char in dangerous_chars:
                filename = filename.replace(char, '_')

            # Ensure filename is not empty
            if not filename or filename == '_':
                filename = 'unnamed_file'

            return filename

        except Exception as e:
            logger.error(f"Error sanitizing filename from URL: {e}")
            return 'unnamed_file'

    @staticmethod
    def validate_video_url(url: str) -> None:
        """
        Validate video URL with security checks

        Args:
            url: Video URL to validate

        Raises:
            HTTPException: If URL is invalid or unsafe
        """
        if not url:
            return  # Allow empty URLs (optional field)

        # Check format
        is_valid, message = URLValidator.validate_url_format(url)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid video URL: {message}")

        # Check for path traversal
        is_safe, message = URLValidator.check_path_traversal(url)
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"Unsafe video URL: {message}")

        logger.info(f"Video URL validation passed: {url}")

    @staticmethod
    def validate_image_url(url: str) -> None:
        """
        Validate image URL with security checks

        Args:
            url: Image URL to validate

        Raises:
            HTTPException: If URL is invalid or unsafe
        """
        if not url:
            return  # Allow empty URLs (optional field)

        # Check format
        is_valid, message = URLValidator.validate_url_format(url)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid image URL: {message}")

        # Check for path traversal
        is_safe, message = URLValidator.check_path_traversal(url)
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"Unsafe image URL: {message}")

        logger.info(f"Image URL validation passed: {url}")


url_validator = URLValidator()
