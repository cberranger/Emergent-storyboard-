# Logging and Monitoring Configuration

## Overview

StoryCanvas backend implements structured JSON logging with request tracking, performance monitoring, and an admin dashboard for metrics analysis.

## Features

- **Structured JSON Logging**: All logs output in JSON format with consistent schema
- **Request ID Tracking**: Every request gets a unique correlation ID for tracking
- **Performance Monitoring**: Track endpoint latency and identify bottlenecks
- **Log Rotation**: Automatic log file rotation to prevent disk space issues
- **Admin Dashboard**: Real-time metrics and performance statistics

## Environment Variables

Configure logging behavior via environment variables in your `.env` file:

```bash
# Log Level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log Format: json or text
LOG_FORMAT=json

# Log File Path
LOG_FILE=backend.log

# Log Rotation - Max file size in bytes (default: 10MB)
LOG_MAX_BYTES=10485760

# Log Rotation - Number of backup files to keep
LOG_BACKUP_COUNT=5

# Enable/disable console output
ENABLE_CONSOLE_LOG=true
```

## Log Format

All logs are structured JSON with the following schema:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "storycanvas.request",
  "message": "Request completed",
  "module": "logging_middleware",
  "function": "dispatch",
  "line": 125,
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/api/v1/projects",
  "status_code": 201,
  "duration_ms": 45.23,
  "duration_seconds": 0.045
}
```

### Request Logging

Each request logs:
- **Start**: Method, path, query params, client info, user agent, request body (truncated if large)
- **End**: Status code, duration, error context (if any)
- **Request ID**: Unique identifier added to response headers as `X-Request-ID`

### Performance Tracking

Performance middleware automatically tracks:
- **Request count** per endpoint
- **Latency metrics**: min, max, avg, p50, p95, p99
- **Error rates** and status code distribution
- **Slow endpoint detection**

## Admin Dashboard

Access metrics via the admin API endpoints:

### Get All Metrics
```http
GET /api/v1/admin/metrics
```

Response:
```json
{
  "status": "ok",
  "stats": {
    "uptime_seconds": 3600,
    "total_requests": 1523,
    "total_errors": 12,
    "overall_error_rate": 0.79,
    "endpoints": [
      {
        "endpoint": "POST /api/v1/generation/generate",
        "request_count": 456,
        "avg_latency_ms": 1234.56,
        "min_latency_ms": 234.12,
        "max_latency_ms": 5678.90,
        "p50_latency_ms": 1100.00,
        "p95_latency_ms": 2500.00,
        "p99_latency_ms": 4000.00,
        "error_count": 5,
        "error_rate": 1.10,
        "status_codes": {
          "200": 450,
          "500": 5,
          "503": 1
        }
      }
    ]
  },
  "slow_endpoints": [...],
  "bottlenecks": [...]
}
```

### Get Slow Endpoints
```http
GET /api/v1/admin/metrics?slow_threshold_ms=1000
```

Returns endpoints with average latency above threshold.

### Get Specific Endpoint Metrics
```http
GET /api/v1/admin/metrics/endpoint/generation/generate?method=POST
```

### Reset Metrics
```http
POST /api/v1/admin/metrics/reset
```

## Response Headers

Every response includes:
- `X-Request-ID`: Unique request identifier for correlation
- `X-Response-Time`: Request duration in milliseconds

## Usage Examples

### Finding Slow Requests

1. Check admin dashboard for slow endpoints
2. Use request ID from logs to trace specific slow requests
3. Analyze error context for failed requests

### Debugging Issues

When a user reports an issue:
1. Get the `X-Request-ID` from browser dev tools (Response Headers)
2. Search logs for that request ID to see full request lifecycle
3. Check error context, duration, and request/response details

### Monitoring Performance

```bash
# Watch for errors in real-time
tail -f backend.log | grep '"level":"ERROR"'

# Extract slow requests (>1 second)
grep -E '"duration_ms":[0-9]{4,}' backend.log

# Count requests by endpoint
grep '"Request completed"' backend.log | jq -r '.path' | sort | uniq -c
```

## Best Practices

1. **Use appropriate log levels**:
   - `DEBUG`: Detailed diagnostic information
   - `INFO`: General informational messages
   - `WARNING`: Warning messages, non-critical issues
   - `ERROR`: Error messages, critical issues
   - `CRITICAL`: Critical failures requiring immediate attention

2. **Include context**: The structured logger accepts additional kwargs for context

3. **Monitor metrics regularly**: Check admin dashboard for performance degradation

4. **Set up alerts**: Monitor error rates and slow endpoints in production

5. **Log rotation**: Ensure `LOG_MAX_BYTES` and `LOG_BACKUP_COUNT` are appropriate for your traffic

## Integration

The logging system is automatically initialized on application startup. All FastAPI routes benefit from request/response logging without additional code.

To use structured logging in your code:

```python
from utils.logging_config import get_logger

logger = get_logger("my_module")

# Log with additional context
logger.info("Processing started", 
            user_id="123", 
            project_id="abc",
            operation="generate_image")

# Log errors with context
try:
    result = some_operation()
except Exception as e:
    logger.error("Operation failed",
                 error=str(e),
                 operation="generate_image",
                 exc_info=True)
```
