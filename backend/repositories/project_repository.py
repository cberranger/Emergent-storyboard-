from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from .base_repository import BaseRepository


class ProjectRepository(BaseRepository):
    """Repository for project persistence operations."""

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def list_projects(
        self,
        limit: int = 100,
        *,
        include_scenes: bool = False,
        scenes_collection: Optional[AsyncIOMotorCollection] = None,
    ) -> List[Dict[str, Any]]:
        projects = await self.find_many({}, sort=[("created_at", -1)], limit=limit)
        if include_scenes and scenes_collection:
            project_ids = [project["id"] for project in projects]
            scenes_cursor = scenes_collection.find({"project_id": {"$in": project_ids}})
            scenes_by_project: Dict[str, List[Dict[str, Any]]] = {}
            async for scene in scenes_cursor:
                scenes_by_project.setdefault(scene["project_id"], []).append(scene)

            for project in projects:
                project["scenes"] = sorted(
                    scenes_by_project.get(project["id"], []),
                    key=lambda s: s.get("order", 0),
                )

        return projects

    async def update_project(
        self,
        project_id: str,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        return await self.update_by_id(project_id, updates)