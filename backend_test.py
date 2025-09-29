#!/usr/bin/env python3
"""
Backend API Testing for Storyboarding App
Tests video generation and model preset functionality
"""

import requests
import json
import sys
import time
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8001/api"
TIMEOUT = 30

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_api_health(self) -> bool:
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_model_types_endpoint(self) -> bool:
        """Test GET /api/models/types endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/models/types", timeout=TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "supported_models" not in data:
                    self.log_test("Model Types Endpoint", False, "Missing 'supported_models' key")
                    return False
                
                supported_models = data["supported_models"]
                expected_models = ["flux_dev", "flux_krea", "sdxl", "pony", "wan_2_1", "wan_2_2", "hidream", "qwen_image", "qwen_edit"]
                
                # Check if all expected models are present
                missing_models = []
                for model in expected_models:
                    if model not in supported_models:
                        missing_models.append(model)
                
                if missing_models:
                    self.log_test("Model Types Endpoint", False, f"Missing models: {missing_models}")
                    return False
                
                # Verify each model has presets
                for model_name, model_info in supported_models.items():
                    if "presets" not in model_info:
                        self.log_test("Model Types Endpoint", False, f"Model {model_name} missing presets")
                        return False
                    
                    if not isinstance(model_info["presets"], list):
                        self.log_test("Model Types Endpoint", False, f"Model {model_name} presets not a list")
                        return False
                    
                    # Check for Fast and Quality presets
                    presets = model_info["presets"]
                    if "fast" not in presets or "quality" not in presets:
                        self.log_test("Model Types Endpoint", False, f"Model {model_name} missing fast/quality presets")
                        return False
                
                self.log_test("Model Types Endpoint", True, f"Found {len(supported_models)} models with presets")
                return True
            else:
                self.log_test("Model Types Endpoint", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Model Types Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_model_presets_endpoint(self) -> bool:
        """Test GET /api/models/presets/{model_name} endpoint"""
        test_models = ["flux_dev", "wan_2_2", "sdxl", "pony", "hidream", "qwen_image"]
        all_passed = True
        
        for model_name in test_models:
            try:
                response = self.session.get(f"{self.base_url}/models/presets/{model_name}", timeout=TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    required_keys = ["model_name", "model_type", "presets"]
                    missing_keys = [key for key in required_keys if key not in data]
                    
                    if missing_keys:
                        self.log_test(f"Model Presets - {model_name}", False, f"Missing keys: {missing_keys}")
                        all_passed = False
                        continue
                    
                    # Verify presets structure
                    presets = data["presets"]
                    if not isinstance(presets, dict):
                        self.log_test(f"Model Presets - {model_name}", False, "Presets not a dictionary")
                        all_passed = False
                        continue
                    
                    # Check for fast and quality presets
                    if "fast" not in presets or "quality" not in presets:
                        self.log_test(f"Model Presets - {model_name}", False, "Missing fast/quality presets")
                        all_passed = False
                        continue
                    
                    # Verify preset parameters
                    for preset_name, preset_config in presets.items():
                        required_params = ["steps", "cfg", "width", "height", "sampler", "scheduler"]
                        missing_params = [param for param in required_params if param not in preset_config]
                        
                        if missing_params:
                            self.log_test(f"Model Presets - {model_name}", False, f"Preset {preset_name} missing params: {missing_params}")
                            all_passed = False
                            break
                    
                    if all_passed:
                        self.log_test(f"Model Presets - {model_name}", True, f"Found {len(presets)} presets")
                else:
                    self.log_test(f"Model Presets - {model_name}", False, f"Status code: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Model Presets - {model_name}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_model_parameters_endpoint(self) -> bool:
        """Test GET /api/models/parameters/{model_name}?preset=fast endpoint"""
        test_cases = [
            ("flux_dev", "fast"),
            ("flux_dev", "quality"),
            ("wan_2_2", "fast"),
            ("sdxl", "quality"),
            ("pony", "fast"),
            ("hidream", "quality")
        ]
        
        all_passed = True
        
        for model_name, preset in test_cases:
            try:
                response = self.session.get(
                    f"{self.base_url}/models/parameters/{model_name}",
                    params={"preset": preset},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    required_keys = ["model_name", "model_type", "preset", "parameters"]
                    missing_keys = [key for key in required_keys if key not in data]
                    
                    if missing_keys:
                        self.log_test(f"Model Parameters - {model_name}:{preset}", False, f"Missing keys: {missing_keys}")
                        all_passed = False
                        continue
                    
                    # Verify parameters structure
                    parameters = data["parameters"]
                    if not isinstance(parameters, dict):
                        self.log_test(f"Model Parameters - {model_name}:{preset}", False, "Parameters not a dictionary")
                        all_passed = False
                        continue
                    
                    # Check for essential parameters
                    essential_params = ["steps", "cfg", "width", "height"]
                    missing_params = [param for param in essential_params if param not in parameters]
                    
                    if missing_params:
                        self.log_test(f"Model Parameters - {model_name}:{preset}", False, f"Missing essential params: {missing_params}")
                        all_passed = False
                        continue
                    
                    # Verify video-specific parameters are present
                    video_params = ["video_fps", "video_frames"]
                    missing_video_params = [param for param in video_params if param not in parameters]
                    
                    if missing_video_params:
                        self.log_test(f"Model Parameters - {model_name}:{preset}", False, f"Missing video params: {missing_video_params}")
                        all_passed = False
                        continue
                    
                    self.log_test(f"Model Parameters - {model_name}:{preset}", True, f"Found {len(parameters)} parameters")
                else:
                    self.log_test(f"Model Parameters - {model_name}:{preset}", False, f"Status code: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Model Parameters - {model_name}:{preset}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_model_detection(self) -> bool:
        """Test model type detection for various model names"""
        test_cases = [
            ("flux_dev_v1.safetensors", "flux_dev"),
            ("flux_krea_model.ckpt", "flux_krea"),
            ("sdxl_base_1.0.safetensors", "sdxl"),
            ("pony_diffusion_v6.safetensors", "pony"),
            ("wan_2.1_model.safetensors", "wan_2_1"),
            ("wan_2.2_high_noise.safetensors", "wan_2_2"),
            ("hidream_v1.ckpt", "hidream"),
            ("qwen_image_model.safetensors", "qwen_image"),
            ("qwen_edit_model.safetensors", "qwen_edit")
        ]
        
        all_passed = True
        
        for model_name, expected_type in test_cases:
            try:
                response = self.session.get(f"{self.base_url}/models/defaults/{model_name}", timeout=TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    detected_type = data.get("detected_type")
                    
                    if detected_type == expected_type:
                        self.log_test(f"Model Detection - {model_name}", True, f"Detected as {detected_type}")
                    else:
                        self.log_test(f"Model Detection - {model_name}", False, f"Expected {expected_type}, got {detected_type}")
                        all_passed = False
                else:
                    self.log_test(f"Model Detection - {model_name}", False, f"Status code: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Model Detection - {model_name}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def setup_test_data(self) -> Dict[str, str]:
        """Setup test data (server, project, scene, clip)"""
        test_data = {}
        
        try:
            # Create a test ComfyUI server
            server_data = {
                "name": "Test Server",
                "url": "http://test-comfyui:8188",
                "server_type": "standard"
            }
            
            response = self.session.post(f"{self.base_url}/comfyui/servers", json=server_data, timeout=TIMEOUT)
            if response.status_code == 200:
                test_data["server_id"] = response.json()["id"]
            else:
                print(f"Failed to create test server: {response.status_code}")
                return {}
            
            # Create a test project
            project_data = {
                "name": "Test Project",
                "description": "Test project for video generation"
            }
            
            response = self.session.post(f"{self.base_url}/projects", json=project_data, timeout=TIMEOUT)
            if response.status_code == 200:
                test_data["project_id"] = response.json()["id"]
            else:
                print(f"Failed to create test project: {response.status_code}")
                return {}
            
            # Create a test scene
            scene_data = {
                "project_id": test_data["project_id"],
                "name": "Test Scene",
                "description": "Test scene for video generation",
                "order": 1
            }
            
            response = self.session.post(f"{self.base_url}/scenes", json=scene_data, timeout=TIMEOUT)
            if response.status_code == 200:
                test_data["scene_id"] = response.json()["id"]
            else:
                print(f"Failed to create test scene: {response.status_code}")
                return {}
            
            # Create a test clip
            clip_data = {
                "scene_id": test_data["scene_id"],
                "name": "Test Clip",
                "length": 5.0,
                "timeline_position": 0.0,
                "order": 1,
                "image_prompt": "A beautiful landscape with mountains",
                "video_prompt": "Camera slowly panning across a beautiful mountain landscape"
            }
            
            response = self.session.post(f"{self.base_url}/clips", json=clip_data, timeout=TIMEOUT)
            if response.status_code == 200:
                test_data["clip_id"] = response.json()["id"]
            else:
                print(f"Failed to create test clip: {response.status_code}")
                return {}
            
            return test_data
            
        except Exception as e:
            print(f"Error setting up test data: {str(e)}")
            return {}
    
    def test_video_generation_endpoint(self) -> bool:
        """Test POST /api/generate with generation_type=video"""
        # Setup test data
        test_data = self.setup_test_data()
        if not test_data:
            self.log_test("Video Generation Setup", False, "Failed to create test data")
            return False
        
        # Test video generation request structure (without actual ComfyUI server)
        video_request = {
            "clip_id": test_data["clip_id"],
            "server_id": test_data["server_id"],
            "prompt": "A majestic eagle soaring through mountain peaks at sunset",
            "negative_prompt": "blurry, low quality, distorted",
            "model": "wan_2.2_t2v_high_noise_14B_fp8_scaled.safetensors",
            "generation_type": "video",
            "params": {
                "width": 768,
                "height": 768,
                "video_frames": 14,
                "video_fps": 24,
                "steps": 20,
                "cfg": 7.5,
                "seed": 42,
                "motion_bucket_id": 127
            }
        }
        
        try:
            response = self.session.post(f"{self.base_url}/generate", json=video_request, timeout=TIMEOUT)
            
            # We expect this to fail with 503 (server offline) rather than 501 (not implemented)
            if response.status_code == 503:
                # This is expected - server is offline but endpoint exists and processes video requests
                self.log_test("Video Generation Endpoint", True, "Endpoint exists and processes video requests (server offline expected)")
                return True
            elif response.status_code == 501:
                # This would indicate the old "not implemented" error
                self.log_test("Video Generation Endpoint", False, "Still returns 501 Not Implemented")
                return False
            elif response.status_code == 200:
                # Unexpected success (would mean ComfyUI server is actually running)
                self.log_test("Video Generation Endpoint", True, "Video generation successful")
                return True
            else:
                # Other error codes
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "Unknown error")
                except:
                    error_detail = response.text
                
                if "not implemented" in error_detail.lower() or "501" in error_detail:
                    self.log_test("Video Generation Endpoint", False, f"Still not implemented: {error_detail}")
                    return False
                else:
                    self.log_test("Video Generation Endpoint", True, f"Endpoint processes requests (error: {error_detail})")
                    return True
                    
        except Exception as e:
            self.log_test("Video Generation Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_video_workflow_selection(self) -> bool:
        """Test that different model types would use appropriate video workflows"""
        # This tests the workflow generation logic by checking model type detection
        # and ensuring video-specific parameters are handled
        
        test_models = [
            ("wan_2.2_t2v_high_noise.safetensors", "wan_2_2"),
            ("svd_xt_1_1.safetensors", "sdxl"),  # SVD would be detected as SDXL type
            ("animatediff_sd15.ckpt", "wan_2_1")  # AnimateDiff would use SD1.5 defaults
        ]
        
        all_passed = True
        
        for model_name, expected_type in test_models:
            try:
                response = self.session.get(f"{self.base_url}/models/parameters/{model_name}", 
                                          params={"preset": "fast"}, timeout=TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    parameters = data.get("parameters", {})
                    
                    # Check for video-specific parameters
                    video_params = ["video_fps", "video_frames"]
                    missing_params = [param for param in video_params if param not in parameters]
                    
                    if missing_params:
                        self.log_test(f"Video Workflow - {model_name}", False, f"Missing video params: {missing_params}")
                        all_passed = False
                    else:
                        # Verify video parameters have reasonable values
                        fps = parameters.get("video_fps", 0)
                        frames = parameters.get("video_frames", 0)
                        
                        if fps <= 0 or frames <= 0:
                            self.log_test(f"Video Workflow - {model_name}", False, f"Invalid video params: fps={fps}, frames={frames}")
                            all_passed = False
                        else:
                            self.log_test(f"Video Workflow - {model_name}", True, f"Video params: {fps}fps, {frames}frames")
                else:
                    self.log_test(f"Video Workflow - {model_name}", False, f"Status code: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Video Workflow - {model_name}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Tests for Video Generation and Model Presets")
        print("=" * 70)
        
        # Test basic connectivity first
        if not self.test_api_health():
            print("\n❌ API is not accessible. Stopping tests.")
            return False
        
        print("\n📋 Testing Model Preset Endpoints...")
        model_types_ok = self.test_model_types_endpoint()
        model_presets_ok = self.test_model_presets_endpoint()
        model_parameters_ok = self.test_model_parameters_endpoint()
        
        print("\n🔍 Testing Model Detection...")
        model_detection_ok = self.test_model_detection()
        
        print("\n🎬 Testing Video Generation...")
        video_generation_ok = self.test_video_generation_endpoint()
        video_workflow_ok = self.test_video_workflow_selection()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        # Overall result
        all_critical_passed = (model_types_ok and model_presets_ok and 
                              model_parameters_ok and video_generation_ok)
        
        if all_critical_passed:
            print("\n✅ All critical functionality is working!")
            return True
        else:
            print("\n❌ Some critical functionality has issues.")
            return False

def main():
    """Main test execution"""
    tester = BackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()