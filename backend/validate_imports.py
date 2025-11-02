"""Validate that imports work correctly"""
try:
    from dtos.inference_config_dtos import (
        ModelConfigurationDTO,
        ModelConfigurationCreateDTO,
        ModelConfigurationUpdateDTO,
    )
    print("[OK] DTOs imported successfully")
except Exception as e:
    print(f"[FAIL] DTOs import failed: {e}")
    exit(1)

try:
    from dtos.character_dtos import (
        FaceFusionProcessingHistoryEntry,
        FaceFusionPreferredSettings,
        FaceFusionOutputGallery,
    )
    print("[OK] FaceFusion DTOs imported successfully")
except Exception as e:
    print(f"[FAIL] FaceFusion DTOs import failed: {e}")
    exit(1)

try:
    from repositories.inference_configuration_repository import ModelConfigurationRepository
    print("[OK] Repository imported successfully")
except Exception as e:
    print(f"[FAIL] Repository import failed: {e}")
    exit(1)

try:
    from services.model_config import ModelConfigurationService
    print("[OK] Service imported successfully")
except Exception as e:
    print(f"[FAIL] Service import failed: {e}")
    exit(1)

try:
    from api.v1 import models_router
    print("[OK] Router imported successfully")
except Exception as e:
    print(f"[FAIL] Router import failed: {e}")
    exit(1)

try:
    from api.v1 import facefusion_router
    print("[OK] FaceFusion router imported successfully")
except Exception as e:
    print(f"[FAIL] FaceFusion router import failed: {e}")
    exit(1)

print("\n[OK] All imports validated successfully!")
