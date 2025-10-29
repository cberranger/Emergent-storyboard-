import json
import os

# Test loading the JSON file
json_path = os.path.join(os.path.dirname(__file__), "utils", "sdxl_checkpoints.json")
print(f"JSON path: {json_path}")
print(f"JSON exists: {os.path.exists(json_path)}")

if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        civitai_database = json.load(f)
    
    print(f"Successfully loaded {len(civitai_database)} models")
    
    # Test the matching function
    from server import find_best_civitai_match_local
    
    test_models = ["RealVisXL", "SDXL Base", "Juggernaut"]
    
    for model_name in test_models:
        match = find_best_civitai_match_local(model_name, civitai_database)
        if match:
            print(f"Found match for '{model_name}': {match.get('name')}")
        else:
            print(f"No match found for '{model_name}'")
