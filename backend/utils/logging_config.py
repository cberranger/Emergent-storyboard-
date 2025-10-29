import logging
import logging.handlers
import os
import sys
from pathlib import Path


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname', 
                          'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname', 'process', 
                          'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info', 
                          'exc_text', 'stack_info', 'request_id']:
                log_data[key] = value
        
        return json.dumps(log_data)


def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "json").lower()
    log_file = os.getenv("LOG_FILE", "backend.log")
    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    enable_console_log = os.getenv("ENABLE_CONSOLE_LOG", "true").lower() == "true"
    
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    level = level_map.get(log_level, logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=log_max_bytes,
        backupCount=log_backup_count
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    if enable_console_log:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    app_logger = logging.getLogger("storycanvas")
    app_logger.setLevel(level)
    
    request_logger = logging.getLogger("storycanvas.request")
    request_logger.setLevel(level)
    
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    return app_logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"storycanvas.{name}")
