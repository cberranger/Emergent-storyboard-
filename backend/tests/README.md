# Service Layer Tests

Comprehensive unit tests for all 10 service layer modules with mock repository dependencies.

## Test Coverage

### Core Services
- **test_generation_service.py** - GenerationService (ComfyUI & OpenAI Sora)
- **test_project_service.py** - ProjectService (projects, scenes, clips)
- **test_comfyui_service.py** - ComfyUIClient (standard & RunPod)
- **test_media_service.py** - MediaService (uploads)
- **test_export_service.py** - ExportService (FCP, Premiere, Resolve, JSON)
- **test_openai_video_service.py** - OpenAIVideoService (Sora API)

### Manager Services
- **test_queue_manager.py** - QueueManager (smart queuing)
- **test_gallery_manager.py** - GalleryManager (generated content)
- **test_batch_generator.py** - BatchGenerator (batch processing)

### Integration
- **test_services_integration.py** - Cross-service integration tests

## Running Tests

```powershell
# Run all tests
cd backend
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_generation_service.py -v

# Run with coverage (requires pytest-cov)
python -m pytest tests/ --cov=services --cov-report=term-missing

# Run specific test
python -m pytest tests/test_generation_service.py::TestGenerationService::test_generate_image_success -v
```

## Test Structure

Each test module follows this pattern:

1. **Fixtures** - Mock repositories, sample data, service instances
2. **Success Cases** - Happy path scenarios
3. **Edge Cases** - Boundary conditions, empty data
4. **Error Cases** - Not found errors, validation errors
5. **Integration Cases** - Multiple service interactions

## Mocking Strategy

- **Repositories** - AsyncMock for database operations
- **External APIs** - Mock aiohttp sessions
- **File Operations** - Mock file I/O and pathlib
- **Database** - Mock Motor/MongoDB collections

## Key Features Tested

### Business Logic
- Generation workflows (image, video, batch)
- Project/scene/clip CRUD operations
- Timeline validation and overlap detection
- Queue management and load balancing
- Gallery content management

### Edge Cases
- Missing resources (clip not found, server not found)
- Server offline scenarios
- Invalid parameters and validation
- Retry logic and failure handling
- Priority queue ordering

### DTO Validation
- Pydantic model validation
- Required fields enforcement
- Optional field handling
- Model serialization/deserialization

### Error Handling
- Custom error types (ClipNotFoundError, etc.)
- Service unavailability
- Network failures
- Database connection issues

## Coverage Goals

- **Target**: >80% coverage on services layer
- **Current**: Run `pytest --cov=services` to check

## Dependencies

- pytest==8.0.0
- pytest-asyncio==0.23.5
- pytest-cov==4.1.0
- pytest-mock==3.12.0
