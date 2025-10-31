"""Models router for model management and configuration endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from database import get_database
from dtos.inference_config_dtos import (
    ModelConfigurationDTO,
    ModelConfigurationCreateDTO,
    ModelConfigurationUpdateDTO,
)
from repositories.inference_configuration_repository import ModelConfigurationRepository
from services.model_config import ModelConfigurationService

router = APIRouter(prefix="/models", tags=["models"])


def get_model_config_service(db=Depends(get_database)) -> ModelConfigurationService:
    """Dependency to get model configuration service"""
    repository = ModelConfigurationRepository(db.model_configurations)
    return ModelConfigurationService(repository)


@router.post("/{model_id}/configurations", response_model=ModelConfigurationDTO)
async def create_model_configuration(
    model_id: str,
    config_data: ModelConfigurationCreateDTO,
    service: ModelConfigurationService = Depends(get_model_config_service),
):
    """Create a new configuration for a specific model"""
    config_data.model_id = model_id
    return await service.create_configuration(config_data)


@router.get("/{model_id}/configurations", response_model=List[ModelConfigurationDTO])
async def get_model_configurations(
    model_id: str,
    service: ModelConfigurationService = Depends(get_model_config_service),
):
    """Get all configurations for a specific model"""
    return await service.get_configurations_by_model(model_id)


@router.get("/configurations/{config_id}", response_model=ModelConfigurationDTO)
async def get_configuration(
    config_id: str,
    service: ModelConfigurationService = Depends(get_model_config_service),
):
    """Get a specific configuration by ID"""
    config = await service.get_configuration(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/configurations/{config_id}", response_model=ModelConfigurationDTO)
async def update_configuration(
    config_id: str,
    update_data: ModelConfigurationUpdateDTO,
    service: ModelConfigurationService = Depends(get_model_config_service),
):
    """Update a configuration"""
    updated = await service.update_configuration(config_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return updated


@router.delete("/configurations/{config_id}")
async def delete_configuration(
    config_id: str,
    service: ModelConfigurationService = Depends(get_model_config_service),
):
    """Delete a configuration"""
    success = await service.delete_configuration(config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {"message": "Configuration deleted successfully"}


@router.post("/configurations/base/{base_model_type}", response_model=ModelConfigurationDTO)
async def create_base_model_configuration(
    base_model_type: str,
    config_data: ModelConfigurationCreateDTO,
    service: ModelConfigurationService = Depends(get_model_config_service),
):
    """Create a global configuration for a base model type"""
    config_data.base_model = base_model_type
    config_data.model_id = None
    return await service.create_configuration(config_data)


@router.get("/configurations/base/{base_model_type}", response_model=List[ModelConfigurationDTO])
async def get_base_model_configurations(
    base_model_type: str,
    service: ModelConfigurationService = Depends(get_model_config_service),
):
    """Get all global configurations for a base model type"""
    return await service.get_configurations_by_base_model(base_model_type)


@router.get("/{model_id}/configurations/default", response_model=ModelConfigurationDTO)
async def get_default_configuration(
    model_id: str,
    service: ModelConfigurationService = Depends(get_model_config_service),
):
    """Get the default configuration for a model"""
    config = await service.get_default_configuration(model_id=model_id)
    if not config:
        raise HTTPException(status_code=404, detail="No default configuration found")
    return config
