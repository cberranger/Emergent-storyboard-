"""Standardized error handling and responses"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class APIError(HTTPException):
    """Base class for API errors with consistent formatting"""

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code or self._generate_error_code(status_code)
        detail = {
            "error": message,
            "error_code": self.error_code,
            "status_code": status_code
        }
        if details:
            detail["details"] = details

        super().__init__(status_code=status_code, detail=detail)
        logger.error(f"API Error [{self.error_code}]: {message}", extra={"details": details})

    @staticmethod
    def _generate_error_code(status_code: int) -> str:
        """Generate error code from HTTP status"""
        return f"ERR_{status_code}"


# 400 Bad Request Errors
class ValidationError(APIError):
    """Request validation failed"""
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, "VALIDATION_ERROR", details)


class InvalidParameterError(APIError):
    """Invalid parameter provided"""
    def __init__(self, parameter: str, message: Optional[str] = None):
        msg = message or f"Invalid parameter: {parameter}"
        super().__init__(status.HTTP_400_BAD_REQUEST, msg, "INVALID_PARAMETER", {"parameter": parameter})


# 404 Not Found Errors
class ResourceNotFoundError(APIError):
    """Resource not found"""
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            message,
            "RESOURCE_NOT_FOUND",
            {"resource_type": resource_type, "resource_id": resource_id}
        )


class ProjectNotFoundError(ResourceNotFoundError):
    """Project not found"""
    def __init__(self, project_id: str):
        super().__init__("Project", project_id)


class SceneNotFoundError(ResourceNotFoundError):
    """Scene not found"""
    def __init__(self, scene_id: str):
        super().__init__("Scene", scene_id)


class ClipNotFoundError(ResourceNotFoundError):
    """Clip not found"""
    def __init__(self, clip_id: str):
        super().__init__("Clip", clip_id)


class ServerNotFoundError(ResourceNotFoundError):
    """ComfyUI Server not found"""
    def __init__(self, server_id: str):
        super().__init__("ComfyUI Server", server_id)


# 409 Conflict Errors
class ConflictError(APIError):
    """Resource conflict"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_409_CONFLICT, message, "CONFLICT", details)


class DuplicateResourceError(APIError):
    """Resource already exists"""
    def __init__(self, resource_type: str, identifier: str):
        message = f"{resource_type} with identifier '{identifier}' already exists"
        super().__init__(
            status.HTTP_409_CONFLICT,
            message,
            "DUPLICATE_RESOURCE",
            {"resource_type": resource_type, "identifier": identifier}
        )


# 413 Payload Too Large
class FileTooLargeError(APIError):
    """File exceeds size limit"""
    def __init__(self, file_type: str, max_size_mb: float, actual_size_mb: float):
        message = f"{file_type} file exceeds maximum size of {max_size_mb}MB (actual: {actual_size_mb:.2f}MB)"
        super().__init__(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            message,
            "FILE_TOO_LARGE",
            {"file_type": file_type, "max_size_mb": max_size_mb, "actual_size_mb": actual_size_mb}
        )


# 422 Unprocessable Entity
class InvalidFileTypeError(APIError):
    """Invalid file type"""
    def __init__(self, file_type: str, allowed_types: list):
        message = f"Invalid {file_type} file type. Allowed types: {', '.join(allowed_types)}"
        super().__init__(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            message,
            "INVALID_FILE_TYPE",
            {"file_type": file_type, "allowed_types": allowed_types}
        )


# 500 Internal Server Errors
class InternalServerError(APIError):
    """Internal server error"""
    def __init__(self, message: str = "An internal error occurred", details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, message, "INTERNAL_ERROR", details)


class DatabaseError(APIError):
    """Database operation failed"""
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        message = f"Database operation failed: {operation}"
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, message, "DATABASE_ERROR", details)


class ExternalServiceError(APIError):
    """External service error"""
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        msg = f"{service} error: {message}"
        super().__init__(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            msg,
            "EXTERNAL_SERVICE_ERROR",
            {"service": service, **({} if not details else details)}
        )


# 503 Service Unavailable
class ServiceUnavailableError(APIError):
    """Service temporarily unavailable"""
    def __init__(self, service: str, message: Optional[str] = None):
        msg = message or f"{service} is temporarily unavailable"
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, msg, "SERVICE_UNAVAILABLE", {"service": service})


class DatabaseUnavailableError(ServiceUnavailableError):
    """Database unavailable"""
    def __init__(self):
        super().__init__("Database", "Database connection unavailable")


# 507 Insufficient Storage
class InsufficientStorageError(APIError):
    """Insufficient storage space"""
    def __init__(self, required_mb: float, available_mb: float):
        message = f"Insufficient storage space. Required: {required_mb:.1f}MB, Available: {available_mb:.1f}MB"
        super().__init__(
            status.HTTP_507_INSUFFICIENT_STORAGE,
            message,
            "INSUFFICIENT_STORAGE",
            {"required_mb": required_mb, "available_mb": available_mb}
        )


# 409 Conflict Error
class ConflictError(APIError):
    """Resource conflict (e.g., timeline overlap)"""
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_409_CONFLICT, message, "CONFLICT_ERROR", details)


# 500 Server Errors
class ServerError(APIError):
    """Internal server error"""
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, message, "SERVER_ERROR", details)


class GenerationError(ServerError):
    """Content generation failed"""
    def __init__(self, generation_type: str, error: str):
        message = f"{generation_type.capitalize()} generation failed"
        super().__init__(message, {"generation_type": generation_type, "error": error})


# 503 Service Unavailable
class ServiceUnavailableError(APIError):
    """Service temporarily unavailable"""
    def __init__(self, service: str, message: Optional[str] = None):
        msg = message or f"{service} is currently unavailable"
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, msg, "SERVICE_UNAVAILABLE", {"service": service})


# Helper functions for common patterns
def handle_db_error(operation: str, error: Exception) -> None:
    """Handle database errors consistently"""
    logger.error(f"Database error during {operation}: {str(error)}")
    raise DatabaseError(operation, {"error": str(error)})


def require_resource(resource, resource_type: str, resource_id: str):
    """Raise error if resource is None"""
    if resource is None:
        raise ResourceNotFoundError(resource_type, resource_id)
    return resource
