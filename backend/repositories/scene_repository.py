from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from .base_repository import BaseRepository


class SceneRepository(BaseRepository):
    """Repository for scene persistence operations."""

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def list_by_project(
        self,
        project_id: str,
        *,
        include_clips: bool = False,
        clips_collection: Optional[AsyncIOMotorCollection] = None,
    ) -> List[Dict[str, Any]]:
        scenes = await self.find_many(
            {"project_id": project_id},
            sort=[("order", 1)],
        )

        if include_clips and clips_collection:
            scene_ids = [scene["id"] for scene in scenes]
            clips_cursor = clips_collection.find({"scene_id": {"$in": scene_ids}})
            clips_by_scene: Dict[str, List[Dict[str, Any]]] = {}
            async for clip in clips_cursor:
                clips_by_scene.setdefault(clip["scene_id"], []).append(clip)

            for scene in scenes:
                scene["clips"] = sorted(
                    clips_by_scene.get(scene["id"], []),
                    key=lambda c: c.get("order", 0),
                )

        return scenes

    async def update_scene(
        self,
        scene_id: str,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        return await self.update_by_id(scene_id, updates)