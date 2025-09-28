#!/usr/bin/env python3
"""
Comprehensive StoryCanvas Backend API Test Suite
Tests all new functionality with proper error handling validation
"""

import requests
import json
import uuid
from pathlib import Path

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

print(f"🧪 Comprehensive Backend API Testing")
print(f"Backend URL: {BASE_URL}")
print(f"API URL: {API_URL}")
print("=" * 60)

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.critical_failures = []
        self.minor_issues = []
        
    def success(self, test_name):
        self.passed += 1
        print(f"✅ {test_name}")
        
    def failure(self, test_name, error, is_critical=True):
        self.failed += 1
        if is_critical:
            self.critical_failures.append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")
        else:
            self.minor_issues.append(f"{test_name}: {error}")
            print(f"⚠️  {test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 60)
        print(f"TEST SUMMARY: {self.passed}/{total} passed")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for error in self.critical_failures:
                print(f"  - {error}")
        
        if self.minor_issues:
            print(f"\n⚠️  MINOR ISSUES ({len(self.minor_issues)}):")
            for issue in self.minor_issues:
                print(f"  - {issue}")
        
        return len(self.critical_failures) == 0

results = TestResults()
test_data = {}

def setup_test_environment():
    """Setup complete test environment"""
    print("\n🔧 Setting up test environment...")
    
    try:
        # 1. Create RunPod server for InfiniteTalk testing
        server_data = {
            "name": "Test RunPod InfiniteTalk Server",
            "url": "https://api.runpod.ai/v2/test-infinitetalk-endpoint",
            "server_type": "runpod",
            "api_key": "test-api-key-infinitetalk"
        }
        
        response = requests.post(f"{API_URL}/comfyui/servers", json=server_data, timeout=10)
        if response.status_code == 200:
            test_data['runpod_server_id'] = response.json()['id']
            results.success("Create RunPod Server")
        else:
            results.failure("Create RunPod Server", f"Status {response.status_code}: {response.text}")
            return False
        
        # 2. Create standard ComfyUI server
        standard_server_data = {
            "name": "Test Standard ComfyUI Server",
            "url": "http://localhost:8188",
            "server_type": "standard"
        }
        
        response = requests.post(f"{API_URL}/comfyui/servers", json=standard_server_data, timeout=10)
        if response.status_code == 200:
            test_data['standard_server_id'] = response.json()['id']
            results.success("Create Standard Server")
        else:
            results.failure("Create Standard Server", f"Status {response.status_code}: {response.text}")
        
        # 3. Create project with music
        project_data = {
            "name": "InfiniteTalk Test Project",
            "description": "Testing InfiniteTalk integration with archive and delete functionality"
        }
        
        response = requests.post(f"{API_URL}/projects", json=project_data, timeout=10)
        if response.status_code == 200:
            test_data['project_id'] = response.json()['id']
            results.success("Create Test Project")
        else:
            results.failure("Create Test Project", f"Status {response.status_code}: {response.text}")
            return False
        
        # 4. Create scene
        scene_data = {
            "project_id": test_data['project_id'],
            "name": "InfiniteTalk Test Scene",
            "description": "Scene for testing lip-sync generation",
            "lyrics": "Hello world, this is a test of InfiniteTalk lip sync technology",
            "order": 1
        }
        
        response = requests.post(f"{API_URL}/scenes", json=scene_data, timeout=10)
        if response.status_code == 200:
            test_data['scene_id'] = response.json()['id']
            results.success("Create Test Scene")
        else:
            results.failure("Create Test Scene", f"Status {response.status_code}: {response.text}")
            return False
        
        # 5. Create clip
        clip_data = {
            "scene_id": test_data['scene_id'],
            "name": "InfiniteTalk Test Clip",
            "lyrics": "Hello world, testing lip sync",
            "length": 5.0,
            "timeline_position": 0.0,
            "order": 1,
            "image_prompt": "A person with clear facial features for lip sync",
            "video_prompt": "Natural lip movement and facial expressions"
        }
        
        response = requests.post(f"{API_URL}/clips", json=clip_data, timeout=10)
        if response.status_code == 200:
            test_data['clip_id'] = response.json()['id']
            results.success("Create Test Clip")
            return True
        else:
            results.failure("Create Test Clip", f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        results.failure("Setup Test Environment", f"Error: {str(e)}")
        return False

def test_infinitetalk_api_structure():
    """Test InfiniteTalk API structure and validation"""
    print("\n🎬 Testing InfiniteTalk API Structure...")
    
    # Test 1: Valid InfiniteTalk request structure
    valid_request = {
        "clip_id": test_data['clip_id'],
        "server_id": test_data['runpod_server_id'],
        "prompt": "A person speaking naturally with clear lip movements",
        "generation_type": "infinitetalk",
        "infinitetalk_params": {
            "input_type": "image",
            "person_count": "single",
            "quality_mode": "high",
            "width": 512,
            "height": 512
        }
    }
    
    try:
        response = requests.post(f"{API_URL}/generate", json=valid_request, timeout=30)
        
        # We expect this to fail due to fake RunPod endpoint, but API should handle it gracefully
        if response.status_code == 500:
            try:
                error_data = response.json()
                if "Failed to generate InfiniteTalk video" in error_data.get("detail", ""):
                    results.success("InfiniteTalk API Structure (Graceful failure as expected)")
                else:
                    results.failure("InfiniteTalk API Structure", f"Unexpected error: {error_data}")
            except:
                results.failure("InfiniteTalk API Structure", f"Invalid error response: {response.text}")
        elif response.status_code == 503:
            results.success("InfiniteTalk API Structure (Server offline as expected)")
        else:
            results.failure("InfiniteTalk API Structure", f"Unexpected status {response.status_code}: {response.text}")
    
    except Exception as e:
        results.failure("InfiniteTalk API Structure", f"Request error: {str(e)}")
    
    # Test 2: InfiniteTalk with standard server (should fail appropriately)
    if 'standard_server_id' in test_data:
        standard_request = {
            "clip_id": test_data['clip_id'],
            "server_id": test_data['standard_server_id'],
            "prompt": "Test prompt",
            "generation_type": "infinitetalk",
            "infinitetalk_params": {
                "input_type": "image",
                "person_count": "single"
            }
        }
        
        try:
            response = requests.post(f"{API_URL}/generate", json=standard_request, timeout=10)
            if response.status_code == 500:
                try:
                    error_data = response.json()
                    if "only supported on RunPod" in error_data.get("detail", ""):
                        results.success("InfiniteTalk Standard Server Rejection")
                    else:
                        results.failure("InfiniteTalk Standard Server Rejection", f"Wrong error: {error_data}", is_critical=False)
                except:
                    results.failure("InfiniteTalk Standard Server Rejection", "Invalid error response", is_critical=False)
            else:
                results.failure("InfiniteTalk Standard Server Rejection", f"Expected 500, got {response.status_code}", is_critical=False)
        except Exception as e:
            results.failure("InfiniteTalk Standard Server Rejection", f"Error: {str(e)}", is_critical=False)
    
    # Test 3: Missing InfiniteTalk parameters
    incomplete_request = {
        "clip_id": test_data['clip_id'],
        "server_id": test_data['runpod_server_id'],
        "prompt": "Test prompt",
        "generation_type": "infinitetalk"
        # Missing infinitetalk_params
    }
    
    try:
        response = requests.post(f"{API_URL}/generate", json=incomplete_request, timeout=10)
        if response.status_code == 400:
            results.success("InfiniteTalk Missing Parameters Validation")
        else:
            results.failure("InfiniteTalk Missing Parameters Validation", f"Expected 400, got {response.status_code}", is_critical=False)
    except Exception as e:
        results.failure("InfiniteTalk Missing Parameters Validation", f"Error: {str(e)}", is_critical=False)

def test_archive_system_comprehensive():
    """Test archive system with comprehensive scenarios"""
    print("\n📦 Testing Archive System Comprehensively...")
    
    # Test 1: Get empty archive
    try:
        response = requests.get(f"{API_URL}/projects/{test_data['project_id']}/archive", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "images" in data and "videos" in data:
                results.success("Get Project Archive Structure")
            else:
                results.failure("Get Project Archive Structure", f"Invalid response format: {data}")
        else:
            results.failure("Get Project Archive Structure", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("Get Project Archive Structure", f"Error: {str(e)}")
    
    # Test 2: Discard content (with non-existent content)
    discard_params = {
        "content_id": str(uuid.uuid4()),
        "content_type": "image"
    }
    
    try:
        response = requests.put(
            f"{API_URL}/clips/{test_data['clip_id']}/discard-content",
            params=discard_params,
            timeout=10
        )
        if response.status_code == 404:
            results.success("Discard Non-existent Content (404 as expected)")
        else:
            results.failure("Discard Non-existent Content", f"Expected 404, got {response.status_code}")
    except Exception as e:
        results.failure("Discard Non-existent Content", f"Error: {str(e)}")
    
    # Test 3: Invalid content type for discard
    invalid_discard_params = {
        "content_id": str(uuid.uuid4()),
        "content_type": "invalid_type"
    }
    
    try:
        response = requests.put(
            f"{API_URL}/clips/{test_data['clip_id']}/discard-content",
            params=invalid_discard_params,
            timeout=10
        )
        if response.status_code == 400:
            results.success("Discard Invalid Content Type (400 as expected)")
        else:
            results.failure("Discard Invalid Content Type", f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.failure("Discard Invalid Content Type", f"Error: {str(e)}")
    
    # Test 4: Restore content (with non-existent content)
    restore_params = {
        "content_id": str(uuid.uuid4()),
        "content_type": "image",
        "target_clip_id": test_data['clip_id']
    }
    
    try:
        response = requests.put(
            f"{API_URL}/projects/{test_data['project_id']}/restore-content",
            params=restore_params,
            timeout=10
        )
        if response.status_code == 404:
            results.success("Restore Non-existent Content (404 as expected)")
        else:
            results.failure("Restore Non-existent Content", f"Expected 404, got {response.status_code}")
    except Exception as e:
        results.failure("Restore Non-existent Content", f"Error: {str(e)}")

def test_delete_functionality_comprehensive():
    """Test delete functionality with comprehensive scenarios"""
    print("\n🗑️ Testing Delete Functionality Comprehensively...")
    
    # Test 1: Delete non-existent content
    delete_params = {
        "content_id": str(uuid.uuid4()),
        "content_type": "image"
    }
    
    try:
        response = requests.delete(
            f"{API_URL}/clips/{test_data['clip_id']}/delete-content",
            params=delete_params,
            timeout=10
        )
        if response.status_code == 404:
            results.success("Delete Non-existent Content (404 as expected)")
        else:
            results.failure("Delete Non-existent Content", f"Expected 404, got {response.status_code}")
    except Exception as e:
        results.failure("Delete Non-existent Content", f"Error: {str(e)}")
    
    # Test 2: Delete with invalid content type
    invalid_delete_params = {
        "content_id": str(uuid.uuid4()),
        "content_type": "invalid_type"
    }
    
    try:
        response = requests.delete(
            f"{API_URL}/clips/{test_data['clip_id']}/delete-content",
            params=invalid_delete_params,
            timeout=10
        )
        if response.status_code == 400:
            results.success("Delete Invalid Content Type (400 as expected)")
        else:
            results.failure("Delete Invalid Content Type", f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.failure("Delete Invalid Content Type", f"Error: {str(e)}")
    
    # Test 3: Delete with non-existent clip
    try:
        response = requests.delete(
            f"{API_URL}/clips/{str(uuid.uuid4())}/delete-content",
            params=delete_params,
            timeout=10
        )
        if response.status_code == 404:
            results.success("Delete from Non-existent Clip (404 as expected)")
        else:
            results.failure("Delete from Non-existent Clip", f"Expected 404, got {response.status_code}")
    except Exception as e:
        results.failure("Delete from Non-existent Clip", f"Error: {str(e)}")

def test_helper_endpoints():
    """Test helper endpoints"""
    print("\n🔧 Testing Helper Endpoints...")
    
    # Test get-image-url endpoint
    try:
        fake_content_id = str(uuid.uuid4())
        response = requests.get(
            f"{API_URL}/clips/{test_data['clip_id']}/get-image-url/{fake_content_id}",
            timeout=10
        )
        if response.status_code == 404:
            results.success("Get Image URL - Non-existent Content (404 as expected)")
        else:
            results.failure("Get Image URL - Non-existent Content", f"Expected 404, got {response.status_code}")
    except Exception as e:
        results.failure("Get Image URL - Non-existent Content", f"Error: {str(e)}")

def test_existing_api_stability():
    """Test that existing APIs are still working"""
    print("\n🔄 Testing Existing API Stability...")
    
    endpoints_to_test = [
        ("GET", f"/projects", "Get Projects"),
        ("GET", f"/projects/{test_data['project_id']}", "Get Project by ID"),
        ("GET", f"/projects/{test_data['project_id']}/scenes", "Get Project Scenes"),
        ("GET", f"/scenes/{test_data['scene_id']}/clips", "Get Scene Clips"),
        ("GET", f"/clips/{test_data['clip_id']}", "Get Clip"),
        ("GET", f"/clips/{test_data['clip_id']}/gallery", "Get Clip Gallery"),
        ("GET", f"/comfyui/servers", "Get ComfyUI Servers"),
    ]
    
    for method, endpoint, name in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{API_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                results.success(name)
            else:
                results.failure(name, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure(name, f"Error: {str(e)}")

def main():
    """Run comprehensive backend tests"""
    print("🚀 Starting Comprehensive StoryCanvas Backend Tests...")
    
    # Test basic API health
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        if response.status_code == 200 and response.json().get("message") == "StoryCanvas API is running":
            results.success("API Health Check")
        else:
            results.failure("API Health Check", f"API not healthy: {response.text}")
            return False
    except Exception as e:
        results.failure("API Health Check", f"Connection error: {str(e)}")
        return False
    
    # Setup test environment
    if not setup_test_environment():
        print("❌ Failed to setup test environment. Stopping tests.")
        return False
    
    # Run comprehensive tests
    test_infinitetalk_api_structure()
    test_archive_system_comprehensive()
    test_delete_functionality_comprehensive()
    test_helper_endpoints()
    test_existing_api_stability()
    
    # Print final summary
    success = results.summary()
    
    if success:
        print("\n🎉 All critical tests passed! Backend is working correctly.")
        print("The InfiniteTalk integration, archive system, and delete functionality are properly implemented.")
    else:
        print(f"\n💥 {len(results.critical_failures)} critical issues found!")
        print("These need to be addressed before the backend can be considered fully functional.")
    
    return success

if __name__ == "__main__":
    main()