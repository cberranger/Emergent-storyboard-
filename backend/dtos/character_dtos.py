from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


def generate_uuid() -> str:
    from uuid import uuid4

    return str(uuid4())


class FaceFusionProcessingHistoryEntry(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    operation_type: str = Field(..., description="enhance, age_adjust, swap, edit, mask, detect")
    input_image_url: str
    output_image_url: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FaceFusionPreferredSettings(BaseModel):
    enhancement_model: str = Field(default="gfpgan_1.4")
    face_enhancer_blend: float = Field(default=1.0, ge=0.0, le=1.0)
    age_adjustment_blend: float = Field(default=1.0, ge=0.0, le=1.0)
    face_mask_types: List[str] = Field(default_factory=lambda: ["box"])
    face_selector_mode: str = Field(default="one", description="one, many, all")
    face_selector_order: str = Field(default="left-right")
    face_detector_model: str = Field(default="yoloface")
    face_detector_size: str = Field(default="640x640")
    face_swapper_model: str = Field(default="inswapper_128")
    face_editor_eyebrow_direction: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_eye_gaze_horizontal: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_eye_gaze_vertical: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_eye_open_ratio: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_lip_open_ratio: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_mouth_grim: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_mouth_pout: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_mouth_purse: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_mouth_smile: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_mouth_position_horizontal: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_mouth_position_vertical: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_head_pitch: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_head_yaw: Optional[int] = Field(default=None, ge=-100, le=100)
    face_editor_head_roll: Optional[int] = Field(default=None, ge=-100, le=100)


class FaceFusionOutputGallery(BaseModel):
    enhanced_faces: List[str] = Field(default_factory=list)
    age_variants: Dict[int, str] = Field(default_factory=dict)
    swapped_faces: List[str] = Field(default_factory=list)
    edited_expressions: List[str] = Field(default_factory=list)
    custom_outputs: List[str] = Field(default_factory=list)


class CharacterCreateDTO(BaseModel):
    project_id: str
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=2000)
    reference_images: List[str] = Field(default_factory=list)
    lora: Optional[str] = Field(default=None, max_length=200)
    trigger_words: Optional[str] = Field(default="", max_length=500)
    style_notes: Optional[str] = Field(default="", max_length=2000)
    facefusion_preferred_settings: Optional[FaceFusionPreferredSettings] = None


class CharacterUpdateDTO(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    reference_images: Optional[List[str]] = None
    lora: Optional[str] = Field(default=None, max_length=200)
    trigger_words: Optional[str] = Field(default=None, max_length=500)
    style_notes: Optional[str] = Field(default=None, max_length=2000)
    facefusion_preferred_settings: Optional[FaceFusionPreferredSettings] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CharacterResponseDTO(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    project_id: str
    name: str
    description: Optional[str] = ""
    reference_images: List[str] = Field(default_factory=list)
    lora: Optional[str] = None
    trigger_words: Optional[str] = ""
    style_notes: Optional[str] = ""
    facefusion_processing_history: List[FaceFusionProcessingHistoryEntry] = Field(default_factory=list)
    facefusion_preferred_settings: Optional[FaceFusionPreferredSettings] = None
    facefusion_output_gallery: FaceFusionOutputGallery = Field(default_factory=FaceFusionOutputGallery)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CharacterListResponseDTO(BaseModel):
    characters: List[CharacterResponseDTO]
    total: int