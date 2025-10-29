from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import DESCENDING

from .base_repository import BaseRepository


class QueueRepository(BaseRepository):
    """Repository for queue job persistence operations."""

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        return await self.find_many({"status": status}, sort=[("priority", DESCENDING), ("created_at", 1)])

    async def find_by_project_id(self, project_id: str) -> List[Dict[str, Any]]:
        return await self.find_many({"project_id": project_id}, sort=[("created_at", DESCENDING)])

    async def find_by_clip_id(self, clip_id: str) -> List[Dict[str, Any]]:
        return await self.find_many({"clip_id": clip_id}, sort=[("created_at", DESCENDING)])

    async def find_pending_jobs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return await self.find_many(
            {"status": {"$in": ["queued", "processing"]}},
            sort=[("priority", DESCENDING), ("created_at", 1)],
            limit=limit
        )

    async def update_status(
        self,
        job_id: str,
        status: str,
        additional_fields: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        updates = {"status": status}
        if additional_fields:
            updates.update(additional_fields)
        return await self.update_by_id(job_id, updates)

    async def delete_by_status(self, status: str) -> int:
        return await self.delete_many({"status": status})

    async def list_all(self, sort_by: Optional[List[tuple[str, int]]] = None) -> List[Dict[str, Any]]:
        if sort_by is None:
            sort_by = [("created_at", DESCENDING)]
        return await self.find_many({}, sort=sort_by)
