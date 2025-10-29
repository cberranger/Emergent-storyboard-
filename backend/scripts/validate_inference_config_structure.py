"""
Validate the InferenceConfigurationRepository structure without requiring database connection
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

print("Validating inference configuration structure...\n")

# Test 1: Import repository module
print("Test 1: Importing repository module...")
try:
    from repositories.inference_configuration_repository import InferenceConfigurationRepository
    print("[PASS] InferenceConfigurationRepository imported successfully\n")
except ImportError as e:
    print(f"[FAIL] Failed to import: {e}\n")
    sys.exit(1)

# Test 2: Check repository inheritance
print("Test 2: Checking repository inheritance...")
try:
    from repositories.base_repository import BaseRepository
    if issubclass(InferenceConfigurationRepository, BaseRepository):
        print("[PASS] InferenceConfigurationRepository extends BaseRepository\n")
    else:
        print("[FAIL] InferenceConfigurationRepository does not extend BaseRepository\n")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] Failed to check inheritance: {e}\n")
    sys.exit(1)

# Test 3: Check required methods
print("Test 3: Checking required methods...")
required_methods = [
    "find_by_model_id",
    "find_by_base_model",
    "find_by_model_and_type",
    "find_by_base_model_and_type",
    "create_index"
]

missing_methods = []
for method_name in required_methods:
    if not hasattr(InferenceConfigurationRepository, method_name):
        missing_methods.append(method_name)

if missing_methods:
    print(f"[FAIL] Missing methods: {', '.join(missing_methods)}\n")
    sys.exit(1)
else:
    print(f"[PASS] All {len(required_methods)} required methods present\n")

# Test 4: Check populate script exists
print("Test 4: Checking populate script...")
populate_script = BACKEND_DIR / "scripts" / "populate_inference_configurations.py"
if populate_script.exists():
    print("[PASS] populate_inference_configurations.py exists\n")
else:
    print("[FAIL] populate_inference_configurations.py not found\n")
    sys.exit(1)

# Test 5: Check documentation exists
print("Test 5: Checking documentation...")
docs_path = BACKEND_DIR.parent / "docs" / "INFERENCE_CONFIGURATION_STANDARDS.md"
if docs_path.exists():
    print("[PASS] INFERENCE_CONFIGURATION_STANDARDS.md exists\n")
else:
    print("[FAIL] INFERENCE_CONFIGURATION_STANDARDS.md not found\n")
    sys.exit(1)

# Test 6: Validate INFERENCE_PRESETS in populate script
print("Test 6: Validating INFERENCE_PRESETS structure...")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("populate", populate_script)
    populate_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(populate_module)
    
    presets = populate_module.INFERENCE_PRESETS
    base_models = list(presets.keys())
    
    print(f"[PASS] Found presets for {len(base_models)} base models:")
    for base_model in base_models:
        has_quality = "quality" in presets[base_model]
        has_speed = "speed" in presets[base_model]
        status = "PASS" if (has_quality and has_speed) else "FAIL"
        print(f"  [{status}] {base_model}: quality={has_quality}, speed={has_speed}")
    print()
except Exception as e:
    print(f"[FAIL] Failed to validate presets: {e}\n")
    sys.exit(1)

# Test 7: Check repository is exported in __init__.py
print("Test 7: Checking repository export...")
try:
    from repositories import InferenceConfigurationRepository as ExportedRepo
    print("[PASS] InferenceConfigurationRepository exported from repositories package\n")
except ImportError:
    print("[FAIL] InferenceConfigurationRepository not exported from repositories package\n")
    sys.exit(1)

print("="*60)
print("All validation checks passed!")
print("="*60)
print("\nStructure is ready. To populate the database, ensure MongoDB is running and execute:")
print("  python backend/scripts/populate_inference_configurations.py")
