# StoryCanvas - Agent Guide

## Setup
```bash
# Backend (Python 3.8+, MongoDB required)
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows: Use .venv not venv
pip install -r requirements.txt

# Frontend (Node.js 16+)
cd frontend
yarn install  # or npm install
```

## Commands
- **Build**: `cd frontend && yarn build`
- **Lint**: Frontend has ESLint via `craco test` (no standalone lint command)
- **Test**: `cd frontend && yarn test` (backend: `pytest` if tests exist)
- **Dev**: Run `launch.bat` or `.\launch.ps1` (starts both servers with interactive config)
- **Backend**: `cd backend && uvicorn server:app --host localhost --port 8001 --reload`
- **Frontend**: `cd frontend && yarn start`

## Stack
- **Backend**: FastAPI, MongoDB (Motor), Pydantic, aiohttp
- **Frontend**: React 18, Shadcn UI (Radix), TailwindCSS, React Router, React DnD, Axios
- **Architecture**: Service layer + Repository pattern + DTOs (backend); Component-based (frontend)

## Structure
- `backend/`: API server (`server.py`), services, repositories, DTOs, models, utils
- `frontend/src/`: Components, hooks, utils, services (API layer)
- Virtual env: `.venv/` (per gitignore)

## Style
- **Backend**: Type hints, DTOs for validation, service layer for logic, repository for DB access
- **Frontend**: Functional components with hooks, Shadcn UI components, @ path aliases, minimal comments
- Naming: snake_case (Python), camelCase (JS)
