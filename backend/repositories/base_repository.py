from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument


class BaseRepository:
    """Generic repository providing common CRUD utilities."""

    def __init__(self, collection: AsyncIOMotorCollection):
        self._collection = collection

    async def create(self, document: Dict[str, Any]) -> Dict[str, Any]:
        await self._collection.insert_one(document)
        return document

    async def find_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        return await self._collection.find_one({"id": document_id})

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._collection.find_one(query)

    async def find_many(
        self,
        query: Dict[str, Any],
        *,
        sort: Optional[List[tuple[str, int]]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        cursor = self._collection.find(query)
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)
        return await cursor.to_list(length=limit or 0)

    async def update_by_id(
        self,
        document_id: str,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        return await self._collection.find_one_and_update(
            {"id": document_id},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )

    async def update_one(
        self,
        query: Dict[str, Any],
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        return await self._collection.find_one_and_update(
            query,
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )

    async def delete_by_id(self, document_id: str) -> bool:
        result = await self._collection.delete_one({"id": document_id})
        return result.deleted_count == 1

    async def delete_many(self, query: Dict[str, Any]) -> int:
        result = await self._collection.delete_many(query)
        return result.deleted_count