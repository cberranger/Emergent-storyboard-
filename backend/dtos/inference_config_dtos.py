"""Data Transfer Objects for inference configurations"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime


class ModelConfigurationDTO(BaseModel):
    """DTO for model inference configuration"""
    model_config = ConfigDict(protected_namespaces=())
    
    id: str
    model_id: Optional[str] = None
    base_model: str
    name: str
    description: Optional[str] = ""
    is_default: bool = False
    steps: int
    cfg_scale: float
    sampler: str
    scheduler: str
    clip_skip: Optional[int] = -1
    resolution_width: int
    resolution_height: int
    batch_size: Optional[int] = 1
    seed: Optional[int] = -1
    additional_params: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ModelConfigurationCreateDTO(BaseModel):
    """DTO for creating model configuration"""
    model_config = ConfigDict(protected_namespaces=())
    
    model_id: Optional[str] = None
    base_model: str
    name: str
    description: Optional[str] = ""
    is_default: bool = False
    steps: int
    cfg_scale: float
    sampler: str
    scheduler: str
    clip_skip: Optional[int] = -1
    resolution_width: int
    resolution_height: int
    batch_size: Optional[int] = 1
    seed: Optional[int] = -1
    additional_params: Dict[str, Any] = Field(default_factory=dict)


class ModelConfigurationUpdateDTO(BaseModel):
    """DTO for updating model configuration"""
    model_config = ConfigDict(protected_namespaces=())
    
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    steps: Optional[int] = None
    cfg_scale: Optional[float] = None
    sampler: Optional[str] = None
    scheduler: Optional[str] = None
    clip_skip: Optional[int] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    batch_size: Optional[int] = None
    seed: Optional[int] = None
    additional_params: Optional[Dict[str, Any]] = None


class InferenceConfigurationDTO(BaseModel):
    """DTO for inference configuration (legacy)"""
    model_config = ConfigDict(protected_namespaces=())
    
    id: str
    model_id: str
    base_model: str
    configuration_type: str
    steps: int
    cfg_scale: float
    sampler: str
    scheduler: str
    model_specific_params: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class InferenceConfigurationCreateDTO(BaseModel):
    """DTO for creating inference configuration (legacy)"""
    model_config = ConfigDict(protected_namespaces=())
    
    model_id: str
    base_model: str
    configuration_type: str
    steps: int
    cfg_scale: float
    sampler: str
    scheduler: str
    model_specific_params: Dict[str, Any] = Field(default_factory=dict)


class InferenceConfigurationUpdateDTO(BaseModel):
    """DTO for updating inference configuration (legacy)"""
    model_config = ConfigDict(protected_namespaces=())
    
    steps: Optional[int] = None
    cfg_scale: Optional[float] = None
    sampler: Optional[str] = None
    scheduler: Optional[str] = None
    model_specific_params: Optional[Dict[str, Any]] = None
