from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)
    
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"email": email.lower()})
    
    async def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"username": username.lower()})
    
    async def update_api_keys(
        self,
        user_id: str,
        api_keys: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        return await self.update_by_id(user_id, {"api_keys": api_keys})
