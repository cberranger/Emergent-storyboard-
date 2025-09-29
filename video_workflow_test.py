#!/usr/bin/env python3
"""
Detailed Video Workflow Testing
Tests the ComfyUI workflow generation logic for different model types
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001/api"

def test_video_specific_parameters():
    """Test that video-specific parameters are properly handled"""
    print("🎬 Testing Video-Specific Parameters...")
    
    # Test different model types and their video parameters
    test_cases = [
        {
            "model": "wan_2.2_t2v_high_noise_14B_fp8_scaled.safetensors",
            "expected_type": "wan_2_2",
            "expected_fps": 24,
            "expected_frames": 14
        },
        {
            "model": "wan_2.1_model.safetensors", 
            "expected_type": "wan_2_1",
            "expected_fps": 24,
            "expected_frames": 14
        },
        {
            "model": "sdxl_base_1.0.safetensors",
            "expected_type": "sdxl", 
            "expected_fps": 12,
            "expected_frames": 14
        }
    ]
    
    session = requests.Session()
    all_passed = True
    
    for case in test_cases:
        try:
            response = session.get(f"{BASE_URL}/models/parameters/{case['model']}", 
                                 params={"preset": "fast"}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                params = data.get("parameters", {})
                
                # Check model type detection
                detected_type = data.get("model_type")
                if detected_type != case["expected_type"]:
                    print(f"❌ {case['model']}: Expected type {case['expected_type']}, got {detected_type}")
                    all_passed = False
                    continue
                
                # Check video parameters
                fps = params.get("video_fps")
                frames = params.get("video_frames")
                
                if fps != case["expected_fps"]:
                    print(f"❌ {case['model']}: Expected {case['expected_fps']} fps, got {fps}")
                    all_passed = False
                    continue
                    
                if frames != case["expected_frames"]:
                    print(f"❌ {case['model']}: Expected {case['expected_frames']} frames, got {frames}")
                    all_passed = False
                    continue
                
                # Check for video-specific parameters that should be present
                video_specific_params = ["motion_bucket_id"] if "wan" in detected_type else []
                
                print(f"✅ {case['model']}: Type={detected_type}, FPS={fps}, Frames={frames}")
                
                # Check for model-specific requirements
                if detected_type == "wan_2_2":
                    required_components = ["requires_high_noise_model", "requires_low_noise_model", "requires_vae", "text_encoder"]
                    missing = [comp for comp in required_components if comp not in params]
                    if missing:
                        print(f"❌ {case['model']}: Missing Wan 2.2 requirements: {missing}")
                        all_passed = False
                    else:
                        print(f"   ✓ Wan 2.2 specific requirements present")
                
            else:
                print(f"❌ {case['model']}: HTTP {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {case['model']}: Error - {str(e)}")
            all_passed = False
    
    return all_passed

def test_model_specializations():
    """Test model specializations and capabilities"""
    print("\n🎯 Testing Model Specializations...")
    
    specialization_tests = [
        {
            "model": "qwen_image_model.safetensors",
            "expected_specialization": "text_rendering",
            "expected_lora_support": True
        },
        {
            "model": "qwen_edit_model.safetensors", 
            "expected_specialization": "image_editing",
            "expected_lora_support": False
        }
    ]
    
    session = requests.Session()
    all_passed = True
    
    for case in specialization_tests:
        try:
            response = session.get(f"{BASE_URL}/models/parameters/{case['model']}", 
                                 params={"preset": "fast"}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                params = data.get("parameters", {})
                
                # Check specialization
                specialization = params.get("specializes_in")
                if specialization != case["expected_specialization"]:
                    print(f"❌ {case['model']}: Expected specialization {case['expected_specialization']}, got {specialization}")
                    all_passed = False
                    continue
                
                # Check LoRA support
                lora_support = params.get("supports_lora", False)
                if lora_support != case["expected_lora_support"]:
                    print(f"❌ {case['model']}: Expected LoRA support {case['expected_lora_support']}, got {lora_support}")
                    all_passed = False
                    continue
                
                max_loras = params.get("max_loras", 0)
                expected_max = 2 if case["expected_lora_support"] else 0
                if max_loras != expected_max:
                    print(f"❌ {case['model']}: Expected max LoRAs {expected_max}, got {max_loras}")
                    all_passed = False
                    continue
                
                print(f"✅ {case['model']}: Specializes in {specialization}, LoRA support: {lora_support}")
                
            else:
                print(f"❌ {case['model']}: HTTP {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {case['model']}: Error - {str(e)}")
            all_passed = False
    
    return all_passed

def test_preset_differences():
    """Test that Fast and Quality presets have meaningful differences"""
    print("\n⚡ Testing Fast vs Quality Preset Differences...")
    
    test_models = ["flux_dev", "sdxl", "wan_2_2"]
    session = requests.Session()
    all_passed = True
    
    for model in test_models:
        try:
            # Get fast preset
            fast_response = session.get(f"{BASE_URL}/models/parameters/{model}", 
                                      params={"preset": "fast"}, timeout=30)
            
            # Get quality preset  
            quality_response = session.get(f"{BASE_URL}/models/parameters/{model}",
                                         params={"preset": "quality"}, timeout=30)
            
            if fast_response.status_code == 200 and quality_response.status_code == 200:
                fast_params = fast_response.json().get("parameters", {})
                quality_params = quality_response.json().get("parameters", {})
                
                # Quality should generally have more steps
                fast_steps = fast_params.get("steps", 0)
                quality_steps = quality_params.get("steps", 0)
                
                if quality_steps <= fast_steps:
                    print(f"❌ {model}: Quality preset should have more steps than fast (fast: {fast_steps}, quality: {quality_steps})")
                    all_passed = False
                    continue
                
                # Check video frame differences
                fast_frames = fast_params.get("video_frames", 0)
                quality_frames = quality_params.get("video_frames", 0)
                
                if quality_frames < fast_frames:
                    print(f"❌ {model}: Quality preset should have same or more frames than fast (fast: {fast_frames}, quality: {quality_frames})")
                    all_passed = False
                    continue
                
                print(f"✅ {model}: Fast({fast_steps} steps, {fast_frames} frames) vs Quality({quality_steps} steps, {quality_frames} frames)")
                
            else:
                print(f"❌ {model}: Failed to get presets (fast: {fast_response.status_code}, quality: {quality_response.status_code})")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {model}: Error - {str(e)}")
            all_passed = False
    
    return all_passed

def main():
    """Run detailed video workflow tests"""
    print("🔬 Detailed Video Workflow Testing")
    print("=" * 50)
    
    # Test video parameters
    video_params_ok = test_video_specific_parameters()
    
    # Test model specializations
    specializations_ok = test_model_specializations()
    
    # Test preset differences
    presets_ok = test_preset_differences()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DETAILED TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("Video Parameters", video_params_ok),
        ("Model Specializations", specializations_ok), 
        ("Preset Differences", presets_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} test categories passed")
    
    if passed == total:
        print("🎉 All detailed video workflow tests passed!")
        return True
    else:
        print("⚠️  Some detailed tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)