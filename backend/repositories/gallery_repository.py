from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import DESCENDING

from .base_repository import BaseRepository


class GalleryRepository(BaseRepository):
    """Repository for gallery content persistence operations."""

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def find_by_clip_id(self, clip_id: str) -> List[Dict[str, Any]]:
        return await self.find_many({"clip_id": clip_id}, sort=[("created_at", DESCENDING)])

    async def find_by_content_type(self, content_type: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return await self.find_many(
            {"content_type": content_type},
            sort=[("created_at", DESCENDING)],
            limit=limit
        )

    async def find_by_clip_and_type(
        self,
        clip_id: str,
        content_type: str
    ) -> List[Dict[str, Any]]:
        return await self.find_many(
            {"clip_id": clip_id, "content_type": content_type},
            sort=[("created_at", DESCENDING)]
        )

    async def find_selected_content(self, clip_id: str, content_type: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"clip_id": clip_id, "content_type": content_type, "is_selected": True})

    async def mark_as_selected(self, content_id: str) -> Optional[Dict[str, Any]]:
        return await self.update_by_id(content_id, {"is_selected": True})

    async def unmark_selected(self, clip_id: str, content_type: str) -> int:
        result = await self._collection.update_many(
            {"clip_id": clip_id, "content_type": content_type, "is_selected": True},
            {"$set": {"is_selected": False}}
        )
        return result.modified_count

    async def delete_by_clip_id(self, clip_id: str) -> int:
        return await self.delete_many({"clip_id": clip_id})
