import requests
import json

# Test the sync endpoint
model_id = "test_model_123"  # Use a test model ID
url = f"http://localhost:8000/api/models/{model_id}/sync-civitai"

try:
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
