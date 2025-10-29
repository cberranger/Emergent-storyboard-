import requests

# Test the new active models endpoints
base_url = "http://localhost:8001/api"

# Test 1: Get all backends
print("Testing GET /backends")
try:
    response = requests.get(f"{base_url}/backends")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        backends = response.json()
        print(f"Found {len(backends)} backends")
        for backend in backends[:3]:
            print(f"  - {backend.get('name')} ({backend.get('url')})")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test 2: Get active models
print("Testing GET /active-models")
try:
    response = requests.get(f"{base_url}/active-models")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        print(f"Found {len(models)} active models")
        for model in models[:5]:
            print(f"  - {model.get('model_name')} on {model.get('backend_name')}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test 3: Get models for a specific backend (if any backends exist)
print("Testing GET /backends/{backend_id}/models")
try:
    # First get a backend ID
    backends_response = requests.get(f"{base_url}/backends")
    if backends_response.status_code == 200:
        backends = backends_response.json()
        if backends:
            backend_id = backends[0]['id']
            print(f"Getting models for backend: {backend_id}")
            
            response = requests.get(f"{base_url}/backends/{backend_id}/models")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                models = response.json()
                print(f"Found {len(models)} models on this backend")
                for model in models[:5]:
                    print(f"  - {model.get('model_name')} ({model.get('model_type')})")
except Exception as e:
    print(f"Error: {e}")
