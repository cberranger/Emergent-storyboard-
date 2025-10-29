import requests
import json

# Test the search endpoint with a real model ID
model_id = "cfe52eea-1e27-4101-abca-75a1ff48be6f"
url = f"http://localhost:8001/api/models/{model_id}/search-civitai"

# Test searching for "RealVisXL"
search_data = {"search_query": "RealVisXL"}

try:
    response = requests.post(url, json=search_data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {result.get('total_found', 0)} matches")
        for i, match in enumerate(result.get('matches', [])[:3]):
            model = match.get('civitai_model', {})
            print(f"\nMatch {i+1}:")
            print(f"  Name: {model.get('name')}")
            print(f"  Score: {match.get('match_score'):.3f}")
            print(f"  Reason: {match.get('match_reason')}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
