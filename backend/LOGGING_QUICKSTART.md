# Logging & Monitoring Quick Start

## Setup

The logging system is automatically configured on server startup. No additional setup required.

## Environment Configuration

Add to your `.env` file (optional - defaults shown):

```bash
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json             # json or text
LOG_FILE=backend.log        # Path to log file
LOG_MAX_BYTES=10485760      # 10MB max file size
LOG_BACKUP_COUNT=5          # Number of backup files
ENABLE_CONSOLE_LOG=true     # Also output to console
```

## Using in Code

```python
from utils.logging_config import get_logger

logger = get_logger("my_module")

# Basic logging
logger.info("Operation completed")

# With context
logger.info("User action", user_id="123", action="create_project")

# Error logging
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", error=str(e), exc_info=True)
```

## Admin Metrics API

### Get All Metrics
```bash
GET /api/v1/admin/metrics
```

Returns:
- Total requests and errors
- Per-endpoint statistics (latency, error rates)
- Slow endpoints
- Status code distribution

### Get Slow Endpoints
```bash
GET /api/v1/admin/metrics?slow_threshold_ms=1000
```

### Get Specific Endpoint
```bash
GET /api/v1/admin/metrics/endpoint/projects/list?method=GET
```

### Reset Metrics
```bash
POST /api/v1/admin/metrics/reset
```

## Response Headers

Every API response includes:
- `X-Request-ID` - Unique request identifier
- `X-Response-Time` - Request duration (e.g., "45.23ms")

## Log Format

All logs are JSON:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "storycanvas.request",
  "message": "Request completed",
  "request_id": "a1b2c3d4-...",
  "method": "POST",
  "path": "/api/v1/projects",
  "status_code": 201,
  "duration_ms": 45.23
}
```

## Monitoring Tips

```bash
# Watch for errors
tail -f backend.log | grep '"level":"ERROR"'

# Extract slow requests (>1 second)
grep -E '"duration_ms":[0-9]{4,}' backend.log

# View metrics in browser
curl http://localhost:8001/api/v1/admin/metrics | jq
```

## Features

✅ Structured JSON logging  
✅ Request ID correlation  
✅ Performance tracking  
✅ Error context capture  
✅ Automatic log rotation  
✅ Real-time metrics dashboard  
✅ Slow endpoint detection  
✅ No code changes required  
