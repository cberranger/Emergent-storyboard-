from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from pydantic import ConfigDict
from dtos.comfyui_dtos import (
    ComfyUIServerCreateDTO,
    ComfyUIServerDTO,
    ComfyUIServerInfoDTO,
    ModelDTO,
)
from repositories.comfyui_repository import ComfyUIRepository
from active_models_service import ActiveModelsService
from services.model_config import MODEL_DEFAULTS, detect_model_type
from utils.errors import DuplicateResourceError, ServerNotFoundError

logger = logging.getLogger(__name__)


class ComfyUIClient:
    """Client wrapper for interacting with a ComfyUI server instance."""

    def __init__(self, server: ComfyUIServerDTO):
        self.server = server
        self.base_url = server.url.rstrip("/")

        if "runpod.ai" in self.base_url or server.server_type == "runpod":
            self.server_type = "runpod"
            if "/v2/" in self.base_url:
                self.endpoint_id = self.base_url.split("/v2/")[-1].split("/")[0]
            else:
                self.endpoint_id = server.endpoint_id or "unknown"
        else:
            self.server_type = "standard"
            self.endpoint_id = None

    async def check_connection(self) -> bool:
        try:
            if self.server_type == "runpod":
                return await self._check_runpod_connection()
            return await self._check_standard_connection()
        except Exception as exc:  # pragma: no cover - network errors
            logger.warning("Failed connection check for %s: %s", self.server.id, exc)
            return False

    async def _check_standard_connection(self) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/system_stats", timeout=5
            ) as response:
                return response.status == 200

    async def _check_runpod_connection(self) -> bool:
        if not self.server.api_key:
            logger.warning("No API key configured for RunPod server %s", self.server.id)
            return False

        if not self.endpoint_id:
            logger.error(
                "No endpoint ID configured for RunPod server %s", self.server.id
            )
            return False

        headers = {
            "Authorization": f"Bearer {self.server.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            status_url = f"https://api.runpod.ai/v2/{self.endpoint_id}/status"
            try:
                async with session.get(
                    status_url, headers=headers, timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") in {"RUNNING", "READY", "IDLE"}:
                            return True
                        logger.warning(
                            "RunPod endpoint %s status: %s",
                            self.endpoint_id,
                            data.get("status"),
                        )
                        return False
                    if response.status == 401:
                        logger.error(
                            "Invalid API key for RunPod endpoint %s", self.endpoint_id
                        )
                    elif response.status == 404:
                        logger.error("RunPod endpoint %s not found", self.endpoint_id)
                    return False
            except asyncio.TimeoutError:
                logger.error("Timeout checking RunPod endpoint %s", self.endpoint_id)
                return False
            except aiohttp.ClientError as exc:
                logger.error(
                    "Network error checking RunPod endpoint %s: %s",
                    self.endpoint_id,
                    exc,
                )
                return False

    async def get_models(self) -> Dict[str, List[str]]:
        try:
            if self.server_type == "runpod":
                return await self._get_runpod_models()
            return await self._get_standard_models()
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Error retrieving models: %s", exc)
            return {"checkpoints": [], "loras": [], "vaes": []}

    async def _get_standard_models(self) -> Dict[str, List[str]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/object_info") as response:
                if response.status != 200:
                    return {"checkpoints": [], "loras": [], "vaes": []}

                data = await response.json()
                models: Dict[str, List[str]] = {
                    "checkpoints": [],
                    "loras": [],
                    "vaes": [],
                }

                for node_info in data.values():
                    if "input" not in node_info or "required" not in node_info["input"]:
                        continue

                    required_inputs = node_info["input"]["required"]
                    for input_name, input_info in required_inputs.items():
                        if not isinstance(input_info, list) or not input_info:
                            continue

                        value = input_info[0]
                        if not isinstance(value, list):
                            continue

                        lowered = input_name.lower()
                        if "ckpt_name" in lowered or "checkpoint" in lowered:
                            models["checkpoints"].extend(value)
                        elif "lora" in lowered:
                            models["loras"].extend(value)
                        elif "vae" in lowered:
                            models["vaes"].extend(value)

                return {key: sorted(set(values)) for key, values in models.items()}

    async def _get_runpod_models(self) -> Dict[str, List[str]]:
        return {
            "checkpoints": [
                "sd_xl_base_1.0.safetensors",
                "sd_xl_refiner_1.0.safetensors",
                "v1-5-pruned-emaonly.ckpt",
                "realisticVisionV60B1_v60B1VAE.safetensors",
            ],
            "loras": [
                "lcm-lora-sdxl.safetensors",
                "pytorch_lora_weights.safetensors",
            ],
            "vaes": [
                "sdxl_vae.safetensors",
                "vae-ft-mse-840000-ema-pruned.ckpt",
            ],
        }

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        model: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        loras: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[str]:
        try:
            if self.server_type == "runpod":
                return await self._generate_image_runpod(
                    prompt, negative_prompt, model, params, loras
                )
            return await self._generate_image_standard(
                prompt, negative_prompt, model, params, loras
            )
        except Exception as exc:
            logger.error("Error generating image on %s: %s", self.server.id, exc)
            return None

    async def _generate_image_runpod(
        self,
        prompt: str,
        negative_prompt: str = "",
        model: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        loras: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[str]:
        if not self.server.api_key:
            logger.error("No API key provided for RunPod server %s", self.server.id)
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.server.api_key}",
        }

        runpod_input: Dict[str, Any] = {"prompt": prompt}
        if negative_prompt:
            runpod_input["negative_prompt"] = negative_prompt

        if params:
            runpod_input.update(
                {
                    "width": params.get("width", 512),
                    "height": params.get("height", 512),
                    "steps": params.get("steps", 20),
                    "cfg_scale": params.get("cfg", 8),
                    "seed": params.get("seed", -1),
                }
            )

        request_data = {"input": runpod_input}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.runpod.ai/v2/{self.endpoint_id}/run",
                headers=headers,
                json=request_data,
            ) as response:
                if response.status != 200:
                    return None

                result = await response.json()
                job_id = result.get("id")
                if not job_id:
                    return None

                for _ in range(120):
                    await asyncio.sleep(1)
                    async with session.get(
                        f"https://api.runpod.ai/v2/{self.endpoint_id}/stream/{job_id}",
                        headers=headers,
                    ) as status_response:
                        if status_response.status != 200:
                            continue

                        status_data = await status_response.json()
                        status = status_data.get("status")
                        if status == "COMPLETED":
                            output = status_data.get("output", {})
                            if isinstance(output, dict):
                                image_url = output.get("image_url")
                                if image_url:
                                    return image_url
                                images = output.get("images")
                                if images and isinstance(images, list):
                                    return images[0].get("url")
                            if isinstance(output, str) and output.startswith("http"):
                                return output
                            break
                        if status in {"FAILED", "CANCELLED"}:
                            logger.error(
                                "RunPod generation failed for job %s: %s",
                                job_id,
                                status_data.get("error"),
                            )
                            break
        return None

    async def _generate_image_standard(
        self,
        prompt: str,
        negative_prompt: str = "",
        model: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        loras: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[str]:
        params = params or {}
        loras = loras or []

        if params.get("use_custom_workflow") and params.get("workflow_json"):
            try:
                workflow = json.loads(params["workflow_json"])
                workflow_str = json.dumps(workflow)
                workflow_str = workflow_str.replace("{{PROMPT}}", prompt)
                workflow_str = workflow_str.replace(
                    "{{NEGATIVE_PROMPT}}", negative_prompt
                )
                workflow_str = workflow_str.replace(
                    "{{MODEL}}", model or "v1-5-pruned-emaonly.ckpt"
                )
                workflow = json.loads(workflow_str)
            except Exception as exc:  # pragma: no cover - safe fallback
                logger.warning("Failed to apply custom workflow: %s", exc)

        workflow = {
            "3": {
                "inputs": {
                    "seed": params.get("seed", 42),
                    "steps": params.get("steps", 20),
                    "cfg": params.get("cfg", 8),
                    "sampler_name": params.get("sampler", "euler"),
                    "scheduler": params.get("scheduler", "normal"),
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
                "class_type": "KSampler",
            },
            "4": {
                "inputs": {
                    "ckpt_name": model or "v1-5-pruned-emaonly.ckpt",
                },
                "class_type": "CheckpointLoaderSimple",
            },
            "5": {
                "inputs": {
                    "width": params.get("width", 512),
                    "height": params.get("height", 512),
                    "batch_size": 1,
                },
                "class_type": "EmptyLatentImage",
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1],
                },
                "class_type": "CLIPTextEncode",
            },
            "7": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["4", 1],
                },
                "class_type": "CLIPTextEncode",
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2],
                },
                "class_type": "VAEDecode",
            },
            "9": {
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["8", 0],
                },
                "class_type": "SaveImage",
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/prompt", json={"prompt": workflow}
            ) as response:
                if response.status != 200:
                    return None

                result = await response.json()
                prompt_id = result.get("prompt_id")
                if not prompt_id:
                    return None

                for _ in range(60):
                    await asyncio.sleep(1)
                    async with session.get(
                        f"{self.base_url}/history/{prompt_id}"
                    ) as hist_response:
                        if hist_response.status != 200:
                            continue

                        history = await hist_response.json()
                        if prompt_id not in history:
                            continue

                        outputs = history[prompt_id].get("outputs", {})
                        for output in outputs.values():
                            if "images" in output:
                                image_info = output["images"][0]
                                filename = image_info["filename"]
                                return f"{self.base_url}/view?filename={filename}"
        return None

    async def generate_video(
        self,
        prompt: str,
        negative_prompt: str = "",
        model: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        loras: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[str]:
        try:
            if self.server_type == "runpod":
                return await self._generate_video_runpod(
                    prompt, negative_prompt, model, params, loras
                )
            return await self._generate_video_standard(
                prompt, negative_prompt, model, params, loras
            )
        except Exception as exc:
            logger.error("Error generating video on %s: %s", self.server.id, exc)
            return None

    async def _generate_video_runpod(
        self,
        prompt: str,
        negative_prompt: str = "",
        model: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        loras: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[str]:
        if not self.server.api_key:
            logger.error("No API key provided for RunPod server %s", self.server.id)
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.server.api_key}",
        }

        runpod_input: Dict[str, Any] = {
            "prompt": prompt,
            "generation_type": "video",
        }
        if negative_prompt:
            runpod_input["negative_prompt"] = negative_prompt

        if params:
            runpod_input.update(
                {
                    "width": params.get("width", 768),
                    "height": params.get("height", 768),
                    "frames": params.get("video_frames", 14),
                    "fps": params.get("video_fps", 24),
                    "steps": params.get("steps", 20),
                    "cfg_scale": params.get("cfg", 7),
                    "seed": params.get("seed", -1),
                    "motion_bucket_id": params.get("motion_bucket_id", 127),
                }
            )

        request_data = {"input": runpod_input}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.runpod.ai/v2/{self.endpoint_id}/run",
                headers=headers,
                json=request_data,
            ) as response:
                if response.status != 200:
                    return None

                result = await response.json()
                job_id = result.get("id")
                if not job_id:
                    return None

                for _ in range(300):
                    await asyncio.sleep(2)
                    async with session.get(
                        f"https://api.runpod.ai/v2/{self.endpoint_id}/stream/{job_id}",
                        headers=headers,
                    ) as status_response:
                        if status_response.status != 200:
                            continue

                        status_data = await status_response.json()
                        status = status_data.get("status")
                        if status == "COMPLETED":
                            output = status_data.get("output", {})
                            if isinstance(output, dict):
                                video_url = output.get("video_url")
                                if video_url:
                                    return video_url
                                videos = output.get("videos")
                                if videos and isinstance(videos, list):
                                    return videos[0].get("url")
                            if isinstance(output, str) and output.startswith("http"):
                                return output
                            break
                        if status in {"FAILED", "CANCELLED"}:
                            logger.error(
                                "RunPod video generation failed: %s",
                                status_data.get("error"),
                            )
                            break
        return None

    async def _generate_video_standard(
        self,
        prompt: str,
        negative_prompt: str = "",
        model: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        loras: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[str]:
        params = params or {}
        loras = loras or []

        model_type = detect_model_type(model or "")
        if "wan" in (model_type or ""):
            workflow = await self._create_wan_video_workflow(
                prompt, negative_prompt, model, params, loras
            )
        elif model and ("svd" in model.lower() or "stable_video" in model.lower()):
            workflow = await self._create_svd_workflow(
                prompt, negative_prompt, model, params, loras
            )
        else:
            workflow = await self._create_animatediff_workflow(
                prompt, negative_prompt, model, params, loras
            )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/prompt", json={"prompt": workflow}
            ) as response:
                if response.status != 200:
                    return None

                result = await response.json()
                prompt_id = result.get("prompt_id")
                if not prompt_id:
                    return None

                for _ in range(300):
                    await asyncio.sleep(2)
                    async with session.get(
                        f"{self.base_url}/history/{prompt_id}"
                    ) as hist_response:
                        if hist_response.status != 200:
                            continue

                        history = await hist_response.json()
                        if prompt_id not in history:
                            continue

                        outputs = history[prompt_id].get("outputs", {})
                        for output in outputs.values():
                            if "gifs" in output or "videos" in output:
                                media = output.get("gifs") or output.get("videos") or []
                                if media:
                                    filename = media[0].get("filename")
                                    if filename:
                                        return (
                                            f"{self.base_url}/view?filename={filename}"
                                        )
        return None

    async def _create_wan_video_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        model: Optional[str],
        params: Dict[str, Any],
        loras: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "1": {
                "inputs": {
                    "ckpt_name": model
                    or "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
            },
            "2": {
                "inputs": {"text": prompt, "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {"text": negative_prompt or "", "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "4": {
                "inputs": {
                    "width": params.get("width", 768),
                    "height": params.get("height", 768),
                    "length": params.get("video_frames", 14),
                    "batch_size": 1,
                },
                "class_type": "EmptyLatentVideo",
            },
            "5": {
                "inputs": {
                    "seed": params.get("seed", 42),
                    "steps": params.get("steps", 20),
                    "cfg": params.get("cfg", 7.5),
                    "sampler_name": params.get("sampler", "euler"),
                    "scheduler": params.get("scheduler", "simple"),
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0],
                },
                "class_type": "KSampler",
            },
            "6": {
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
                "class_type": "VAEDecode",
            },
            "7": {
                "inputs": {
                    "filename_prefix": "video",
                    "fps": params.get("video_fps", 24),
                    "images": ["6", 0],
                },
                "class_type": "SaveAnimatedWEBP",
            },
        }

    async def _create_svd_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        model: Optional[str],
        params: Dict[str, Any],
        loras: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "1": {
                "inputs": {"ckpt_name": model or "svd_xt_1_1.safetensors"},
                "class_type": "CheckpointLoaderSimple",
            },
            "2": {
                "inputs": {
                    "width": params.get("width", 1024),
                    "height": params.get("height", 576),
                    "batch_size": 1,
                },
                "class_type": "EmptyLatentImage",
            },
            "3": {
                "inputs": {"text": prompt, "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "4": {
                "inputs": {
                    "seed": params.get("seed", 42),
                    "steps": params.get("steps", 25),
                    "cfg": params.get("cfg", 2.5),
                    "sampler_name": "euler",
                    "scheduler": "karras",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["3", 0],
                    "negative": ["3", 0],
                    "latent_image": ["2", 0],
                },
                "class_type": "KSampler",
            },
            "5": {
                "inputs": {"samples": ["4", 0], "vae": ["1", 2]},
                "class_type": "VAEDecode",
            },
            "6": {
                "inputs": {
                    "filename_prefix": "svd_video",
                    "fps": params.get("video_fps", 6),
                    "images": ["5", 0],
                },
                "class_type": "SaveAnimatedWEBP",
            },
        }

    async def _create_animatediff_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        model: Optional[str],
        params: Dict[str, Any],
        loras: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "1": {
                "inputs": {"ckpt_name": model or "v1-5-pruned-emaonly.ckpt"},
                "class_type": "CheckpointLoaderSimple",
            },
            "2": {
                "inputs": {"text": prompt, "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {
                    "text": negative_prompt or "low quality, blurry",
                    "clip": ["1", 1],
                },
                "class_type": "CLIPTextEncode",
            },
            "4": {
                "inputs": {
                    "width": params.get("width", 512),
                    "height": params.get("height", 512),
                    "length": params.get("video_frames", 16),
                    "batch_size": 1,
                },
                "class_type": "EmptyLatentVideo",
            },
            "5": {
                "inputs": {
                    "seed": params.get("seed", 42),
                    "steps": params.get("steps", 20),
                    "cfg": params.get("cfg", 7.5),
                    "sampler_name": params.get("sampler", "euler_a"),
                    "scheduler": params.get("scheduler", "normal"),
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0],
                },
                "class_type": "KSampler",
            },
            "6": {
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
                "class_type": "VAEDecode",
            },
            "7": {
                "inputs": {
                    "filename_prefix": "animatediff",
                    "fps": params.get("video_fps", 8),
                    "images": ["6", 0],
                },
                "class_type": "SaveAnimatedWEBP",
            },
        }


