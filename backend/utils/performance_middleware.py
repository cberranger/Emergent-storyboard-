import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Callable, Dict, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import threading
import statistics


class PerformanceTracker:
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.status_codes: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self.lock = threading.Lock()
        self.start_time = datetime.utcnow()
    
    def record_request(self, endpoint: str, duration: float, status_code: int):
        with self.lock:
            self.request_times[endpoint].append(duration)
            self.request_counts[endpoint] += 1
            self.status_codes[endpoint][status_code] += 1
            
            if status_code >= 500:
                self.error_counts[endpoint] += 1
    
    def get_endpoint_stats(self, endpoint: str) -> Dict:
        with self.lock:
            times = list(self.request_times[endpoint])
            
            if not times:
                return {
                    "endpoint": endpoint,
                    "request_count": 0,
                    "avg_latency_ms": 0,
                    "min_latency_ms": 0,
                    "max_latency_ms": 0,
                    "p50_latency_ms": 0,
                    "p95_latency_ms": 0,
                    "p99_latency_ms": 0,
                    "error_count": 0,
                    "error_rate": 0,
                    "status_codes": {}
                }
            
            times_ms = [t * 1000 for t in times]
            sorted_times = sorted(times_ms)
            
            return {
                "endpoint": endpoint,
                "request_count": self.request_counts[endpoint],
                "avg_latency_ms": round(statistics.mean(times_ms), 2),
                "min_latency_ms": round(min(times_ms), 2),
                "max_latency_ms": round(max(times_ms), 2),
                "p50_latency_ms": round(sorted_times[len(sorted_times) // 2], 2),
                "p95_latency_ms": round(sorted_times[int(len(sorted_times) * 0.95)], 2),
                "p99_latency_ms": round(sorted_times[int(len(sorted_times) * 0.99)], 2),
                "error_count": self.error_counts[endpoint],
                "error_rate": round(self.error_counts[endpoint] / self.request_counts[endpoint] * 100, 2),
                "status_codes": dict(self.status_codes[endpoint])
            }
    
    def get_all_stats(self) -> Dict:
        with self.lock:
            endpoints = list(self.request_counts.keys())
        
        stats = [self.get_endpoint_stats(endpoint) for endpoint in endpoints]
        
        stats.sort(key=lambda x: x["avg_latency_ms"], reverse=True)
        
        total_requests = sum(s["request_count"] for s in stats)
        total_errors = sum(s["error_count"] for s in stats)
        
        return {
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "overall_error_rate": round(total_errors / total_requests * 100, 2) if total_requests > 0 else 0,
            "endpoints": stats
        }
    
    def get_slow_endpoints(self, threshold_ms: float = 1000) -> List[Dict]:
        with self.lock:
            endpoints = list(self.request_counts.keys())
        
        slow_endpoints = []
        for endpoint in endpoints:
            stats = self.get_endpoint_stats(endpoint)
            if stats["avg_latency_ms"] > threshold_ms:
                slow_endpoints.append(stats)
        
        slow_endpoints.sort(key=lambda x: x["avg_latency_ms"], reverse=True)
        return slow_endpoints
    
    def reset_stats(self):
        with self.lock:
            self.request_times.clear()
            self.request_counts.clear()
            self.error_counts.clear()
            self.status_codes.clear()
            self.start_time = datetime.utcnow()


performance_tracker = PerformanceTracker()


class PerformanceMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, tracker: PerformanceTracker = None):
        super().__init__(app)
        self.tracker = tracker or performance_tracker
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        endpoint = f"{request.method} {request.url.path}"
        
        self.tracker.record_request(endpoint, duration, response.status_code)
        
        response.headers["X-Response-Time"] = f"{round(duration * 1000, 2)}ms"
        
        return response
