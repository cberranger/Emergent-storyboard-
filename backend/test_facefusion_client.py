import asyncio
import pytest
from server import FaceFusionClient

@pytest.mark.asyncio
async def test_facefusion_client_connection():
    """Test FaceFusion client connection"""
    client = FaceFusionClient("http://192.168.1.10:9002")
    is_connected = await client.check_connection()
    print(f"FaceFusion connection status: {is_connected}")
    assert isinstance(is_connected, bool)

@pytest.mark.asyncio
async def test_facefusion_client_methods_exist():
    """Test that all required methods exist on FaceFusionClient"""
    client = FaceFusionClient()
    
    assert hasattr(client, 'swap_face')
    assert hasattr(client, 'enhance_face')
    assert hasattr(client, 'edit_face_age')
    assert hasattr(client, 'edit_face_expression')
    assert hasattr(client, 'edit_face_features')
    assert hasattr(client, 'process_video')
    assert hasattr(client, 'extract_frames')
    assert hasattr(client, 'submit_job')
    assert hasattr(client, 'get_job_status')
    assert hasattr(client, 'poll_job')
    assert hasattr(client, 'cancel_job')
    assert hasattr(client, 'get_job_result')
    assert hasattr(client, 'check_connection')

@pytest.mark.asyncio
async def test_facefusion_client_parameters():
    """Test that methods accept correct parameters"""
    client = FaceFusionClient()
    
    import inspect
    
    swap_sig = inspect.signature(client.swap_face)
    assert 'source_face' in swap_sig.parameters
    assert 'target_media' in swap_sig.parameters
    assert 'face_swapper_model' in swap_sig.parameters
    assert 'source_face_index' in swap_sig.parameters
    assert 'target_face_index' in swap_sig.parameters
    assert 'face_mask_types' in swap_sig.parameters
    assert 'face_enhancer_model' in swap_sig.parameters
    
    enhance_sig = inspect.signature(client.enhance_face)
    assert 'target_media' in enhance_sig.parameters
    assert 'face_enhancer_model' in enhance_sig.parameters
    assert 'face_enhancer_blend' in enhance_sig.parameters
    assert 'face_enhancer_iterations' in enhance_sig.parameters
    
    age_sig = inspect.signature(client.edit_face_age)
    assert 'target_media' in age_sig.parameters
    assert 'face_editor_age' in age_sig.parameters
    assert 'face_editor_age_direction' in age_sig.parameters
    
    expr_sig = inspect.signature(client.edit_face_expression)
    assert 'face_editor_mouth_smile' in expr_sig.parameters
    assert 'face_editor_eye_open_ratio' in expr_sig.parameters
    assert 'face_editor_head_pitch' in expr_sig.parameters
    
    feat_sig = inspect.signature(client.edit_face_features)
    assert 'face_editor_nose_length' in feat_sig.parameters
    assert 'face_editor_eye_size' in feat_sig.parameters
    
    video_sig = inspect.signature(client.process_video)
    assert 'source_face' in video_sig.parameters
    assert 'target_video' in video_sig.parameters
    assert 'trim_frame_start' in video_sig.parameters
    assert 'output_video_fps' in video_sig.parameters
    
    job_sig = inspect.signature(client.submit_job)
    assert 'operation' in job_sig.parameters
    assert 'params' in job_sig.parameters
    assert 'priority' in job_sig.parameters

if __name__ == "__main__":
    asyncio.run(test_facefusion_client_connection())
    asyncio.run(test_facefusion_client_methods_exist())
    asyncio.run(test_facefusion_client_parameters())
    print("All tests passed!")
