from __future__ import annotations

from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from .base_repository import BaseRepository


class ComfyUIRepository(BaseRepository):
    """Repository for ComfyUI server persistence."""


    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def find_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        normalized = (url or "").rstrip("/")
        return await self.find_one({"url": {"$in": [normalized, f"{normalized}/"]}})

    async def set_active(self, server_id: str, is_active: bool) -> Optional[Dict[str, Any]]:
        return await self.update_by_id(server_id, {"is_active": is_active})