import requests

# Test the sync endpoint with a real model ID
model_id = "cfe52eea-1e27-4101-abca-75a1ff48be6f"  # First model from the list
url = f"http://localhost:8001/api/models/{model_id}/sync-civitai"

try:
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Model synced with Civitai info")
        print(f"Civitai Model ID: {result.get('civitai_info', {}).get('modelId')}")
        print(f"Civitai Model Name: {result.get('civitai_info', {}).get('name')}")
        print(f"Match Quality: {result.get('civitai_match_quality')}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
