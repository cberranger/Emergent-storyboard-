from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional

from services.openai_video_service import openai_video_service

router = APIRouter(prefix="/openai", tags=["openai"])


def _serialize(obj: Any) -> Any:
    if obj is None:
        return None
    try:
        md = getattr(obj, "model_dump", None)
        if callable(md):
            return md()
        to_dict = getattr(obj, "to_dict", None)
        if callable(to_dict):
            return to_dict()
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, (list, tuple)):
            return [_serialize(x) for x in obj]
        if hasattr(obj, "__dict__"):
            try:
                return dict(obj.__dict__)
            except Exception:
                pass
        return obj
    except Exception:
        return str(obj)


@router.get("/videos/{video_id}", response_model=None)
async def get_video(video_id: str) -> Any:
    try:
        video = await openai_video_service.retrieve(video_id)
        return _serialize(video)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI retrieve error: {str(e)}")


@router.get("/videos", response_model=None)
async def list_videos(
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    after: Optional[str] = None,
    order: Optional[str] = Query(default=None),
) -> Any:
    try:
        kwargs: Dict[str, Any] = {}
        if limit is not None:
            kwargs["limit"] = limit
        if after:
            kwargs["after"] = after
        if order in ("asc", "desc"):
            kwargs["order"] = order
        page = await openai_video_service.list(**kwargs)
        return _serialize(page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI list error: {str(e)}")


@router.delete("/videos/{video_id}", response_model=None)
async def delete_video(video_id: str) -> Any:
    try:
        result = await openai_video_service.delete(video_id)
        return _serialize(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI delete error: {str(e)}")