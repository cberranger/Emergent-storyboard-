"""Database models for tracking active models on backends"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ModelType(str, Enum):
    """Type of model"""
    CHECKPOINT = "checkpoint"
    LORA = "lora"
    CONTROLNET = "controlnet"
    UPSCALE = "upscale"
    VAE = "vae"
    OTHER = "other"


class BackendModelInfo(BaseModel):
    """Information about a model being served by a specific backend"""
    id: str = Field(..., description="Unique identifier for this backend-model relationship")
    backend_id: str = Field(..., description="ID of the ComfyUI backend")
    backend_name: str = Field(..., description="Name of the ComfyUI backend")
    backend_url: str = Field(..., description="URL of the ComfyUI backend")
    
    # Model information
    model_id: str = Field(..., description="ID of the model in the database")
    model_name: str = Field(..., description="Name of the model file")
    model_type: ModelType = Field(..., description="Type of model")
    model_path: str = Field(..., description="Path to the model file on the backend")
    model_size: Optional[int] = Field(None, description="Size of the model file in bytes")
    
    # Civitai mapping (if available)
    civitai_model_id: Optional[str] = Field(None, description="Civitai model ID if matched")
    civitai_model_name: Optional[str] = Field(None, description="Civitai model name if matched")
    civitai_match_quality: Optional[str] = Field(None, description="Quality of Civitai match")
    
    # Status and metadata
    is_active: bool = Field(True, description="Whether this model is currently active on the backend")
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last time this model was detected")
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="First time this model was detected")
    
    # Additional model metadata from ComfyUI
    model_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata from ComfyUI")
    
    class Config:
        collection_name = "active_backend_models"


class BackendInfo(BaseModel):
    """Information about a ComfyUI backend"""
    id: str = Field(..., description="Unique identifier for the backend")
    name: str = Field(..., description="Name of the backend")
    url: str = Field(..., description="URL of the backend")
    is_online: bool = Field(True, description="Whether the backend is currently online")
    last_check: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last time the backend was checked")
    model_count: int = Field(0, description="Number of models this backend is serving")
    
    class Config:
        collection_name = "backends"


class ModelSyncStatus(BaseModel):
    """Track sync status for models"""
    model_id: str = Field(..., description="ID of the model in the database")
    civitai_model_id: Optional[str] = Field(None, description="Civitai model ID if synced")
    sync_status: str = Field(..., description="Sync status: pending, synced, failed")
    last_sync_attempt: Optional[datetime] = Field(None, description="Last time sync was attempted")
    last_sync_success: Optional[datetime] = Field(None, description="Last time sync was successful")
    sync_error: Optional[str] = Field(None, description="Error message if sync failed")
    
    class Config:
        collection_name = "model_sync_status"
