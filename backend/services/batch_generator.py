"""Batch generation service for processing multiple clips"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class BatchGenerator:
    """Manages batch generation of multiple clips"""

    def __init__(self, batch_repository=None):
        self.active_batches: Dict[str, Dict[str, Any]] = {}
        self._repository = batch_repository
        self._initialized = False

    async def _load_from_db(self):
        """Load active batches from database"""
        if self._initialized or not self._repository:
            return
        
        try:
            active_batches = await self._repository.find_active_batches()
            for batch_data in active_batches:
                self.active_batches[batch_data["id"]] = batch_data
            
            self._initialized = True
            logger.info(f"Loaded {len(self.active_batches)} active batches from database")
        except Exception as e:
            logger.error(f"Failed to load batches from database: {e}")

    async def _persist_batch(self, batch: Dict[str, Any]):
        """Persist batch to database"""
        if not self._repository:
            return
        
        try:
            existing = await self._repository.find_by_id(batch["id"])
            if existing:
                await self._repository.update_by_id(batch["id"], batch)
            else:
                await self._repository.create(batch)
        except Exception as e:
            logger.error(f"Failed to persist batch {batch['id']}: {e}")

    async def generate_batch(
        self,
        db,
        clip_ids: List[str],
        server_id: str,
        generation_type: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate content for multiple clips

        Args:
            db: Database instance
            clip_ids: List of clip IDs to generate
            server_id: ComfyUI server ID
            generation_type: "image" or "video"
            params: Generation parameters

        Returns:
            Batch job info with status
        """
        import uuid
        from server import ComfyUIServer, ComfyUIClient
        from services.gallery_manager import gallery_manager

        await self._load_from_db()
        
        batch_id = str(uuid.uuid4())

        # Initialize batch tracking
        batch = {
            "id": batch_id,
            "status": "processing",
            "total": len(clip_ids),
            "completed": 0,
            "failed": 0,
            "results": [],
            "started_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        self.active_batches[batch_id] = batch
        await self._persist_batch(batch)

        logger.info(f"Starting batch generation {batch_id} for {len(clip_ids)} clips")

        # Get server
        server_data = await db.comfyui_servers.find_one({"id": server_id})
        if not server_data:
            batch["status"] = "failed"
            batch["error"] = "Server not found"
            batch["updated_at"] = datetime.now(timezone.utc)
            await self._persist_batch(batch)
            return batch

        server = ComfyUIServer(**server_data)
        client = ComfyUIClient(server)

        # Check server connection
        if not await client.check_connection():
            batch["status"] = "failed"
            batch["error"] = "Server offline"
            batch["updated_at"] = datetime.now(timezone.utc)
            await self._persist_batch(batch)
            return batch

        # Process clips
        tasks = []
        for clip_id in clip_ids:
            task = self._generate_single(
                db, clip_id, client, server, generation_type, params, batch_id
            )
            tasks.append(task)

        # Run all generations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Update batch status
        batch["status"] = "completed"
        batch["completed"] = sum(1 for r in results if not isinstance(r, Exception))
        batch["failed"] = sum(1 for r in results if isinstance(r, Exception))
        batch["results"] = [
            r if not isinstance(r, Exception) else {"error": str(r)}
            for r in results
        ]
        batch["updated_at"] = datetime.now(timezone.utc)
        await self._persist_batch(batch)

        logger.info(f"Batch {batch_id} completed: {batch['completed']}/{batch['total']} successful")

        return batch

    async def _generate_single(
        self,
        db,
        clip_id: str,
        client,
        server,
        generation_type: str,
        params: Dict[str, Any],
        batch_id: str
    ) -> Dict[str, Any]:
        """Generate content for a single clip"""
        from server import detect_model_type
        from services.gallery_manager import gallery_manager

        try:
            # Get clip
            clip_data = await db.clips.find_one({"id": clip_id})
            if not clip_data:
                raise ValueError(f"Clip {clip_id} not found")

            # Use clip's prompt or provided prompt
            prompt = params.get("prompt", clip_data.get(f"{generation_type}_prompt", ""))
            if not prompt:
                raise ValueError(f"No prompt for clip {clip_id}")

            # Generate content
            if generation_type == "image":
                result_url = await client.generate_image(
                    prompt=prompt,
                    negative_prompt=params.get("negative_prompt", ""),
                    model=params.get("model"),
                    params=params.get("generation_params", {}),
                    loras=params.get("loras", [])
                )
            else:
                result_url = await client.generate_video(
                    prompt=prompt,
                    negative_prompt=params.get("negative_prompt", ""),
                    model=params.get("model"),
                    params=params.get("generation_params", {}),
                    loras=params.get("loras", [])
                )

            if not result_url:
                raise ValueError("Generation failed - no result URL")

            # Detect model type
            model_type = detect_model_type(params.get("model", "unknown"))

            # Create generated content
            new_content = gallery_manager.create_generated_content(
                content_type=generation_type,
                url=result_url,
                prompt=prompt,
                negative_prompt=params.get("negative_prompt", ""),
                server_id=server.id,
                server_name=server.name,
                model_name=params.get("model", "unknown"),
                model_type=model_type,
                generation_params=params.get("generation_params", {})
            )

            # Add to clip gallery
            result = await gallery_manager.add_generated_content(
                db=db,
                clip_id=clip_id,
                new_content=new_content,
                content_type=generation_type
            )

            return {
                "clip_id": clip_id,
                "status": "success",
                "result": result
            }

        except Exception as e:
            logger.error(f"Failed to generate for clip {clip_id}: {e}")
            return {
                "clip_id": clip_id,
                "status": "failed",
                "error": str(e)
            }

    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get status of a batch job"""
        await self._load_from_db()
        
        batch = self.active_batches.get(batch_id)
        if batch:
            return batch
        
        if self._repository:
            batch_data = await self._repository.find_by_id(batch_id)
            if batch_data:
                return batch_data
        
        return {"error": "Batch not found"}

    async def list_batches(self) -> List[Dict[str, Any]]:
        """List all batch jobs"""
        await self._load_from_db()
        
        if self._repository:
            try:
                recent_batches = await self._repository.list_recent(limit=100)
                memory_batch_ids = set(self.active_batches.keys())
                
                for batch in recent_batches:
                    if batch["id"] not in memory_batch_ids:
                        self.active_batches[batch["id"]] = batch
                
            except Exception as e:
                logger.error(f"Failed to list batches from database: {e}")
        
        return list(self.active_batches.values())

    async def clear_completed_batches(self) -> int:
        """Clear completed batch jobs from memory"""
        to_remove = [
            batch_id for batch_id, batch in self.active_batches.items()
            if batch["status"] in ["completed", "failed"]
        ]
        for batch_id in to_remove:
            del self.active_batches[batch_id]
        return len(to_remove)


# Global instance
batch_generator = BatchGenerator()
