from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from dtos.clip_dtos import (
    ClipCreateDTO,
    ClipGalleryResponseDTO,
    ClipResponseDTO,
    ClipTimelineUpdateDTO,
    ClipUpdateDTO,
    GeneratedContentDTO,
)
from dtos.project_dtos import (
    ProjectCreateDTO,
    ProjectListResponseDTO,
    ProjectResponseDTO,
    ProjectWithScenesDTO,
)
from dtos.scene_dtos import (
    SceneCreateDTO,
    SceneListResponseDTO,
    SceneResponseDTO,
    SceneUpdateDTO,
)
from repositories.clip_repository import ClipRepository
from repositories.project_repository import ProjectRepository
from repositories.scene_repository import SceneRepository
from utils.errors import (
    ClipNotFoundError,
    ProjectNotFoundError,
    SceneNotFoundError,
    ValidationError,
)
from utils.timeline_validator import timeline_validator


def _cleanup_document(document: Optional[Dict]) -> Optional[Dict]:
    if document and "_id" in document:
        document = dict(document)
        document.pop("_id", None)
    return document


class ProjectService:
    """Business logic for projects, scenes, and clips."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        scene_repository: SceneRepository,
        clip_repository: ClipRepository,
    ):
        self._projects = project_repository
        self._scenes = scene_repository
        self._clips = clip_repository

    # -------------------------------------------------------------------------
    # Project operations
    # -------------------------------------------------------------------------
    async def create_project(self, payload: ProjectCreateDTO) -> ProjectResponseDTO:
        dto = ProjectResponseDTO(
            id=str(uuid4()),
            name=payload.name,
            description=payload.description or "",
            music_file_path=None,
            music_duration=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        await self._projects.create(dto.model_dump())
        return dto

    async def list_projects(self, include_scenes: bool = False) -> ProjectListResponseDTO:
        scenes_collection = self._scenes._collection if include_scenes else None
        projects = await self._projects.list_projects(
            include_scenes=include_scenes,
            scenes_collection=scenes_collection,
        )
        cleaned = [_cleanup_document(project) or {} for project in projects]

        if include_scenes:
            project_dtos = [
                ProjectWithScenesDTO(
                    **{
                        **project,
                        "scenes": [
                            SceneResponseDTO(**_cleanup_document(scene) or {})
                            for scene in project.get("scenes", [])
                        ],
                    }
                )
                for project in cleaned
            ]
        else:
            project_dtos = [ProjectResponseDTO(**project) for project in cleaned]

        return ProjectListResponseDTO(projects=project_dtos, total=len(project_dtos))

    async def get_project(self, project_id: str) -> ProjectResponseDTO:
        project = await self._projects.find_by_id(project_id)
        project = _cleanup_document(project)
        if not project:
            raise ProjectNotFoundError(project_id)
        return ProjectResponseDTO(**project)

    # -------------------------------------------------------------------------
    # Scene operations
    # -------------------------------------------------------------------------
    async def create_scene(self, payload: SceneCreateDTO) -> SceneResponseDTO:
        await self._ensure_project_exists(payload.project_id)

        dto = SceneResponseDTO(
            id=str(uuid4()),
            project_id=payload.project_id,
            name=payload.name,
            description=payload.description or "",
            lyrics=payload.lyrics or "",
            order=payload.order,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        await self._scenes.create(dto.model_dump())
        return dto

    async def list_project_scenes(self, project_id: str, include_clips: bool = False) -> SceneListResponseDTO:
        await self._ensure_project_exists(project_id)
        clips_collection = self._clips._collection if include_clips else None

        scenes = await self._scenes.list_by_project(
            project_id,
            include_clips=include_clips,
            clips_collection=clips_collection,
        )
        cleaned = [_cleanup_document(scene) or {} for scene in scenes]

        if include_clips:
            scene_dtos = [
                SceneResponseDTO(
                    **{
                        **scene,
                        "clips": [
                            ClipResponseDTO(**_cleanup_document(clip) or {})
                            for clip in scene.get("clips", [])
                        ],
                    }
                )
                for scene in cleaned
            ]
        else:
            scene_dtos = [SceneResponseDTO(**scene) for scene in cleaned]

        return SceneListResponseDTO(scenes=scene_dtos, total=len(scene_dtos))

    async def get_scene(self, scene_id: str) -> SceneResponseDTO:
        scene = await self._scenes.find_by_id(scene_id)
        scene = _cleanup_document(scene)
        if not scene:
            raise SceneNotFoundError(scene_id)
        return SceneResponseDTO(**scene)

    async def update_scene(self, scene_id: str, payload: SceneUpdateDTO) -> SceneResponseDTO:
        updates = {
            key: value
            for key, value in payload.model_dump(exclude_none=True).items()
            if key != "updated_at"
        }
        updates["updated_at"] = datetime.now(timezone.utc)

        updated = await self._scenes.update_scene(scene_id, updates)
        updated = _cleanup_document(updated)
        if not updated:
            raise SceneNotFoundError(scene_id)
        return SceneResponseDTO(**updated)

    # -------------------------------------------------------------------------
    # Clip operations
    # -------------------------------------------------------------------------
    async def create_clip(self, payload: ClipCreateDTO) -> ClipResponseDTO:
        await self._ensure_scene_exists(payload.scene_id)

        dto = ClipResponseDTO(
            id=str(uuid4()),
            scene_id=payload.scene_id,
            name=payload.name,
            lyrics=payload.lyrics or "",
            length=payload.length,
            timeline_position=payload.timeline_position,
            order=payload.order,
            image_prompt=payload.image_prompt or "",
            video_prompt=payload.video_prompt or "",
            generated_images=[],
            generated_videos=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        await self._clips.create(dto.model_dump())
        return dto

    async def list_scene_clips(self, scene_id: str) -> List[ClipResponseDTO]:
        await self._ensure_scene_exists(scene_id)
        clips = await self._clips.list_by_scene(scene_id)
        return [ClipResponseDTO(**(_cleanup_document(clip) or {})) for clip in clips]

    async def list_clips_by_project(self, project_id: str) -> List[ClipResponseDTO]:
        await self._ensure_project_exists(project_id)
        clips = await self._clips.list_by_project(project_id)
        return [ClipResponseDTO(**(_cleanup_document(clip) or {})) for clip in clips]

    async def get_clip(self, clip_id: str) -> ClipResponseDTO:
        clip = await self._clips.find_by_id(clip_id)
        clip = _cleanup_document(clip)
        if not clip:
            raise ClipNotFoundError(clip_id)
        return ClipResponseDTO(**clip)

    async def update_clip(self, clip_id: str, payload: ClipUpdateDTO) -> ClipResponseDTO:
        clip = await self._clips.find_by_id(clip_id)
        clip = _cleanup_document(clip)
        if not clip:
            raise ClipNotFoundError(clip_id)

        updates = {
            key: value
            for key, value in payload.model_dump(exclude_none=True).items()
            if value is not None
        }
        if not updates:
            raise ValidationError("No valid fields provided for update")

        updates["updated_at"] = datetime.now(timezone.utc)
        updated = await self._clips.update_by_id(clip_id, updates)
        updated = _cleanup_document(updated)
        if not updated:
            raise ClipNotFoundError(clip_id)
        return ClipResponseDTO(**updated)

    async def update_clip_prompts(
        self,
        clip_id: str,
        image_prompt: str,
        video_prompt: str,
    ) -> ClipResponseDTO:
        clip = await self._clips.update_prompts(
            clip_id=clip_id,
            image_prompt=image_prompt,
            video_prompt=video_prompt,
        )
        clip = _cleanup_document(clip)
        if not clip:
            raise ClipNotFoundError(clip_id)
        return ClipResponseDTO(**clip)

    async def update_clip_timeline_position(
        self,
        clip_id: str,
        payload: ClipTimelineUpdateDTO,
        *,
        check_overlap: bool = True,
    ) -> Dict:
        clip_data = await self._clips.find_by_id(clip_id)
        clip_data = _cleanup_document(clip_data)
        if not clip_data:
            raise ClipNotFoundError(clip_id)

        clip = ClipResponseDTO(**clip_data)
        new_position = payload.position

        if check_overlap:
            all_clips_data = await self._clips.find_many({"scene_id": clip.scene_id})
            all_clips = [
                ClipResponseDTO(**(_cleanup_document(item) or {}))
                for item in all_clips_data
            ]

            is_valid, error_msg = timeline_validator.check_overlap(
                clip_id=clip_id,
                new_position=new_position,
                clip_length=clip.length,
                other_clips=all_clips,
            )
            if not is_valid:
                suggested = timeline_validator.find_next_available_position(
                    clip_length=clip.length,
                    other_clips=[c for c in all_clips if c.id != clip_id],
                    preferred_position=new_position,
                )
                raise ValidationError(
                    f"Timeline conflict: {error_msg}. Suggested position: {suggested}"
                )

        updated = await self._clips.update_timeline_position(clip_id, new_position)
        updated = _cleanup_document(updated)
        if not updated:
            raise ClipNotFoundError(clip_id)

        updated_clips_data = await self._clips.find_many({"scene_id": clip.scene_id})
        updated_clips = [
            ClipResponseDTO(**(_cleanup_document(item) or {}))
            for item in updated_clips_data
        ]
        summary = timeline_validator.get_timeline_summary(updated_clips)

        return {
            "message": "Timeline position updated",
            "clip_id": clip_id,
            "new_position": new_position,
            "timeline_summary": summary,
        }

    async def analyze_scene_timeline(self, scene_id: str) -> Dict:
        await self._ensure_scene_exists(scene_id)
        clips_data = await self._clips.find_many({"scene_id": scene_id})
        clips = [
            ClipResponseDTO(**(_cleanup_document(item) or {}))
            for item in clips_data
        ]

        summary = timeline_validator.get_timeline_summary(clips)

        overlaps = []
        for i, clip1 in enumerate(clips):
            for clip2 in clips[i + 1:]:
                is_valid, error_msg = timeline_validator.check_overlap(
                    clip_id=clip1.id,
                    new_position=clip1.timeline_position,
                    clip_length=clip1.length,
                    other_clips=[clip2],
                )
                if not is_valid:
                    overlaps.append(
                        {
                            "clip1_id": clip1.id,
                            "clip1_name": clip1.name,
                            "clip2_id": clip2.id,
                            "clip2_name": clip2.name,
                            "error": error_msg,
                        }
                    )

        gaps = []
        sorted_clips = sorted(clips, key=lambda c: c.timeline_position)
        for i in range(len(sorted_clips) - 1):
            current_end = sorted_clips[i].timeline_position + sorted_clips[i].length
            next_start = sorted_clips[i + 1].timeline_position
            gap_size = next_start - current_end
            if gap_size > 0.1:
                gaps.append(
                    {
                        "after_clip_id": sorted_clips[i].id,
                        "after_clip_name": sorted_clips[i].name,
                        "before_clip_id": sorted_clips[i + 1].id,
                        "before_clip_name": sorted_clips[i + 1].name,
                        "gap_start": current_end,
                        "gap_end": next_start,
                        "gap_duration": gap_size,
                    }
                )

        return {
            "scene_id": scene_id,
            "summary": summary,
            "overlaps": overlaps,
            "gaps": gaps,
            "has_issues": len(overlaps) > 0,
            "total_clips": len(clips),
        }

    async def get_clip_gallery(self, clip_id: str) -> ClipGalleryResponseDTO:
        clip = await self._clips.find_by_id(clip_id)
        clip = _cleanup_document(clip)
        if not clip:
            raise ClipNotFoundError(clip_id)

        return ClipGalleryResponseDTO(
            images=[
                GeneratedContentDTO(**image)
                for image in clip.get("generated_images", [])
            ],
            videos=[
                GeneratedContentDTO(**video)
                for video in clip.get("generated_videos", [])
            ],
            selected_image_id=clip.get("selected_image_id"),
            selected_video_id=clip.get("selected_video_id"),
        )

    # -------------------------------------------------------------------------
    # Character Management
    # -------------------------------------------------------------------------
    async def create_character(self, payload: Any) -> Any:
        """Create a new character for consistent generation"""
        character_data = {
            "id": str(uuid.uuid4()),
            "name": payload.name,
            "description": payload.description,
            "project_id": payload.project_id if hasattr(payload, 'project_id') else None,
            "reference_images": payload.reference_images if hasattr(payload, 'reference_images') else [],
            "style_notes": payload.style_notes if hasattr(payload, 'style_notes') else "",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        db = await self._projects._get_db()
        await db.characters.insert_one(character_data)
        return character_data

    async def list_characters(self, project_id: Optional[str] = None) -> List[Any]:
        """Get all characters, optionally filtered by project"""
        db = await self._projects._get_db()
        query = {"project_id": project_id} if project_id else {}
        characters = await db.characters.find(query).to_list(None)
        return characters

    async def get_character(self, character_id: str) -> Any:
        """Get a specific character"""
        db = await self._projects._get_db()
        character = await db.characters.find_one({"id": character_id})
        if not character:
            raise ResourceNotFoundError("Character", character_id)
        return character

    async def update_character(self, character_id: str, payload: Any) -> Any:
        """Update a character"""
        db = await self._projects._get_db()
        character = await db.characters.find_one({"id": character_id})
        if not character:
            raise ResourceNotFoundError("Character", character_id)

        update_data = {
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        if hasattr(payload, 'name') and payload.name is not None:
            update_data["name"] = payload.name
        if hasattr(payload, 'description') and payload.description is not None:
            update_data["description"] = payload.description
        if hasattr(payload, 'reference_images') and payload.reference_images is not None:
            update_data["reference_images"] = payload.reference_images
        if hasattr(payload, 'style_notes') and payload.style_notes is not None:
            update_data["style_notes"] = payload.style_notes

        await db.characters.update_one(
            {"id": character_id},
            {"$set": update_data}
        )

        updated = await db.characters.find_one({"id": character_id})
        return updated

    async def delete_character(self, character_id: str) -> None:
        """Delete a character"""
        db = await self._projects._get_db()
        result = await db.characters.delete_one({"id": character_id})
        if result.deleted_count == 0:
            raise ResourceNotFoundError("Character", character_id)

    async def apply_character_to_clip(self, character_id: str, clip_id: str) -> Dict:
        """Apply character settings to a clip's generation prompt"""
        character = await self.get_character(character_id)
        clip = await self.get_clip(clip_id)

        # Build enhanced prompt with character details
        character_prompt = f"{character['description']}"
        if character.get('style_notes'):
            character_prompt += f", {character['style_notes']}"

        # Update clip's prompt
        current_prompt = clip.get('prompt', '')
        enhanced_prompt = f"{character_prompt}. {current_prompt}" if current_prompt else character_prompt

        await self.update_clip_prompts(clip_id, enhanced_prompt, clip.get('negative_prompt'))

        return {
            "message": "Character applied to clip",
            "character_id": character_id,
            "clip_id": clip_id,
            "enhanced_prompt": enhanced_prompt
        }

    # -------------------------------------------------------------------------
    # Style Template Management
    # -------------------------------------------------------------------------
    async def create_style_template(self, payload: Any) -> Any:
        """Create a new style template"""
        template_data = {
            "id": str(uuid.uuid4()),
            "name": payload.name,
            "description": payload.description if hasattr(payload, 'description') else "",
            "project_id": payload.project_id if hasattr(payload, 'project_id') else None,
            "prompt_template": payload.prompt_template,
            "negative_prompt_template": payload.negative_prompt_template if hasattr(payload, 'negative_prompt_template') else "",
            "default_params": payload.default_params if hasattr(payload, 'default_params') else {},
            "use_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        db = await self._projects._get_db()
        await db.style_templates.insert_one(template_data)
        return template_data

    async def list_style_templates(self, project_id: Optional[str] = None) -> List[Any]:
        """Get all style templates, optionally filtered by project"""
        db = await self._projects._get_db()
        query = {"project_id": project_id} if project_id else {}
        templates = await db.style_templates.find(query).to_list(None)
        return templates

    async def get_style_template(self, template_id: str) -> Any:
        """Get a specific style template"""
        db = await self._projects._get_db()
        template = await db.style_templates.find_one({"id": template_id})
        if not template:
            raise ResourceNotFoundError("StyleTemplate", template_id)
        return template

    async def update_style_template(self, template_id: str, payload: Any) -> Any:
        """Update a style template"""
        db = await self._projects._get_db()
        template = await db.style_templates.find_one({"id": template_id})
        if not template:
            raise ResourceNotFoundError("StyleTemplate", template_id)

        update_data = {
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        if hasattr(payload, 'name') and payload.name is not None:
            update_data["name"] = payload.name
        if hasattr(payload, 'description') and payload.description is not None:
            update_data["description"] = payload.description
        if hasattr(payload, 'prompt_template') and payload.prompt_template is not None:
            update_data["prompt_template"] = payload.prompt_template
        if hasattr(payload, 'negative_prompt_template') and payload.negative_prompt_template is not None:
            update_data["negative_prompt_template"] = payload.negative_prompt_template
        if hasattr(payload, 'default_params') and payload.default_params is not None:
            update_data["default_params"] = payload.default_params

        await db.style_templates.update_one(
            {"id": template_id},
            {"$set": update_data}
        )

        updated = await db.style_templates.find_one({"id": template_id})
        return updated

    async def delete_style_template(self, template_id: str) -> None:
        """Delete a style template"""
        db = await self._projects._get_db()
        result = await db.style_templates.delete_one({"id": template_id})
        if result.deleted_count == 0:
            raise ResourceNotFoundError("StyleTemplate", template_id)

    async def increment_template_usage(self, template_id: str) -> None:
        """Increment use count for a template"""
        db = await self._projects._get_db()
        result = await db.style_templates.update_one(
            {"id": template_id},
            {
                "$inc": {"use_count": 1},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        if result.matched_count == 0:
            raise ResourceNotFoundError("StyleTemplate", template_id)

    # -------------------------------------------------------------------------
    # Additional CRUD Operations
    # -------------------------------------------------------------------------
    async def update_project(self, project_id: str, payload: Any) -> Any:
        """Update a project"""
        await self._ensure_project_exists(project_id)

        update_data = {
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        if hasattr(payload, 'name') and payload.name is not None:
            update_data["name"] = payload.name
        if hasattr(payload, 'description') and payload.description is not None:
            update_data["description"] = payload.description
        if hasattr(payload, 'target_aspect_ratio') and payload.target_aspect_ratio is not None:
            update_data["target_aspect_ratio"] = payload.target_aspect_ratio
        if hasattr(payload, 'target_fps') and payload.target_fps is not None:
            update_data["target_fps"] = payload.target_fps
        if hasattr(payload, 'music_url') and payload.music_url is not None:
            update_data["music_url"] = payload.music_url

        updated = await self._projects.update(project_id, update_data)
        return updated

    async def delete_project(self, project_id: str) -> None:
        """Delete a project and all its scenes and clips"""
        await self._ensure_project_exists(project_id)

        # Delete all scenes and their clips
        scenes = await self._scenes.find_by_project(project_id)
        for scene in scenes:
            clips = await self._clips.find_by_scene(scene["id"])
            for clip in clips:
                await self._clips.delete(clip["id"])
            await self._scenes.delete(scene["id"])

        # Delete the project
        await self._projects.delete(project_id)

    async def delete_scene(self, scene_id: str) -> None:
        """Delete a scene and all its clips"""
        await self._ensure_scene_exists(scene_id)

        # Delete all clips in the scene
        clips = await self._clips.find_by_scene(scene_id)
        for clip in clips:
            await self._clips.delete(clip["id"])

        # Delete the scene
        await self._scenes.delete(scene_id)

    async def delete_clip(self, clip_id: str) -> None:
        """Delete a clip"""
        clip = await self._clips.find_by_id(clip_id)
        if not clip:
            raise ClipNotFoundError(clip_id)

        await self._clips.delete(clip_id)

    async def get_project_with_scenes(self, project_id: str) -> Any:
        """Get a project with all its scenes"""
        project = await self.get_project(project_id)
        scenes = await self.list_project_scenes(project_id, include_clips=False)

        project_dict = dict(project) if hasattr(project, '__dict__') else project
        project_dict["scenes"] = scenes

        return project_dict

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    async def _ensure_project_exists(self, project_id: str) -> None:
        project = await self._projects.find_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)

    async def _ensure_scene_exists(self, scene_id: str) -> None:
        scene = await self._scenes.find_by_id(scene_id)
        if not scene:
            raise SceneNotFoundError(scene_id)