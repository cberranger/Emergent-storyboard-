from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from .base_repository import BaseRepository


class ClipRepository(BaseRepository):
    """Repository for clip persistence operations."""

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def list_by_scene(self, scene_id: str) -> List[Dict[str, Any]]:
        return await self.find_many(
            {"scene_id": scene_id},
            sort=[("order", 1)],
        )

    async def list_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        return await self.find_many(
            {"project_id": project_id},
            sort=[("order", 1)],
        )

    async def update_gallery(
        self,
        clip_id: str,
        *,
        generated_images: Optional[List[Dict[str, Any]]] = None,
        generated_videos: Optional[List[Dict[str, Any]]] = None,
        selected_image_id: Optional[str] = None,
        selected_video_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        updates: Dict[str, Any] = {"updated_at": datetime.now(timezone.utc)}
        if generated_images is not None:
            updates["generated_images"] = generated_images
        if generated_videos is not None:
            updates["generated_videos"] = generated_videos
        if selected_image_id is not None:
            updates["selected_image_id"] = selected_image_id
        if selected_video_id is not None:
            updates["selected_video_id"] = selected_video_id

        return await self.update_by_id(clip_id, updates)

    async def update_prompts(
        self,
        clip_id: str,
        image_prompt: Optional[str],
        video_prompt: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        updates = {
            "image_prompt": image_prompt,
            "video_prompt": video_prompt,
            "updated_at": datetime.now(timezone.utc),
        }
        return await self.update_by_id(clip_id, updates)

    async def update_timeline_position(
        self,
        clip_id: str,
        timeline_position: float,
    ) -> Optional[Dict[str, Any]]:
        updates = {
            "timeline_position": timeline_position,
            "updated_at": datetime.now(timezone.utc),
        }
        return await self.update_by_id(clip_id, updates)