"""Test script to verify DTO imports"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

print("Testing DTO imports...")

try:
    from dtos import (
        InferenceConfigurationDTO,
        InferenceConfigurationCreateDTO,
        InferenceConfigurationUpdateDTO
    )
    print("[PASS] All inference configuration DTOs imported successfully")
except ImportError as e:
    print(f"[FAIL] Failed to import DTOs: {e}")
    sys.exit(1)

print("\nAll DTO tests passed!")
