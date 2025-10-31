"""Manual test script for model configurations API"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from repositories.inference_configuration_repository import ModelConfigurationRepository
from services.model_config import ModelConfigurationService
from dtos.inference_config_dtos import ModelConfigurationCreateDTO


async def test_model_configurations():
    """Test model configurations service directly"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["storyboard"]
    
    repository = ModelConfigurationRepository(db.model_configurations)
    service = ModelConfigurationService(repository)
    
    print("Creating model configuration...")
    config_data = ModelConfigurationCreateDTO(
        model_id="test_model_123",
        base_model="sdxl",
        name="High Quality",
        description="High quality settings for SDXL",
        is_default=True,
        steps=35,
        cfg_scale=7.5,
        sampler="dpmpp_2m",
        scheduler="karras",
        clip_skip=-1,
        resolution_width=1024,
        resolution_height=1024,
        batch_size=1,
        seed=-1,
        additional_params={"refiner_steps": 5}
    )
    
    created = await service.create_configuration(config_data)
    print(f"Created configuration: {created.id} - {created.name}")
    
    print("\nFetching configurations for model...")
    configs = await service.get_configurations_by_model("test_model_123")
    print(f"Found {len(configs)} configuration(s)")
    for config in configs:
        print(f"  - {config.name}: {config.steps} steps, CFG {config.cfg_scale}")
    
    print("\nCreating base model configuration...")
    base_config_data = ModelConfigurationCreateDTO(
        model_id=None,
        base_model="flux_dev",
        name="Flux Fast",
        description="Fast settings for Flux Dev",
        is_default=False,
        steps=8,
        cfg_scale=2.0,
        sampler="euler",
        scheduler="simple",
        resolution_width=1024,
        resolution_height=1024,
    )
    
    created_base = await service.create_configuration(base_config_data)
    print(f"Created base configuration: {created_base.id} - {created_base.name}")
    
    print("\nFetching configurations for base model...")
    base_configs = await service.get_configurations_by_base_model("flux_dev")
    print(f"Found {len(base_configs)} base configuration(s)")
    for config in base_configs:
        print(f"  - {config.name}: {config.steps} steps, CFG {config.cfg_scale}")
    
    print("\n✓ All tests completed successfully!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(test_model_configurations())
