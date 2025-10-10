"""Gallery management service for handling generated content"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging

from dtos.clip_dtos import ClipResponseDTO, GeneratedContentDTO
from utils.errors import ClipNotFoundError

logger = logging.getLogger(__name__)


class GalleryManager:
    """Manages gallery operations for clips"""

    @staticmethod
    def initialize_clip_fields(clip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize clip with default values for gallery fields

        Args:
            clip_data: Raw clip data from database

        Returns:
            Clip data with initialized fields
        """
        clip_data = dict(clip_data)
        clip_data.setdefault("generated_images", [])
        clip_data.setdefault("generated_videos", [])
        clip_data.setdefault("selected_image_id", None)
        clip_data.setdefault("selected_video_id", None)
        clip_data.setdefault("image_prompt", "")
        clip_data.setdefault("video_prompt", "")
        clip_data.setdefault("updated_at", datetime.now(timezone.utc))
        return clip_data

    @staticmethod
    async def add_generated_content(
        db,
        clip_id: str,
        new_content: GeneratedContentDTO,
        content_type: str
    ) -> Dict[str, Any]:
        """
        Add generated content to clip gallery

        Args:
            db: Database instance
            clip_id: Clip ID
            new_content: GeneratedContentDTO object
            content_type: "image" or "video"

        Returns:
            Response dict with message and content info
        """
        clip_data = await db.clips.find_one({"id": clip_id})
        if not clip_data:
            raise ClipNotFoundError(clip_id)

        logger.info("Found clip: %s", clip_data.get("id"))

        clip_data = GalleryManager.initialize_clip_fields(clip_data)
        clip = ClipResponseDTO(**clip_data)

        if content_type == "image":
            clip.generated_images.append(new_content)

            if len(clip.generated_images) == 1:
                clip.selected_image_id = new_content.id
                new_content.is_selected = True

            await db.clips.update_one(
                {"id": clip_id},
                {"$set": {
                    "generated_images": [img.model_dump() for img in clip.generated_images],
                    "selected_image_id": clip.selected_image_id,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )

            return {
                "message": "Image generated successfully",
                "content": new_content.model_dump(),
                "total_images": len(clip.generated_images)
            }

        if content_type == "video":
            clip.generated_videos.append(new_content)

            if len(clip.generated_videos) == 1:
                clip.selected_video_id = new_content.id
                new_content.is_selected = True

            await db.clips.update_one(
                {"id": clip_id},
                {"$set": {
                    "generated_videos": [vid.model_dump() for vid in clip.generated_videos],
                    "selected_video_id": clip.selected_video_id,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )

            return {
                "message": "Video generated successfully",
                "content": new_content.model_dump(),
                "total_videos": len(clip.generated_videos)
            }

        raise ValueError(f"Invalid content type: {content_type}")

    @staticmethod
    async def select_content(
        db,
        clip_id: str,
        content_id: str,
        content_type: str
    ) -> Dict[str, Any]:
        """
        Select a generated content item as active

        Args:
            db: Database instance
            clip_id: Clip ID
            content_id: Content ID to select
            content_type: "image" or "video"

        Returns:
            Success message
        """
        field_name = "generated_images" if content_type == "image" else "generated_videos"
        selected_field = "selected_image_id" if content_type == "image" else "selected_video_id"

        clip_data = await db.clips.find_one({"id": clip_id})
        if not clip_data:
            raise ClipNotFoundError(clip_id)

        content_list: List[Dict[str, Any]] = clip_data.get(field_name, [])
        for content in content_list:
            content["is_selected"] = (content["id"] == content_id)

        await db.clips.update_one(
            {"id": clip_id},
            {"$set": {
                field_name: content_list,
                selected_field: content_id,
                "updated_at": datetime.now(timezone.utc)
            }}
        )

        return {"message": f"Selected {content_type} updated successfully"}

    @staticmethod
    def create_generated_content(
        content_type: str,
        url: str,
        prompt: str,
        negative_prompt: str,
        server_id: str,
        server_name: str,
        model_name: str,
        model_type: Optional[str],
        generation_params: Dict[str, Any]
    ) -> GeneratedContentDTO:
        """
        Create a GeneratedContentDTO object
        """
        return GeneratedContentDTO(
            content_type=content_type,
            url=url,
            prompt=prompt,
            negative_prompt=negative_prompt,
            server_id=server_id,
            server_name=server_name,
            model_name=model_name,
            model_type=model_type,
            generation_params=generation_params,
            is_selected=False
        )


# Global instance
gallery_manager = GalleryManager()
