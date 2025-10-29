from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import DESCENDING

from .base_repository import BaseRepository


class BatchRepository(BaseRepository):
    """Repository for batch operation persistence operations."""

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        return await self.find_many({"status": status}, sort=[("created_at", DESCENDING)])

    async def find_active_batches(self) -> List[Dict[str, Any]]:
        return await self.find_many(
            {"status": {"$in": ["pending", "processing"]}},
            sort=[("created_at", DESCENDING)]
        )

    async def update_status(
        self,
        batch_id: str,
        status: str,
        additional_fields: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        updates = {"status": status}
        if additional_fields:
            updates.update(additional_fields)
        return await self.update_by_id(batch_id, updates)

    async def increment_counters(
        self,
        batch_id: str,
        completed: int = 0,
        failed: int = 0
    ) -> Optional[Dict[str, Any]]:
        result = await self._collection.find_one_and_update(
            {"id": batch_id},
            {
                "$inc": {
                    "completed": completed,
                    "failed": failed
                }
            },
            return_document=True
        )
        return result

    async def delete_completed_batches(self) -> int:
        return await self.delete_many({"status": {"$in": ["completed", "failed"]}})

    async def list_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.find_many({}, sort=[("created_at", DESCENDING)], limit=limit)
