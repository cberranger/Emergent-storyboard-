"""OpenAI Sora Video API wrapper service."""
import os
import asyncio
import logging
import math
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from openai import AsyncOpenAI, OpenAI  # type: ignore
except Exception:  # pragma: no cover - allow module import even if dependency not yet installed
    AsyncOpenAI = None  # type: ignore
    OpenAI = None  # type: ignore

from config import config as app_config
from utils.errors import ServiceUnavailableError, GenerationError

logger = logging.getLogger(__name__)


class OpenAIVideoService:
    """Encapsulates OpenAI Video (Sora) API operations and local persistence."""
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.getenv("OPENAI_API_KEY") or getattr(app_config, "OPENAI_API_KEY", "") or ""
        self._api_key: str = key
        self._async_client = AsyncOpenAI(api_key=key) if (AsyncOpenAI and key) else None
        self._sync_client = OpenAI(api_key=key) if (OpenAI and key) else None

    def refresh_api_key(self, api_key: Optional[str] = None) -> None:
        """Refresh client instances when the API key changes."""
        key = api_key or os.getenv("OPENAI_API_KEY") or getattr(app_config, "OPENAI_API_KEY", "") or ""
        if key != getattr(self, "_api_key", ""):
            self._api_key = key
            self._async_client = AsyncOpenAI(api_key=key) if (AsyncOpenAI and key) else None
            self._sync_client = OpenAI(api_key=key) if (OpenAI and key) else None

    def _ensure_client(self) -> None:
        if not self._async_client:
            raise ServiceUnavailableError("OpenAI", "OPENAI_API_KEY not configured")

    @staticmethod
    def _build_create_args(model: str, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map internal params to OpenAI Videos.create arguments."""
        args: Dict[str, Any] = {"model": model, "prompt": prompt}

        # Resolution (OpenAI expects "size" as WIDTHxHEIGHT)
        width = params.get("width")
        height = params.get("height")
        if width and height:
            try:
                args["size"] = f"{int(width)}x{int(height)}"
            except Exception:
                pass

        # Duration (OpenAI accepts "seconds")
        frames = params.get("video_frames")
        fps = params.get("video_fps")
        if frames and fps:
            try:
                seconds = max(1, int(math.ceil(float(frames) / float(fps))))
                args["seconds"] = seconds
            except Exception:
                pass

        # Input reference image (first frame) - support path or URL under /uploads
        ref_path: Optional[str] = params.get("input_reference_path")
        ref_url: Optional[str] = params.get("input_reference_url")

        # If only URL is provided, resolve to local path under ./uploads/...
        if not ref_path and ref_url:
            try:
                if "/uploads/" in ref_url:
                    tail = ref_url.split("/uploads/")[-1]
                    candidate = Path("uploads") / Path(tail)
                    if candidate.exists():
                        ref_path = str(candidate)
                elif ref_url.startswith("/uploads/"):
                    candidate = Path(ref_url.lstrip("/"))
                    if candidate.exists():
                        ref_path = str(candidate)
            except Exception:
                # Non-fatal - continue without input_reference
                pass

        if ref_path:
            try:
                # Do not close the handle early; the SDK reads it during the call
                f = open(ref_path, "rb")
                args["input_reference"] = f  # SDK should treat this as a file-like field
            except Exception as exc:
                logger.warning("OpenAI input_reference unavailable (%s). Proceeding without.", exc)

        return args

    async def create(self, model: str, prompt: str, params: Optional[Dict[str, Any]] = None) -> Any:
        self._ensure_client()
        args = self._build_create_args(model, prompt, params or {})
        return await self._async_client.videos.create(**args)  # type: ignore

    async def create_and_poll(self, model: str, prompt: str, params: Optional[Dict[str, Any]] = None) -> Any:
        self._ensure_client()
        args = self._build_create_args(model, prompt, params or {})
        return await self._async_client.videos.create_and_poll(**args)  # type: ignore

    async def retrieve(self, video_id: str) -> Any:
        self._ensure_client()
        return await self._async_client.videos.retrieve(video_id)  # type: ignore

    async def list(self, **kwargs: Any) -> Any:
        self._ensure_client()
        return await self._async_client.videos.list(**kwargs)  # type: ignore

    async def remix(self, video_id: str, **params: Any) -> Any:
        self._ensure_client()
        return await self._async_client.videos.remix(video_id, **params)  # type: ignore

    async def delete(self, video_id: str) -> Any:
        self._ensure_client()
        return await self._async_client.videos.delete(video_id)  # type: ignore

    async def download_content(self, video_id: str, variant: Optional[str] = "video") -> Any:
        """Return OpenAI SDK content object for the given video ID."""
        self._ensure_client()
        try:
            if variant is None:
                return await self._async_client.videos.download_content(video_id)  # type: ignore
            return await self._async_client.videos.download_content(video_id, variant=variant)  # type: ignore
        except Exception:
            # Fallback to sync client (can happen if async variant not available in SDK)
            if not self._sync_client:
                raise
            if variant is None:
                return self._sync_client.videos.download_content(video_id)  # type: ignore
            return self._sync_client.videos.download_content(video_id, variant=variant)  # type: ignore

    async def generate_video_to_local(self, model: str, prompt: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a video job, wait for completion, download MP4 to uploads/openai/videos, and return local URL.
        """
        self.refresh_api_key()
        video = await self.create_and_poll(model=model, prompt=prompt, params=params or {})

        status = getattr(video, "status", None)
        if not status and isinstance(video, dict):
            status = video.get("status")

        if status != "completed":
            raise GenerationError("video", f"OpenAI video job status: {status}")

        video_id = getattr(video, "id", None)
        if not video_id and isinstance(video, dict):
            video_id = video.get("id")
        if not video_id:
            raise GenerationError("video", "OpenAI returned no video id")

        # Ensure directory
        dest_dir = Path("uploads") / "openai" / "videos"
        dest_dir.mkdir(parents=True, exist_ok=True)
        out_path = dest_dir / f"{video_id}.mp4"

        # Download and write file
        content = await self.download_content(video_id, variant="video")
        write_method = getattr(content, "write_to_file", None)
        if write_method:
            await asyncio.to_thread(write_method, str(out_path))
        else:
            # Try other common patterns
            array_buffer = getattr(content, "array_buffer", None) or getattr(content, "arrayBuffer", None)
            if array_buffer:
                data = await array_buffer()
                buffer_bytes = bytes(data) if not isinstance(data, (bytes, bytearray)) else data
                await asyncio.to_thread(out_path.write_bytes, buffer_bytes)
            else:
                get_bytes = getattr(content, "get_bytes", None)
                if get_bytes:
                    data = await get_bytes()
                    await asyncio.to_thread(out_path.write_bytes, data)
                else:
                    # Fallback best-effort - treat as bytes-like
                    await asyncio.to_thread(out_path.write_bytes, content)  # type: ignore

        return f"/uploads/openai/videos/{video_id}.mp4"


# Global singleton
openai_video_service = OpenAIVideoService()