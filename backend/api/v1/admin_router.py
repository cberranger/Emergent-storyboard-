from fastapi import APIRouter, Query
from typing import Optional
from utils.performance_middleware import performance_tracker

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/metrics")
async def get_metrics(
    slow_threshold_ms: Optional[float] = Query(default=1000, description="Threshold for slow endpoint detection")
):
    stats = performance_tracker.get_all_stats()
    slow_endpoints = performance_tracker.get_slow_endpoints(threshold_ms=slow_threshold_ms)
    
    return {
        "status": "ok",
        "stats": stats,
        "slow_endpoints": slow_endpoints,
        "bottlenecks": [
            endpoint for endpoint in slow_endpoints[:10]
        ]
    }


@router.post("/metrics/reset")
async def reset_metrics():
    performance_tracker.reset_stats()
    return {
        "status": "ok",
        "message": "Metrics reset successfully"
    }


@router.get("/metrics/endpoint/{endpoint_path:path}")
async def get_endpoint_metrics(endpoint_path: str, method: str = Query(default="GET")):
    endpoint = f"{method.upper()} /{endpoint_path}"
    stats = performance_tracker.get_endpoint_stats(endpoint)
    
    return {
        "status": "ok",
        "endpoint": stats
    }
