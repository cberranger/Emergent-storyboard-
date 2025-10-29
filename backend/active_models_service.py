"""Service for managing active models on backends"""
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne
from models import BackendModelInfo, BackendInfo, ModelType, ModelSyncStatus


class ActiveModelsService:
    """Service for tracking which models are active on which backends"""
    
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str):
        self.db = db_client[db_name]
        self.active_models_collection = self.db.active_backend_models
        self.backends_collection = self.db.backends
        self.sync_status_collection = self.db.model_sync_status
        
    async def update_backend_models(self, backend_id: str, backend_name: str, backend_url: str, 
                                   models_data: List[Dict[str, Any]]) -> int:
        """
        Update the list of models served by a backend
        
        Args:
            backend_id: Unique ID for the backend
            backend_name: Name of the backend
            backend_url: URL of the backend
            models_data: List of model data from ComfyUI API
            
        Returns:
            Number of models updated
        """
        now = datetime.now(timezone.utc)
        
        # Update backend info
        await self.backends_collection.update_one(
            {"id": backend_id},
            {
                "$set": {
                    "name": backend_name,
                    "url": backend_url,
                    "is_online": True,
                    "last_check": now,
                    "model_count": len(models_data)
                }
            },
            upsert=True
        )
        
        # Prepare bulk update operations
        operations = []
        
        for model in models_data:
            # Determine model type based on path or name
            model_type = self._determine_model_type(model.get("path", ""), model.get("name", ""))
            
            # Create unique ID for this backend-model relationship
            active_model_id = f"{backend_id}_{model.get('name', 'unknown')}"
            
            # Update operation
            operations.append(
                UpdateOne(
                    {"id": active_model_id},
                    {
                        "$set": {
                            "backend_id": backend_id,
                            "backend_name": backend_name,
                            "backend_url": backend_url,
                            "model_id": model.get("id", ""),
                            "model_name": model.get("name", ""),
                            "model_type": model_type.value,
                            "model_path": model.get("path", ""),
                            "model_size": model.get("size"),
                            "is_active": True,
                            "last_seen": now,
                            "model_metadata": model.get("metadata", {}),
                            "first_seen": {
                                "$cond": {
                                    "if": {"$eq": ["$first_seen", None]},
                                    "then": now,
                                    "else": "$first_seen"
                                }
                            }
                        },
                        "$setOnInsert": {
                            "id": active_model_id,
                            "first_seen": now
                        }
                    },
                    upsert=True
                )
            )
        
        # Execute bulk update
        if operations:
            result = await self.active_models_collection.bulk_write(operations)
            print(f"Updated {result.upserted_count} new models, modified {result.modified_count} existing models for backend {backend_name}")
        
        # Mark models not seen in this update as inactive
        await self.active_models_collection.update_many(
            {
                "backend_id": backend_id,
                "last_seen": {"$lt": now}
            },
            {"$set": {"is_active": False}}
        )
        
        return len(models_data)
    
    async def get_active_models(self, backend_id: Optional[str] = None, 
                                model_type: Optional[ModelType] = None) -> List[BackendModelInfo]:
        """
        Get list of active models
        
        Args:
            backend_id: Filter by specific backend (optional)
            model_type: Filter by model type (optional)
            
        Returns:
            List of active backend models
        """
        query = {"is_active": True}
        
        if backend_id:
            query["backend_id"] = backend_id
            
        if model_type:
            query["model_type"] = model_type.value
        
        cursor = self.active_models_collection.find(query)
        models = []
        
        async for doc in cursor:
            # Convert datetime objects to strings for Pydantic
            if "last_seen" in doc and doc["last_seen"]:
                doc["last_seen"] = doc["last_seen"].isoformat()
            if "first_seen" in doc and doc["first_seen"]:
                doc["first_seen"] = doc["first_seen"].isoformat()
                
            models.append(BackendModelInfo(**doc))
        
        return models
    
    async def get_backends(self, online_only: bool = True) -> List[BackendInfo]:
        """
        Get list of backends
        
        Args:
            online_only: Only return online backends
            
        Returns:
            List of backends
        """
        query = {}
        if online_only:
            query["is_online"] = True
        
        cursor = self.backends_collection.find(query)
        backends = []
        
        async for doc in cursor:
            if "last_check" in doc and doc["last_check"]:
                doc["last_check"] = doc["last_check"].isoformat()
            backends.append(BackendInfo(**doc))
        
        return backends
    
    async def sync_model_with_civitai(self, model_id: str, civitai_info: Dict[str, Any], 
                                     match_quality: str) -> bool:
        """
        Update a model with its Civitai information
        
        Args:
            model_id: ID of the model in the database
            civitai_info: Civitai model information
            match_quality: Quality of the match
            
        Returns:
            True if successful
        """
        try:
            # Update the active model records with Civitai info
            await self.active_models_collection.update_many(
                {"model_id": model_id},
                {
                    "$set": {
                        "civitai_model_id": civitai_info.get("modelId"),
                        "civitai_model_name": civitai_info.get("name"),
                        "civitai_match_quality": match_quality
                    }
                }
            )
            
            # Update sync status
            await self.sync_status_collection.update_one(
                {"model_id": model_id},
                {
                    "$set": {
                        "civitai_model_id": civitai_info.get("modelId"),
                        "sync_status": "synced",
                        "last_sync_success": datetime.now(timezone.utc),
                        "sync_error": None
                    },
                    "$setOnInsert": {
                        "model_id": model_id,
                        "last_sync_attempt": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
            return True
        except Exception as e:
            print(f"Error syncing model {model_id} with Civitai: {e}")
            return False
    
    async def get_models_for_sync(self, limit: int = 100) -> List[str]:
        """
        Get models that need to be synced with Civitai
        
        Args:
            limit: Maximum number of models to return
            
        Returns:
            List of model IDs that need syncing
        """
        # Get models that haven't been synced or have failed sync
        pipeline = [
            {
                "$match": {
                    "is_active": True,
                    "$or": [
                        {"civitai_model_id": None},
                        {"civitai_model_id": ""}
                    ]
                }
            },
            {"$limit": limit},
            {"$project": {"model_id": 1, "_id": 0}}
        ]
        
        cursor = self.active_models_collection.aggregate(pipeline)
        model_ids = []
        
        async for doc in cursor:
            model_ids.append(doc["model_id"])
        
        return model_ids
    
    def _determine_model_type(self, path: str, name: str) -> ModelType:
        """Determine model type based on path and name"""
        path_lower = path.lower()
        name_lower = name.lower()
        
        if "loras" in path_lower or name_lower.endswith(".safetensors") and "lora" in name_lower:
            return ModelType.LORA
        elif "controlnet" in path_lower or "control_" in name_lower:
            return ModelType.CONTROLNET
        elif "vae" in path_lower or name_lower.endswith(".vae.safetensors"):
            return ModelType.VAE
        elif "upscale" in path_lower or "esrgan" in name_lower or "real-esrgan" in name_lower:
            return ModelType.UPSCALE
        elif "checkpoints" in path_lower or "models" in path_lower:
            return ModelType.CHECKPOINT
        else:
            return ModelType.OTHER
