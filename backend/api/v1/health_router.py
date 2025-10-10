from fastapi import APIRouter

from database import db_manager

router = APIRouter(tags=["health"])


@router.get("/", summary="API root status")
async def root():
    """Return a simple status payload for the API root."""
    return {"message": "StoryCanvas API is running", "status": "healthy"}


@router.get("/health", summary="Comprehensive health check")
async def health_check():
    """Perform a health check of core dependencies."""
    db_healthy = await db_manager.health_check()
    mongo_url = db_manager.mongo_url or ""
    redacted_url = mongo_url.replace("mongodb://", "mongodb://***@") if mongo_url else ""

    status = {
        "status": "healthy" if db_healthy else "unhealthy",
        "components": {
            "database": {
                "status": "up" if db_healthy else "down",
                "database": db_manager.db_name,
                "url": redacted_url,
            }
        },
    }

    return status