"""FaceFusion integration router for API v1."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import aiohttp
import logging

from .dependencies import get_database
from dtos.character_dtos import (
    FaceFusionProcessingHistoryEntry,
    FaceFusionPreferredSettings,
    FaceFusionOutputGallery,
)
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/facefusion", tags=["facefusion"])


class FaceEnhanceRequest(BaseModel):
    character_id: Optional[str] = None
    image_url: str
    enhancement_model: str = Field(default="gfpgan_1.4")
    face_enhancer_blend: float = Field(default=1.0, ge=0.0, le=1.0)
    facefusion_url: str = Field(default="http://localhost:7870")


class FaceAgeAdjustRequest(BaseModel):
    character_id: Optional[str] = None
    image_url: str
    target_age: int = Field(..., ge=0, le=100)
    face_editor_blend: float = Field(default=1.0, ge=0.0, le=1.0)
    facefusion_url: str = Field(default="http://localhost:7870")


class FaceSwapRequest(BaseModel):
    character_id: Optional[str] = None
    source_face_url: str
    target_image_url: str
    face_swapper_model: str = Field(default="inswapper_128")
    facefusion_url: str = Field(default="http://localhost:7870")


class FaceMaskRequest(BaseModel):
    character_id: Optional[str] = None
    image_url: str
    mask_types: List[str] = Field(default=["box"])
    face_selector_mode: str = Field(default="one")
    facefusion_url: str = Field(default="http://localhost:7870")


class FaceDetectionRequest(BaseModel):
    image_url: str
    face_detector_model: str = Field(default="yoloface")
    face_detector_size: str = Field(default="640x640")
    facefusion_url: str = Field(default="http://localhost:7870")


class FaceEditRequest(BaseModel):
    character_id: Optional[str] = None
    image_url: str
    eyebrow_direction: Optional[int] = Field(default=None, ge=-100, le=100)
    eye_gaze_horizontal: Optional[int] = Field(default=None, ge=-100, le=100)
    eye_gaze_vertical: Optional[int] = Field(default=None, ge=-100, le=100)
    eye_open_ratio: Optional[int] = Field(default=None, ge=-100, le=100)
    lip_open_ratio: Optional[int] = Field(default=None, ge=-100, le=100)
    mouth_grim: Optional[int] = Field(default=None, ge=-100, le=100)
    mouth_pout: Optional[int] = Field(default=None, ge=-100, le=100)
    mouth_purse: Optional[int] = Field(default=None, ge=-100, le=100)
    mouth_smile: Optional[int] = Field(default=None, ge=-100, le=100)
    mouth_position_horizontal: Optional[int] = Field(default=None, ge=-100, le=100)
    mouth_position_vertical: Optional[int] = Field(default=None, ge=-100, le=100)
    head_pitch: Optional[int] = Field(default=None, ge=-100, le=100)
    head_yaw: Optional[int] = Field(default=None, ge=-100, le=100)
    head_roll: Optional[int] = Field(default=None, ge=-100, le=100)
    facefusion_url: str = Field(default="http://localhost:7870")


class VideoProcessRequest(BaseModel):
    character_id: Optional[str] = None
    video_url: str
    operation_type: str = Field(..., description="enhance, age_adjust, swap, edit")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    facefusion_url: str = Field(default="http://localhost:7870")


class BatchOperation(BaseModel):
    operation_type: str = Field(..., description="enhance, age_adjust, swap, edit, mask, detect")
    image_url: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class BatchProcessRequest(BaseModel):
    character_id: Optional[str] = None
    operations: List[BatchOperation]
    facefusion_url: str = Field(default="http://localhost:7870")


async def call_facefusion_api(
    endpoint: str,
    facefusion_url: str,
    method: str = "POST",
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{facefusion_url.rstrip('/')}/api/v1/{endpoint}"
            async with session.request(method, url, json=json_data, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"FaceFusion API error: {error_text}"
                    )
    except aiohttp.ClientError as e:
        logger.error(f"FaceFusion connection error: {e}")
        raise HTTPException(status_code=503, detail=f"FaceFusion server unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected FaceFusion error: {e}")
        raise HTTPException(status_code=500, detail=f"FaceFusion processing error: {str(e)}")


async def add_to_character_history(
    db,
    character_id: str,
    operation_type: str,
    input_url: str,
    output_url: str,
    parameters: Dict[str, Any],
    success: bool,
    error_message: Optional[str] = None,
    processing_time: Optional[float] = None
):
    history_entry = FaceFusionProcessingHistoryEntry(
        operation_type=operation_type,
        input_image_url=input_url,
        output_image_url=output_url,
        parameters=parameters,
        success=success,
        error_message=error_message,
        processing_time_seconds=processing_time,
    )
    
    await db.characters.update_one(
        {"id": character_id},
        {
            "$push": {"facefusion_processing_history": history_entry.dict()},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )


async def update_character_gallery(
    db,
    character_id: str,
    gallery_type: str,
    image_url: str,
    metadata: Optional[Dict[str, Any]] = None
):
    update_field = f"facefusion_output_gallery.{gallery_type}"
    
    if gallery_type == "age_variants" and metadata and "age" in metadata:
        await db.characters.update_one(
            {"id": character_id},
            {
                "$set": {
                    f"{update_field}.{metadata['age']}": image_url,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
    else:
        await db.characters.update_one(
            {"id": character_id},
            {
                "$push": {update_field: image_url},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )


@router.get("/status")
async def check_facefusion_status(facefusion_url: str = "http://localhost:7870"):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{facefusion_url.rstrip('/')}/api/v1/status",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                is_online = response.status == 200
                return {
                    "online": is_online,
                    "url": facefusion_url,
                    "status_code": response.status
                }
    except Exception as e:
        return {
            "online": False,
            "url": facefusion_url,
            "error": str(e)
        }


@router.post("/enhance-face")
async def enhance_face(
    request: FaceEnhanceRequest,
    db = Depends(get_database)
):
    start_time = datetime.now(timezone.utc)
    
    try:
        result = await call_facefusion_api(
            "enhance-face",
            request.facefusion_url,
            json_data={
                "source_path": request.image_url,
                "face_enhancer_model": request.enhancement_model,
                "face_enhancer_blend": request.face_enhancer_blend
            }
        )
        
        output_url = result.get("output_path")
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        if request.character_id:
            await add_to_character_history(
                db, request.character_id, "enhance", request.image_url, output_url,
                {"model": request.enhancement_model, "blend": request.face_enhancer_blend},
                True, None, processing_time
            )
            await update_character_gallery(db, request.character_id, "enhanced_faces", output_url)
        
        return {
            "success": True,
            "output_url": output_url,
            "processing_time_seconds": processing_time
        }
    except Exception as e:
        if request.character_id:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await add_to_character_history(
                db, request.character_id, "enhance", request.image_url, "",
                {"model": request.enhancement_model}, False, str(e), processing_time
            )
        raise


@router.post("/adjust-face-age")
async def adjust_face_age(
    request: FaceAgeAdjustRequest,
    db = Depends(get_database)
):
    start_time = datetime.now(timezone.utc)
    
    try:
        result = await call_facefusion_api(
            "adjust-face",
            request.facefusion_url,
            json_data={
                "source_path": request.image_url,
                "face_editor_age": request.target_age,
                "face_editor_blend": request.face_editor_blend
            }
        )
        
        output_url = result.get("output_path")
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        if request.character_id:
            await add_to_character_history(
                db, request.character_id, "age_adjust", request.image_url, output_url,
                {"target_age": request.target_age, "blend": request.face_editor_blend},
                True, None, processing_time
            )
            await update_character_gallery(
                db, request.character_id, "age_variants", output_url,
                {"age": request.target_age}
            )
        
        return {
            "success": True,
            "output_url": output_url,
            "target_age": request.target_age,
            "processing_time_seconds": processing_time
        }
    except Exception as e:
        if request.character_id:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await add_to_character_history(
                db, request.character_id, "age_adjust", request.image_url, "",
                {"target_age": request.target_age}, False, str(e), processing_time
            )
        raise


@router.post("/swap-face")
async def swap_face(
    request: FaceSwapRequest,
    db = Depends(get_database)
):
    start_time = datetime.now(timezone.utc)
    
    try:
        result = await call_facefusion_api(
            "swap-face",
            request.facefusion_url,
            json_data={
                "source_face_path": request.source_face_url,
                "target_image_path": request.target_image_url,
                "face_swapper_model": request.face_swapper_model
            }
        )
        
        output_url = result.get("output_path")
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        if request.character_id:
            await add_to_character_history(
                db, request.character_id, "swap", request.source_face_url, output_url,
                {"target": request.target_image_url, "model": request.face_swapper_model},
                True, None, processing_time
            )
            await update_character_gallery(db, request.character_id, "swapped_faces", output_url)
        
        return {
            "success": True,
            "output_url": output_url,
            "processing_time_seconds": processing_time
        }
    except Exception as e:
        if request.character_id:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await add_to_character_history(
                db, request.character_id, "swap", request.source_face_url, "",
                {"target": request.target_image_url}, False, str(e), processing_time
            )
        raise


@router.post("/mask-face")
async def mask_face(
    request: FaceMaskRequest,
    db = Depends(get_database)
):
    start_time = datetime.now(timezone.utc)
    
    try:
        result = await call_facefusion_api(
            "mask-face",
            request.facefusion_url,
            json_data={
                "source_path": request.image_url,
                "face_mask_types": request.mask_types,
                "face_selector_mode": request.face_selector_mode
            }
        )
        
        output_url = result.get("output_path")
        faces_detected = result.get("faces_detected", 0)
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        if request.character_id:
            await add_to_character_history(
                db, request.character_id, "mask", request.image_url, output_url,
                {"mask_types": request.mask_types, "selector_mode": request.face_selector_mode},
                True, None, processing_time
            )
        
        return {
            "success": True,
            "output_url": output_url,
            "faces_detected": faces_detected,
            "mask_types": request.mask_types,
            "processing_time_seconds": processing_time
        }
    except Exception as e:
        if request.character_id:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await add_to_character_history(
                db, request.character_id, "mask", request.image_url, "",
                {"mask_types": request.mask_types}, False, str(e), processing_time
            )
        raise


@router.post("/detect-faces")
async def detect_faces(request: FaceDetectionRequest):
    try:
        result = await call_facefusion_api(
            "detect-faces",
            request.facefusion_url,
            json_data={
                "source_path": request.image_url,
                "face_detector_model": request.face_detector_model,
                "face_detector_size": request.face_detector_size
            }
        )
        
        return {
            "success": True,
            "faces": result.get("faces", []),
            "total_faces": result.get("total_faces", 0),
            "detector_model": request.face_detector_model
        }
    except Exception as e:
        raise


@router.post("/edit-face")
async def edit_face(
    request: FaceEditRequest,
    db = Depends(get_database)
):
    start_time = datetime.now(timezone.utc)
    
    editor_params = {}
    if request.eyebrow_direction is not None:
        editor_params["face_editor_eyebrow_direction"] = request.eyebrow_direction
    if request.eye_gaze_horizontal is not None:
        editor_params["face_editor_eye_gaze_horizontal"] = request.eye_gaze_horizontal
    if request.eye_gaze_vertical is not None:
        editor_params["face_editor_eye_gaze_vertical"] = request.eye_gaze_vertical
    if request.eye_open_ratio is not None:
        editor_params["face_editor_eye_open_ratio"] = request.eye_open_ratio
    if request.lip_open_ratio is not None:
        editor_params["face_editor_lip_open_ratio"] = request.lip_open_ratio
    if request.mouth_grim is not None:
        editor_params["face_editor_mouth_grim"] = request.mouth_grim
    if request.mouth_pout is not None:
        editor_params["face_editor_mouth_pout"] = request.mouth_pout
    if request.mouth_purse is not None:
        editor_params["face_editor_mouth_purse"] = request.mouth_purse
    if request.mouth_smile is not None:
        editor_params["face_editor_mouth_smile"] = request.mouth_smile
    if request.mouth_position_horizontal is not None:
        editor_params["face_editor_mouth_position_horizontal"] = request.mouth_position_horizontal
    if request.mouth_position_vertical is not None:
        editor_params["face_editor_mouth_position_vertical"] = request.mouth_position_vertical
    if request.head_pitch is not None:
        editor_params["face_editor_head_pitch"] = request.head_pitch
    if request.head_yaw is not None:
        editor_params["face_editor_head_yaw"] = request.head_yaw
    if request.head_roll is not None:
        editor_params["face_editor_head_roll"] = request.head_roll
    
    try:
        api_data = {"source_path": request.image_url}
        api_data.update(editor_params)
        
        result = await call_facefusion_api(
            "edit-face",
            request.facefusion_url,
            json_data=api_data
        )
        
        output_url = result.get("output_path")
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        if request.character_id:
            await add_to_character_history(
                db, request.character_id, "edit", request.image_url, output_url,
                editor_params, True, None, processing_time
            )
            await update_character_gallery(db, request.character_id, "edited_expressions", output_url)
        
        return {
            "success": True,
            "output_url": output_url,
            "parameters": editor_params,
            "processing_time_seconds": processing_time
        }
    except Exception as e:
        if request.character_id:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await add_to_character_history(
                db, request.character_id, "edit", request.image_url, "",
                editor_params, False, str(e), processing_time
            )
        raise


@router.post("/process-video")
async def process_video(
    request: VideoProcessRequest,
    db = Depends(get_database)
):
    start_time = datetime.now(timezone.utc)
    
    try:
        api_data = {
            "source_path": request.video_url,
            "operation_type": request.operation_type
        }
        api_data.update(request.parameters)
        
        result = await call_facefusion_api(
            "process-video",
            request.facefusion_url,
            json_data=api_data
        )
        
        output_url = result.get("output_path")
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        if request.character_id:
            await add_to_character_history(
                db, request.character_id, f"video_{request.operation_type}",
                request.video_url, output_url, request.parameters,
                True, None, processing_time
            )
        
        return {
            "success": True,
            "output_url": output_url,
            "operation_type": request.operation_type,
            "processing_time_seconds": processing_time
        }
    except Exception as e:
        if request.character_id:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await add_to_character_history(
                db, request.character_id, f"video_{request.operation_type}",
                request.video_url, "", request.parameters, False, str(e), processing_time
            )
        raise


@router.post("/batch-process")
async def batch_process(
    request: BatchProcessRequest,
    db = Depends(get_database)
):
    job_id = str(uuid.uuid4())
    results = []
    
    job_data = {
        "id": job_id,
        "character_id": request.character_id,
        "status": "processing",
        "total_operations": len(request.operations),
        "completed_operations": 0,
        "failed_operations": 0,
        "results": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.facefusion_jobs.insert_one(job_data)
    
    for idx, operation in enumerate(request.operations):
        try:
            api_data = {"source_path": operation.image_url}
            api_data.update(operation.parameters)
            
            result = await call_facefusion_api(
                operation.operation_type,
                request.facefusion_url,
                json_data=api_data
            )
            
            output_url = result.get("output_path")
            results.append({
                "operation_index": idx,
                "operation_type": operation.operation_type,
                "input_url": operation.image_url,
                "output_url": output_url,
                "success": True
            })
            
            await db.facefusion_jobs.update_one(
                {"id": job_id},
                {
                    "$inc": {"completed_operations": 1},
                    "$push": {"results": results[-1]},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            
        except Exception as e:
            logger.error(f"Batch operation {idx} failed: {e}")
            results.append({
                "operation_index": idx,
                "operation_type": operation.operation_type,
                "input_url": operation.image_url,
                "success": False,
                "error": str(e)
            })
            
            await db.facefusion_jobs.update_one(
                {"id": job_id},
                {
                    "$inc": {"failed_operations": 1},
                    "$push": {"results": results[-1]},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
    
    await db.facefusion_jobs.update_one(
        {"id": job_id},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    return {
        "job_id": job_id,
        "total_operations": len(request.operations),
        "completed_operations": sum(1 for r in results if r.get("success")),
        "failed_operations": sum(1 for r in results if not r.get("success")),
        "results": results
    }


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    db = Depends(get_database)
):
    job = await db.facefusion_jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.pop("_id", None)
    return job


@router.get("/jobs")
async def list_jobs(
    character_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db = Depends(get_database)
):
    query = {}
    if character_id:
        query["character_id"] = character_id
    if status:
        query["status"] = status
    
    jobs = await db.facefusion_jobs.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    for job in jobs:
        job.pop("_id", None)
    
    return {
        "jobs": jobs,
        "total": len(jobs)
    }


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    db = Depends(get_database)
):
    result = await db.facefusion_jobs.delete_one({"id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}


@router.get("/characters/{character_id}/gallery")
async def get_character_gallery(
    character_id: str,
    db = Depends(get_database)
):
    character = await db.characters.find_one({"id": character_id})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    gallery = character.get("facefusion_output_gallery", {})
    
    total_images = (
        len(gallery.get("enhanced_faces", [])) +
        len(gallery.get("age_variants", {})) +
        len(gallery.get("swapped_faces", [])) +
        len(gallery.get("edited_expressions", [])) +
        len(gallery.get("custom_outputs", []))
    )
    
    return {
        "character_id": character_id,
        "gallery": gallery,
        "total_images": total_images
    }


@router.get("/characters/{character_id}/history")
async def get_character_processing_history(
    character_id: str,
    limit: int = 50,
    db = Depends(get_database)
):
    character = await db.characters.find_one({"id": character_id})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    history = character.get("facefusion_processing_history", [])
    history_sorted = sorted(history, key=lambda x: x.get("created_at", ""), reverse=True)[:limit]
    
    return {
        "character_id": character_id,
        "history": history_sorted,
        "total": len(history)
    }


@router.put("/characters/{character_id}/settings")
async def update_character_facefusion_settings(
    character_id: str,
    settings: FaceFusionPreferredSettings,
    db = Depends(get_database)
):
    result = await db.characters.update_one(
        {"id": character_id},
        {
            "$set": {
                "facefusion_preferred_settings": settings.dict(),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {
        "message": "Settings updated successfully",
        "character_id": character_id,
        "settings": settings
    }


@router.get("/characters/{character_id}/settings")
async def get_character_facefusion_settings(
    character_id: str,
    db = Depends(get_database)
):
    character = await db.characters.find_one({"id": character_id})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    settings = character.get("facefusion_preferred_settings")
    if not settings:
        settings = FaceFusionPreferredSettings().dict()
    
    return {
        "character_id": character_id,
        "settings": settings
    }
