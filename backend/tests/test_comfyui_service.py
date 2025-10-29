import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from services.comfyui_service import ComfyUIClient
from dtos.comfyui_dtos import ComfyUIServerDTO


class TestComfyUIClient:
    
    @pytest.fixture
    def standard_server(self):
        return ComfyUIServerDTO(
            id="server-001",
            name="Test Server",
            url="http://localhost:8188",
            server_type="standard",
            api_key=None,
            endpoint_id=None,
            is_online=True
        )
    
    @pytest.fixture
    def runpod_server(self):
        return ComfyUIServerDTO(
            id="server-002",
            name="RunPod Server",
            url="https://api.runpod.ai/v2/endpoint123",
            server_type="runpod",
            api_key="test-api-key",
            endpoint_id="endpoint123",
            is_online=True
        )
    
    def test_client_initialization_standard(self, standard_server):
        client = ComfyUIClient(standard_server)
        
        assert client.server_type == "standard"
        assert client.base_url == "http://localhost:8188"
        assert client.endpoint_id is None
    
    def test_client_initialization_runpod(self, runpod_server):
        client = ComfyUIClient(runpod_server)
        
        assert client.server_type == "runpod"
        assert client.endpoint_id == "endpoint123"
    
    async def test_check_connection_standard_success(self, standard_server):
        client = ComfyUIClient(standard_server)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_response
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await client.check_connection()
            
            assert result is True
    
    async def test_check_connection_standard_failure(self, standard_server):
        client = ComfyUIClient(standard_server)
        
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_response
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await client.check_connection()
            
            assert result is False
    
    async def test_check_connection_runpod_success(self, runpod_server):
        client = ComfyUIClient(runpod_server)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "RUNNING"})
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_response
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await client.check_connection()
            
            assert result is True
    
    async def test_check_connection_runpod_no_api_key(self):
        server = ComfyUIServerDTO(
            id="server-002",
            name="RunPod Server",
            url="https://api.runpod.ai/v2/endpoint123",
            server_type="runpod",
            api_key=None,
            endpoint_id="endpoint123",
            is_online=True
        )
        client = ComfyUIClient(server)
        
        result = await client.check_connection()
        
        assert result is False
    
    async def test_get_models_standard(self, standard_server):
        client = ComfyUIClient(standard_server)
        
        mock_object_info = {
            "CheckpointLoaderSimple": {
                "input": {
                    "required": {
                        "ckpt_name": [["model1.safetensors", "model2.ckpt"]]
                    }
                }
            },
            "LoraLoader": {
                "input": {
                    "required": {
                        "lora_name": [["lora1.safetensors", "lora2.safetensors"]]
                    }
                }
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_object_info)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_response
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await client.get_models()
            
            assert "checkpoints" in result
            assert "loras" in result
            assert len(result["checkpoints"]) > 0
            assert len(result["loras"]) > 0
    
    async def test_get_models_runpod(self, runpod_server):
        client = ComfyUIClient(runpod_server)
        
        result = await client.get_models()
        
        assert "checkpoints" in result
        assert "loras" in result
        assert "vaes" in result
        assert len(result["checkpoints"]) > 0
    
    async def test_generate_image_standard(self, standard_server):
        client = ComfyUIClient(standard_server)
        
        mock_prompt_response = AsyncMock()
        mock_prompt_response.status = 200
        mock_prompt_response.json = AsyncMock(return_value={"prompt_id": "prompt-123"})
        mock_prompt_response.__aenter__.return_value = mock_prompt_response
        mock_prompt_response.__aexit__.return_value = None
        
        mock_history_response = AsyncMock()
        mock_history_response.status = 200
        mock_history_response.json = AsyncMock(return_value={
            "prompt-123": {
                "outputs": {
                    "9": {
                        "images": [{"filename": "test.png"}]
                    }
                }
            }
        })
        mock_history_response.__aenter__.return_value = mock_history_response
        mock_history_response.__aexit__.return_value = None
        
        mock_session = AsyncMock()
        mock_session.post.return_value = mock_prompt_response
        mock_session.get.return_value = mock_history_response
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await client.generate_image(
                prompt="test prompt",
                negative_prompt="",
                model="test-model.safetensors"
            )
            
            assert result is not None
            assert "test.png" in result
    
    async def test_generate_image_runpod(self, runpod_server):
        client = ComfyUIClient(runpod_server)
        
        mock_run_response = AsyncMock()
        mock_run_response.status = 200
        mock_run_response.json = AsyncMock(return_value={"id": "job-123"})
        mock_run_response.__aenter__.return_value = mock_run_response
        mock_run_response.__aexit__.return_value = None
        
        mock_stream_response = AsyncMock()
        mock_stream_response.status = 200
        mock_stream_response.json = AsyncMock(return_value={
            "status": "COMPLETED",
            "output": {"image_url": "http://test.com/image.png"}
        })
        mock_stream_response.__aenter__.return_value = mock_stream_response
        mock_stream_response.__aexit__.return_value = None
        
        mock_session = AsyncMock()
        mock_session.post.return_value = mock_run_response
        mock_session.get.return_value = mock_stream_response
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        
        with patch('aiohttp.ClientSession', return_value=mock_session), \
             patch('asyncio.sleep', new_callable=AsyncMock):
            
            result = await client.generate_image(
                prompt="test prompt",
                negative_prompt="",
                model="test-model"
            )
            
            assert result == "http://test.com/image.png"
    
    async def test_generate_video_standard(self, standard_server):
        client = ComfyUIClient(standard_server)
        
        with patch.object(client, '_create_animatediff_workflow', new_callable=AsyncMock) as mock_workflow:
            mock_workflow.return_value = {"test": "workflow"}
            
            mock_prompt_response = AsyncMock()
            mock_prompt_response.status = 200
            mock_prompt_response.json = AsyncMock(return_value={"prompt_id": "prompt-456"})
            mock_prompt_response.__aenter__.return_value = mock_prompt_response
            mock_prompt_response.__aexit__.return_value = None
            
            mock_history_response = AsyncMock()
            mock_history_response.status = 200
            mock_history_response.json = AsyncMock(return_value={
                "prompt-456": {
                    "outputs": {
                        "9": {
                            "videos": [{"filename": "test.mp4"}]
                        }
                    }
                }
            })
            mock_history_response.__aenter__.return_value = mock_history_response
            mock_history_response.__aexit__.return_value = None
            
            mock_session = AsyncMock()
            mock_session.post.return_value = mock_prompt_response
            mock_session.get.return_value = mock_history_response
            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            
            with patch('aiohttp.ClientSession', return_value=mock_session), \
                 patch('asyncio.sleep', new_callable=AsyncMock):
                
                result = await client.generate_video(
                    prompt="test video prompt",
                    negative_prompt="",
                    model="animatediff-model"
                )
                
                assert result is not None
                assert "test.mp4" in result
