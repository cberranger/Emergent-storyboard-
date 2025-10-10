"""Data Transfer Objects for backend API."""

from .comfyui_dtos import (
    ComfyUIServerCreateDTO,
    ComfyUIServerDTO,
    ComfyUIServerInfoDTO,
    ModelDTO,
)
from .project_dtos import (
    ProjectCreateDTO,
    ProjectUpdateDTO,
    ProjectResponseDTO,
    ProjectListResponseDTO,
    ProjectWithScenesDTO,
)
from .scene_dtos import (
    SceneCreateDTO,
    SceneUpdateDTO,
    SceneResponseDTO,
    SceneListResponseDTO,
)
from .clip_dtos import (
    ClipCreateDTO,
    ClipUpdateDTO,
    ClipResponseDTO,
    ClipTimelineUpdateDTO,
    ClipGalleryResponseDTO,
    GeneratedContentDTO,
    ClipVersionDTO,
)
from .media_dtos import (
    UploadMusicResponseDTO,
    UploadFaceImageResponseDTO,
)
from .generation_dtos import (
    GenerationRequestDTO,
    GenerationResponseDTO,
    GenerationParamsDTO,
    LoraConfigDTO,
    BatchGenerationRequestDTO,
    BatchGenerationJobDTO,
    BatchGenerationStatusDTO,
)
from .template_dtos import (
    StyleTemplateCreateDTO,
    StyleTemplateUpdateDTO,
    StyleTemplateResponseDTO,
    StyleTemplateListResponseDTO,
)
from .character_dtos import (
    CharacterCreateDTO,
    CharacterUpdateDTO,
    CharacterResponseDTO,
    CharacterListResponseDTO,
)
from .queue_dtos import (
    QueueJobRequestDTO,
    QueueJobResponseDTO,
    QueueStatusDTO,
    QueueServerRegistrationDTO,
    QueueJobStatusDTO,
)

__all__ = [
    # ComfyUI DTOs
    "ComfyUIServerCreateDTO",
    "ComfyUIServerDTO",
    "ComfyUIServerInfoDTO",
    "ModelDTO",
    # Project DTOs
    "ProjectCreateDTO",
    "ProjectUpdateDTO",
    "ProjectResponseDTO",
    "ProjectListResponseDTO",
    "ProjectWithScenesDTO",
    # Scene DTOs
    "SceneCreateDTO",
    "SceneUpdateDTO",
    "SceneResponseDTO",
    "SceneListResponseDTO",
    # Clip DTOs
    "ClipCreateDTO",
    "ClipUpdateDTO",
    "ClipResponseDTO",
    "ClipTimelineUpdateDTO",
    "ClipGalleryResponseDTO",
    "GeneratedContentDTO",
    "ClipVersionDTO",
    # Media DTOs
    "UploadMusicResponseDTO",
    "UploadFaceImageResponseDTO",
    # Generation DTOs
    "GenerationRequestDTO",
    "GenerationResponseDTO",
    "GenerationParamsDTO",
    "LoraConfigDTO",
    "BatchGenerationRequestDTO",
    "BatchGenerationJobDTO",
    "BatchGenerationStatusDTO",
    # Style Template DTOs
    "StyleTemplateCreateDTO",
    "StyleTemplateUpdateDTO",
    "StyleTemplateResponseDTO",
    "StyleTemplateListResponseDTO",
    # Character DTOs
    "CharacterCreateDTO",
    "CharacterUpdateDTO",
    "CharacterResponseDTO",
    "CharacterListResponseDTO",
    # Queue DTOs
    "QueueJobRequestDTO",
    "QueueJobResponseDTO",
    "QueueStatusDTO",
    "QueueServerRegistrationDTO",
    "QueueJobStatusDTO",
]