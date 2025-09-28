#!/usr/bin/env python3
"""
Focused InfiniteTalk API Test
"""

import requests
import json
import uuid
from pathlib import Path

# Get backend URL from frontend .env
def get_backend_url():
    frontend_env_path = Path("/app/frontend/.env")
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

print(f"Testing InfiniteTalk at: {API_URL}")

# Create minimal test data
def setup_minimal_test():
    # Create server
    server_data = {
        "name": "Test RunPod Server",
        "url": "https://api.runpod.ai/v2/test-endpoint",
        "server_type": "runpod",
        "api_key": "test-api-key"
    }
    
    server_response = requests.post(f"{API_URL}/comfyui/servers", json=server_data)
    if server_response.status_code != 200:
        print(f"Failed to create server: {server_response.text}")
        return None, None, None
    
    server_id = server_response.json()['id']
    
    # Create project
    project_data = {"name": "Test Project", "description": "Test"}
    project_response = requests.post(f"{API_URL}/projects", json=project_data)
    if project_response.status_code != 200:
        print(f"Failed to create project: {project_response.text}")
        return None, None, None
    
    project_id = project_response.json()['id']
    
    # Create scene
    scene_data = {
        "project_id": project_id,
        "name": "Test Scene",
        "description": "Test scene",
        "order": 1
    }
    scene_response = requests.post(f"{API_URL}/scenes", json=scene_data)
    if scene_response.status_code != 200:
        print(f"Failed to create scene: {scene_response.text}")
        return None, None, None
    
    scene_id = scene_response.json()['id']
    
    # Create clip
    clip_data = {
        "scene_id": scene_id,
        "name": "Test Clip",
        "lyrics": "Hello world",
        "length": 5.0,
        "order": 1
    }
    clip_response = requests.post(f"{API_URL}/clips", json=clip_data)
    if clip_response.status_code != 200:
        print(f"Failed to create clip: {clip_response.text}")
        return None, None, None
    
    clip_id = clip_response.json()['id']
    
    return server_id, project_id, clip_id

def test_infinitetalk_detailed():
    server_id, project_id, clip_id = setup_minimal_test()
    if not all([server_id, project_id, clip_id]):
        print("Failed to setup test data")
        return
    
    print(f"Created: server_id={server_id}, project_id={project_id}, clip_id={clip_id}")
    
    # Test InfiniteTalk generation
    infinitetalk_request = {
        "clip_id": clip_id,
        "server_id": server_id,
        "prompt": "A person speaking naturally",
        "generation_type": "infinitetalk",
        "infinitetalk_params": {
            "input_type": "image",
            "person_count": "single",
            "quality_mode": "high",
            "width": 512,
            "height": 512
        }
    }
    
    print("\nTesting InfiniteTalk generation...")
    print(f"Request: {json.dumps(infinitetalk_request, indent=2)}")
    
    response = requests.post(f"{API_URL}/generate", json=infinitetalk_request, timeout=30)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"Response Body: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Response Text: {response.text}")

if __name__ == "__main__":
    test_infinitetalk_detailed()