class ComfyUIService:
    """Service layer encapsulating ComfyUI server operations."""

    def __init__(
        self,
        repository: ComfyUIRepository,
        active_models_service: Optional[ActiveModelsService] = None,
    ):
        self._repository = repository
        self._active_models_service = active_models_service

    @staticmethod
    def _normalize_server_url(url: Optional[str]) -> str:
        return (url or "").rstrip("/")

    @staticmethod
    def _apply_runpod_settings(server_dict: Dict[str, Any]) -> Dict[str, Any]:
        url = server_dict.get("url", "")
        if "runpod.ai" in url:
            server_dict["server_type"] = "runpod"
            if "/v2/" in url:
                server_dict["endpoint_id"] = url.split("/v2/")[-1].split("/")[0]
        else:
            server_dict["server_type"] = "standard"
            server_dict.pop("endpoint_id", None)
        return server_dict

    async def create_server(self, payload: ComfyUIServerCreateDTO) -> ComfyUIServerDTO:
        server_dict = payload.model_dump()
        server_dict["url"] = self._normalize_server_url(str(server_dict.get("url", "")))

        existing = await self._repository.find_by_url(server_dict["url"])
        if existing:
            raise DuplicateResourceError("ComfyUI Server", server_dict["url"])

        server_dict = self._apply_runpod_settings(server_dict)
        server = ComfyUIServerDTO(**server_dict)
        await self._repository.create(server.model_dump())
        return server

    async def register_server(
        self, payload: ComfyUIServerCreateDTO
    ) -> ComfyUIServerDTO:
        return await self.create_server(payload)

    async def list_servers(self) -> List[ComfyUIServerDTO]:
        raw_servers = await self._repository.find_many({})
        return [ComfyUIServerDTO(**server) for server in raw_servers]

    async def update_server(
        self, server_id: str, payload: ComfyUIServerCreateDTO
    ) -> ComfyUIServerDTO:
        existing = await self._repository.find_by_id(server_id)
        if not existing:
            raise ServerNotFoundError(server_id)

        updates = payload.model_dump()
        if "url" in updates:
            updates["url"] = self._normalize_server_url(str(updates["url"]))

        existing_url = self._normalize_server_url(existing.get("url"))
        incoming_url = (
            self._normalize_server_url(updates.get("url")) if updates.get("url") else ""
        )

        if incoming_url and incoming_url != existing_url:
            duplicate = await self._repository.find_by_url(incoming_url)
            if duplicate and duplicate.get("id") != server_id:
                raise DuplicateResourceError("ComfyUI Server", incoming_url)

        updates = self._apply_runpod_settings(updates)
        updated = await self._repository.update_by_id(server_id, updates)
        if not updated:
            raise ServerNotFoundError(server_id)
        return ComfyUIServerDTO(**updated)

    async def delete_server(self, server_id: str) -> None:
        deleted = await self._repository.delete_by_id(server_id)
        if not deleted:
            raise ServerNotFoundError(server_id)

    async def get_server(self, server_id: str) -> Optional[ComfyUIServerDTO]:
        data = await self._repository.find_by_id(server_id)
        return ComfyUIServerDTO(**data) if data else None

    async def get_server_info(self, server_id: str) -> Optional[ComfyUIServerInfoDTO]:
        server_data = await self._repository.find_by_id(server_id)
        if not server_data:
            return None

        server = ComfyUIServerDTO(**server_data)
        client = ComfyUIClient(server)

        is_online = await client.check_connection()
        if not is_online:
            return ComfyUIServerInfoDTO(
                server=server, models=[], loras=[], is_online=False
            )

        models_data = await client.get_models()
        models = [
            ModelDTO(name=name, type="checkpoint")
            for name in models_data.get("checkpoints", [])
        ]
        loras = [
            ModelDTO(name=name, type="lora") for name in models_data.get("loras", [])
        ]

        # Store models in active_backend_models collection if service is available
        if self._active_models_service:
            try:
                # Prepare models data for storage
                all_models = []

                # Add checkpoints
                for model_name in models_data.get("checkpoints", []):
                    all_models.append(
                        {
                            "id": model_name,  # Use model name as ID
                            "name": model_name,
                            "path": f"checkpoints/{model_name}",  # Default path
                            "type": "checkpoint",
                        }
                    )

                # Add LoRAs
                for model_name in models_data.get("loras", []):
                    all_models.append(
                        {
                            "id": model_name,
                            "name": model_name,
                            "path": f"loras/{model_name}",  # Default path
                            "type": "lora",
                        }
                    )

                # Add VAEs
                for model_name in models_data.get("vaes", []):
                    all_models.append(
                        {
                            "id": model_name,
                            "name": model_name,
                            "path": f"vae/{model_name}",  # Default path
                            "type": "vae",
                        }
                    )

                # Update the active models database
                await self._active_models_service.update_backend_models(
                    backend_id=server.id,
                    backend_name=server.name,
                    backend_url=server.url,
                    models_data=all_models,
                )

                logger.info(
                    f"Stored {len(all_models)} models from backend {server.name}"
                )

            except Exception as e:
                logger.error(f"Failed to store models from backend {server.name}: {e}")
                # Continue without failing the request

        return ComfyUIServerInfoDTO(
            server=server, models=models, loras=loras, is_online=True
        )

    async def get_supported_models(self) -> Dict[str, Dict[str, List[str]]]:
        result: Dict[str, Dict[str, List[str]]] = {}
        for model_type, config in MODEL_DEFAULTS.items():
            result[model_type] = {
                "presets": [
                    preset
                    for preset, preset_config in config.items()
                    if isinstance(preset_config, dict)
                ],
                "display_name": model_type.replace("_", " ").title(),
            }
        return {"supported_models": result}

    async def get_server_workflows(
        self, server_id: str
    ) -> Optional[Dict[str, List[str]]]:
        server_data = await self._repository.find_by_id(server_id)
        if not server_data:
            return None

        server = ComfyUIServerDTO(**server_data)
        if server.server_type != "standard":
            return {"workflows": []}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{server.url}/workflows") as response:
                    if response.status == 200:
                        workflows = await response.json()
                        return {"workflows": workflows}
            except Exception as exc:  # pragma: no cover - network errors
                logger.warning("Failed fetching workflows for %s: %s", server_id, exc)

        return {"workflows": []}
