import json
import logging
import time
import uuid
from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message
import traceback
import sys


class StructuredLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log(self, level: int, msg: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": msg,
            **kwargs
        }
        self.logger.log(level, json.dumps(log_entry))
    
    def debug(self, msg: str, **kwargs):
        self.log(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg: str, **kwargs):
        self.log(logging.INFO, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        self.log(logging.WARNING, msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        self.log(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg: str, **kwargs):
        self.log(logging.CRITICAL, msg, **kwargs)


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger: logging.Logger = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger("storycanvas.request")
        self.structured_logger = StructuredLogger(self.logger)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        request_body = body_bytes.decode('utf-8')
                        if len(request_body) > 1000:
                            request_body = request_body[:1000] + "... (truncated)"
                    except:
                        request_body = "[binary data]"
                
                received = False

                async def receive() -> Message:
                    nonlocal received
                    if received:
                        return {"type": "http.request", "body": b"", "more_body": False}
                    received = True
                    return {"type": "http.request", "body": body_bytes, "more_body": False}
                request._receive = receive
            except:
                pass
        
        self.structured_logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            content_type=request.headers.get("content-type"),
            request_body=request_body
        )
        
        response = None
        error_context = None
        
        try:
            response = await call_next(request)
        except Exception as e:
            error_context = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            
            self.structured_logger.error(
                "Request error",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                **error_context
            )
            
            raise
        finally:
            duration = time.time() - start_time
            
            status_code = response.status_code if response else 500
            
            log_level = logging.INFO
            if status_code >= 500:
                log_level = logging.ERROR
            elif status_code >= 400:
                log_level = logging.WARNING
            
            log_data = {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": round(duration * 1000, 2),
                "duration_seconds": round(duration, 3)
            }
            
            if error_context:
                log_data.update(error_context)
            
            self.structured_logger.log(
                log_level,
                "Request completed",
                **log_data
            )
            
            if response:
                response.headers["X-Request-ID"] = request_id
        
        return response
