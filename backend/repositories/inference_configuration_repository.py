from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from .base_repository import BaseRepository


class InferenceConfigurationRepository(BaseRepository):
    """Repository for inference configuration persistence."""

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def find_by_model_id(
        self, 
        model_id: str,
        configuration_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find configurations by model_id
        
        Args:
            model_id: The model identifier
            configuration_type: Optional filter for 'quality' or 'speed'
            
        Returns:
            List of configuration documents
        """
        query = {"model_id": model_id}
        if configuration_type:
            query["configuration_type"] = configuration_type
        return await self.find_many(query)

    async def find_by_base_model(
        self,
        base_model: str,
        configuration_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find configurations by base_model for secondary grouping
        
        Args:
            base_model: The base model type (e.g., 'sdxl', 'flux_dev', 'pony')
            configuration_type: Optional filter for 'quality' or 'speed'
            
        Returns:
            List of configuration documents
        """
        query = {"base_model": base_model}
        if configuration_type:
            query["configuration_type"] = configuration_type
        return await self.find_many(query)

    async def find_by_model_and_type(
        self,
        model_id: str,
        configuration_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a specific configuration by model_id and type
        
        Args:
            model_id: The model identifier
            configuration_type: Either 'quality' or 'speed'
            
        Returns:
            Configuration document or None
        """
        return await self.find_one({
            "model_id": model_id,
            "configuration_type": configuration_type
        })

    async def find_by_base_model_and_type(
        self,
        base_model: str,
        configuration_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a specific configuration by base_model and type
        
        Args:
            base_model: The base model type
            configuration_type: Either 'quality' or 'speed'
            
        Returns:
            Configuration document or None
        """
        return await self.find_one({
            "base_model": base_model,
            "configuration_type": configuration_type
        })

    async def create_index(self) -> None:
        """Create indexes for efficient querying"""
        await self._collection.create_index("model_id")
        await self._collection.create_index("base_model")
        await self._collection.create_index([
            ("model_id", 1),
            ("configuration_type", 1)
        ], unique=True)
