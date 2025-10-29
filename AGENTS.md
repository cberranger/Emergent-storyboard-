# Agent Commands & Guidelines

## Setup
```bash
cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt
cd ../frontend && yarn install
```

## Commands
- **Build**: `cd frontend && yarn build`
- **Lint**: `cd frontend && npx eslint src/`
- **Test**: `python backend/test_*.py` (no formal test framework)
- **Dev**: `.\launch.bat` (starts backend on :8001, frontend on :3000)

## Stack
- **Backend**: FastAPI + MongoDB + Motor (async) + aiohttp
- **Frontend**: React 18 + Shadcn UI + React DnD + Tailwind CSS
- **Architecture**: Service layer + Repository pattern + DTOs

## Structure
- `backend/server.py` - Main API server
- `backend/services/` - Business logic (project, queue, generation, comfyui, export)
- `backend/repositories/` - Database access layer
- `frontend/src/components/` - React components (.jsx for UI, .js for older)

## Style
- Backend: 4-space indent, snake_case, Pydantic models for validation
- Frontend: 2-space indent, camelCase, functional components with hooks
- No comments unless complex logic; follow existing patterns; use shadcn/ui components
