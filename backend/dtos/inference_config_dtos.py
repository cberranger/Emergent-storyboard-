"""Data Transfer Objects for inference configurations"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime


class InferenceConfigurationDTO(BaseModel):
    """DTO for inference configuration"""
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
    """DTO for creating inference configuration"""
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
    """DTO for updating inference configuration"""
    model_config = ConfigDict(protected_namespaces=())
    
    steps: Optional[int] = None
    cfg_scale: Optional[float] = None
    sampler: Optional[str] = None
    scheduler: Optional[str] = None
    model_specific_params: Optional[Dict[str, Any]] = None
