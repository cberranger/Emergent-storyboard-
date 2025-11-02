"""Test script for FaceFusion API endpoints"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api.v1.facefusion_router import (
    FaceEnhanceRequest,
    FaceAgeAdjustRequest,
    FaceSwapRequest,
    FaceMaskRequest,
    FaceDetectionRequest,
    FaceEditRequest,
    VideoProcessRequest,
    BatchOperation,
    BatchProcessRequest,
)


def test_request_models():
    """Test that all request models can be instantiated"""
    
    print("Testing FaceEnhanceRequest...")
    enhance_req = FaceEnhanceRequest(
        image_url="http://example.com/image.jpg",
        enhancement_model="gfpgan_1.4"
    )
    assert enhance_req.image_url == "http://example.com/image.jpg"
    assert enhance_req.enhancement_model == "gfpgan_1.4"
    print("✓ FaceEnhanceRequest OK")
    
    print("Testing FaceAgeAdjustRequest...")
    age_req = FaceAgeAdjustRequest(
        image_url="http://example.com/image.jpg",
        target_age=25
    )
    assert age_req.target_age == 25
    print("✓ FaceAgeAdjustRequest OK")
    
    print("Testing FaceSwapRequest...")
    swap_req = FaceSwapRequest(
        source_face_url="http://example.com/face.jpg",
        target_image_url="http://example.com/target.jpg"
    )
    assert swap_req.source_face_url == "http://example.com/face.jpg"
    print("✓ FaceSwapRequest OK")
    
    print("Testing FaceMaskRequest...")
    mask_req = FaceMaskRequest(
        image_url="http://example.com/image.jpg",
        mask_types=["box", "occlusion"]
    )
    assert len(mask_req.mask_types) == 2
    print("✓ FaceMaskRequest OK")
    
    print("Testing FaceDetectionRequest...")
    detect_req = FaceDetectionRequest(
        image_url="http://example.com/image.jpg"
    )
    assert detect_req.face_detector_model == "yoloface"
    print("✓ FaceDetectionRequest OK")
    
    print("Testing FaceEditRequest...")
    edit_req = FaceEditRequest(
        image_url="http://example.com/image.jpg",
        mouth_smile=50,
        eye_open_ratio=20
    )
    assert edit_req.mouth_smile == 50
    print("✓ FaceEditRequest OK")
    
    print("Testing VideoProcessRequest...")
    video_req = VideoProcessRequest(
        video_url="http://example.com/video.mp4",
        operation_type="enhance",
        parameters={"model": "gfpgan_1.4"}
    )
    assert video_req.operation_type == "enhance"
    print("✓ VideoProcessRequest OK")
    
    print("Testing BatchProcessRequest...")
    batch_req = BatchProcessRequest(
        operations=[
            BatchOperation(
                operation_type="enhance",
                image_url="http://example.com/image1.jpg",
                parameters={"model": "gfpgan_1.4"}
            ),
            BatchOperation(
                operation_type="age_adjust",
                image_url="http://example.com/image2.jpg",
                parameters={"target_age": 30}
            )
        ]
    )
    assert len(batch_req.operations) == 2
    print("✓ BatchProcessRequest OK")


def test_dto_imports():
    """Test that DTOs can be imported"""
    from dtos.character_dtos import (
        FaceFusionProcessingHistoryEntry,
        FaceFusionPreferredSettings,
        FaceFusionOutputGallery,
    )
    
    print("Testing FaceFusionProcessingHistoryEntry...")
    history = FaceFusionProcessingHistoryEntry(
        operation_type="enhance",
        input_image_url="http://example.com/input.jpg",
        output_image_url="http://example.com/output.jpg",
        parameters={"model": "gfpgan_1.4"},
        success=True
    )
    assert history.operation_type == "enhance"
    print("✓ FaceFusionProcessingHistoryEntry OK")
    
    print("Testing FaceFusionPreferredSettings...")
    settings = FaceFusionPreferredSettings(
        enhancement_model="codeformer",
        face_enhancer_blend=0.8
    )
    assert settings.enhancement_model == "codeformer"
    assert settings.face_enhancer_blend == 0.8
    print("✓ FaceFusionPreferredSettings OK")
    
    print("Testing FaceFusionOutputGallery...")
    gallery = FaceFusionOutputGallery(
        enhanced_faces=["http://example.com/enhanced1.jpg"],
        age_variants={25: "http://example.com/age25.jpg"}
    )
    assert len(gallery.enhanced_faces) == 1
    assert 25 in gallery.age_variants
    print("✓ FaceFusionOutputGallery OK")


if __name__ == "__main__":
    print("=" * 60)
    print("FaceFusion API Test Suite")
    print("=" * 60)
    
    try:
        test_request_models()
        print()
        test_dto_imports()
        print()
        print("=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Test failed: {e}")
        print("=" * 60)
        sys.exit(1)
