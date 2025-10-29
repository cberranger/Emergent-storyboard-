from fastapi import APIRouter

from . import (
    auth_router,
    characters_router,
    clips_router,
    comfyui_router,
    generation_router,
    health_router,
    media_router,
    projects_router,
    queue_router,
    scenes_router,
    templates_router,
    openai_router,
    admin_router,
)

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router.router)
api_v1_router.include_router(health_router.router)
api_v1_router.include_router(comfyui_router.router)
api_v1_router.include_router(projects_router.router)
api_v1_router.include_router(scenes_router.router)
api_v1_router.include_router(clips_router.router)
api_v1_router.include_router(media_router.router)
api_v1_router.include_router(generation_router.router)
api_v1_router.include_router(queue_router.router)
api_v1_router.include_router(templates_router.router)
api_v1_router.include_router(characters_router.router)
api_v1_router.include_router(openai_router.router)
api_v1_router.include_router(admin_router.router)