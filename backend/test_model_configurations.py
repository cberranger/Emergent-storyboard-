"""Tests for model configurations API"""
import pytest
from datetime import datetime, timezone

from dtos.inference_config_dtos import ModelConfigurationCreateDTO, ModelConfigurationUpdateDTO


@pytest.mark.asyncio
async def test_create_model_configuration(test_client, db_conn):
    """Test creating a model-specific configuration"""
    model_id = "test_model_123"
    config_data = {
        "model_id": model_id,
        "base_model": "sdxl",
        "name": "High Quality",
        "description": "High quality settings for SDXL",
        "is_default": True,
        "steps": 35,
        "cfg_scale": 7.5,
        "sampler": "dpmpp_2m",
        "scheduler": "karras",
        "clip_skip": -1,
        "resolution_width": 1024,
        "resolution_height": 1024,
        "batch_size": 1,
        "seed": -1,
        "additional_params": {"refiner_steps": 5}
    }
    
    response = test_client.post(f"/api/v1/models/{model_id}/configurations", json=config_data)
    assert response.status_code == 200
    
    result = response.json()
    assert result["name"] == "High Quality"
    assert result["model_id"] == model_id
    assert result["base_model"] == "sdxl"
    assert result["steps"] == 35
    assert result["is_default"] is True
    assert "id" in result
    assert "created_at" in result


@pytest.mark.asyncio
async def test_get_model_configurations(test_client, db_conn):
    """Test retrieving all configurations for a model"""
    model_id = "test_model_456"
    
    config1 = {
        "model_id": model_id,
        "base_model": "flux_dev",
        "name": "Fast",
        "steps": 8,
        "cfg_scale": 2.0,
        "sampler": "euler",
        "scheduler": "simple",
        "resolution_width": 1024,
        "resolution_height": 1024,
    }
    
    config2 = {
        "model_id": model_id,
        "base_model": "flux_dev",
        "name": "Quality",
        "steps": 28,
        "cfg_scale": 3.5,
        "sampler": "euler",
        "scheduler": "simple",
        "resolution_width": 1024,
        "resolution_height": 1024,
    }
    
    test_client.post(f"/api/v1/models/{model_id}/configurations", json=config1)
    test_client.post(f"/api/v1/models/{model_id}/configurations", json=config2)
    
    response = test_client.get(f"/api/v1/models/{model_id}/configurations")
    assert response.status_code == 200
    
    configs = response.json()
    assert len(configs) == 2
    assert any(c["name"] == "Fast" for c in configs)
    assert any(c["name"] == "Quality" for c in configs)


@pytest.mark.asyncio
async def test_create_base_model_configuration(test_client, db_conn):
    """Test creating a base model configuration"""
    base_model_type = "pony"
    config_data = {
        "base_model": base_model_type,
        "name": "Pony Default",
        "description": "Default settings for Pony models",
        "is_default": True,
        "steps": 28,
        "cfg_scale": 7.0,
        "sampler": "dpmpp_2m",
        "scheduler": "karras",
        "resolution_width": 1024,
        "resolution_height": 1024,
    }
    
    response = test_client.post(
        f"/api/v1/models/configurations/base/{base_model_type}",
        json=config_data
    )
    assert response.status_code == 200
    
    result = response.json()
    assert result["name"] == "Pony Default"
    assert result["base_model"] == base_model_type
    assert result["model_id"] is None
    assert result["is_default"] is True


@pytest.mark.asyncio
async def test_get_base_model_configurations(test_client, db_conn):
    """Test retrieving configurations for a base model type"""
    base_model_type = "wan_2_2"
    
    config_data = {
        "base_model": base_model_type,
        "name": "WAN 2.2 Standard",
        "steps": 20,
        "cfg_scale": 7.5,
        "sampler": "dpmpp_2m",
        "scheduler": "karras",
        "resolution_width": 768,
        "resolution_height": 768,
        "additional_params": {
            "requires_high_noise_model": True,
            "requires_low_noise_model": True
        }
    }
    
    test_client.post(
        f"/api/v1/models/configurations/base/{base_model_type}",
        json=config_data
    )
    
    response = test_client.get(f"/api/v1/models/configurations/base/{base_model_type}")
    assert response.status_code == 200
    
    configs = response.json()
    assert len(configs) >= 1
    assert any(c["name"] == "WAN 2.2 Standard" for c in configs)


@pytest.mark.asyncio
async def test_update_configuration(test_client, db_conn):
    """Test updating a configuration"""
    model_id = "test_model_789"
    
    create_data = {
        "model_id": model_id,
        "base_model": "hidream",
        "name": "Original",
        "steps": 12,
        "cfg_scale": 5.0,
        "sampler": "euler_a",
        "scheduler": "karras",
        "resolution_width": 1024,
        "resolution_height": 1024,
    }
    
    create_response = test_client.post(
        f"/api/v1/models/{model_id}/configurations",
        json=create_data
    )
    config_id = create_response.json()["id"]
    
    update_data = {
        "name": "Updated",
        "steps": 25,
        "cfg_scale": 6.5
    }
    
    response = test_client.put(
        f"/api/v1/models/configurations/{config_id}",
        json=update_data
    )
    assert response.status_code == 200
    
    result = response.json()
    assert result["name"] == "Updated"
    assert result["steps"] == 25
    assert result["cfg_scale"] == 6.5
    assert result["sampler"] == "euler_a"


@pytest.mark.asyncio
async def test_delete_configuration(test_client, db_conn):
    """Test deleting a configuration"""
    model_id = "test_model_delete"
    
    create_data = {
        "model_id": model_id,
        "base_model": "qwen_image",
        "name": "To Delete",
        "steps": 10,
        "cfg_scale": 5.5,
        "sampler": "euler_a",
        "scheduler": "normal",
        "resolution_width": 1024,
        "resolution_height": 1024,
    }
    
    create_response = test_client.post(
        f"/api/v1/models/{model_id}/configurations",
        json=create_data
    )
    config_id = create_response.json()["id"]
    
    response = test_client.delete(f"/api/v1/models/configurations/{config_id}")
    assert response.status_code == 200
    
    get_response = test_client.get(f"/api/v1/models/configurations/{config_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_default_configuration(test_client, db_conn):
    """Test retrieving default configuration for a model"""
    model_id = "test_model_default"
    
    config_data = {
        "model_id": model_id,
        "base_model": "flux_dev",
        "name": "Default Config",
        "is_default": True,
        "steps": 28,
        "cfg_scale": 3.5,
        "sampler": "euler",
        "scheduler": "simple",
        "resolution_width": 1024,
        "resolution_height": 1024,
    }
    
    test_client.post(f"/api/v1/models/{model_id}/configurations", json=config_data)
    
    response = test_client.get(f"/api/v1/models/{model_id}/configurations/default")
    assert response.status_code == 200
    
    result = response.json()
    assert result["name"] == "Default Config"
    assert result["is_default"] is True
