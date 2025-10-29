"""
Simple test script to validate InferenceConfigurationRepository functionality
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid

BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import db_manager
from repositories.inference_configuration_repository import InferenceConfigurationRepository


async def test_repository():
    """Test basic repository operations"""
    
    print("Connecting to database...")
    success = await db_manager.connect()
    if not success:
        print("Failed to connect to database")
        return False
    
    db = db_manager.get_database()
    repo = InferenceConfigurationRepository(db.inference_configurations)
    
    print("✓ Connected to database\n")
    
    # Test 1: Create indexes
    print("Test 1: Creating indexes...")
    try:
        await repo.create_index()
        print("✓ Indexes created successfully\n")
    except Exception as e:
        print(f"✗ Failed to create indexes: {e}\n")
        return False
    
    # Test 2: Create a test configuration
    print("Test 2: Creating test configuration...")
    test_config = {
        "id": str(uuid.uuid4()),
        "model_id": "test-model-123",
        "base_model": "sdxl",
        "configuration_type": "quality",
        "steps": 30,
        "cfg_scale": 7.5,
        "sampler": "dpmpp_2m",
        "scheduler": "karras",
        "model_specific_params": {
            "width": 1024,
            "height": 1024,
            "clip_skip": -1
        },
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    try:
        created = await repo.create(test_config)
        print(f"✓ Created configuration: {created['id']}\n")
    except Exception as e:
        print(f"✗ Failed to create configuration: {e}\n")
        return False
    
    # Test 3: Find by model_id
    print("Test 3: Finding by model_id...")
    try:
        configs = await repo.find_by_model_id("test-model-123")
        print(f"✓ Found {len(configs)} configuration(s) for model_id\n")
    except Exception as e:
        print(f"✗ Failed to find by model_id: {e}\n")
        return False
    
    # Test 4: Find by model_id and type
    print("Test 4: Finding by model_id and type...")
    try:
        config = await repo.find_by_model_and_type("test-model-123", "quality")
        if config:
            print(f"✓ Found quality configuration: {config['steps']} steps, cfg_scale {config['cfg_scale']}\n")
        else:
            print("✗ Configuration not found\n")
            return False
    except Exception as e:
        print(f"✗ Failed to find by model_id and type: {e}\n")
        return False
    
    # Test 5: Find by base_model
    print("Test 5: Finding by base_model...")
    try:
        configs = await repo.find_by_base_model("sdxl")
        print(f"✓ Found {len(configs)} configuration(s) for base_model 'sdxl'\n")
    except Exception as e:
        print(f"✗ Failed to find by base_model: {e}\n")
        return False
    
    # Test 6: Find by base_model and type
    print("Test 6: Finding by base_model and type...")
    try:
        config = await repo.find_by_base_model_and_type("sdxl", "quality")
        if config:
            print(f"✓ Found base_model quality configuration\n")
        else:
            print("✗ Configuration not found (may be expected if none exist)\n")
    except Exception as e:
        print(f"✗ Failed to find by base_model and type: {e}\n")
        return False
    
    # Cleanup: Delete test configuration
    print("Cleanup: Deleting test configuration...")
    try:
        deleted = await repo.delete_by_id(test_config["id"])
        if deleted:
            print("✓ Test configuration deleted\n")
        else:
            print("⚠ Test configuration not deleted (may not exist)\n")
    except Exception as e:
        print(f"⚠ Failed to delete test configuration: {e}\n")
    
    await db_manager.disconnect()
    
    print("="*60)
    print("All tests passed! ✓")
    print("="*60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_repository())
    sys.exit(0 if success else 1)
