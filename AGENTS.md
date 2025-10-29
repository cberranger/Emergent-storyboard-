# StoryCanvas - AI Agent Guide

## Setup
```bash
# Backend - Python virtual environment in venv/
cd backend
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate | Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# Frontend - Node.js with Yarn
cd frontend
yarn install  # or npm install
```

## Commands
- **Build**: `cd frontend && yarn build`
- **Lint**: `cd frontend && yarn eslint`  _(Note: No explicit lint script defined)_
- **Test**: Backend: `python -m pytest` Frontend: `cd frontend && yarn test`
- **Dev Server**: `.\launch.bat` (automated) or manually:
  - Backend: `cd backend && uvicorn server:app --reload --host localhost --port 8001`
  - Frontend: `cd frontend && yarn start` (port 3000)

## Tech Stack
- **Backend**: FastAPI + MongoDB (Motor) + aiohttp | Service/Repository pattern
- **Frontend**: React 18 + Shadcn UI + React DnD + Tailwindcss
- **Integration**: ComfyUI API, RunPod serverless, FaceFusion
- **Database**: MongoDB (default: `192.168.1.10:27017`, db: `storyboard`)

## Architecture
- Backend: `/api/v1` versioned endpoints, service layer (`services/`), repository pattern (`repositories/`), Pydantic DTOs
- Frontend: Component-based (`components/`), hooks (`hooks/`), API service layer, React Router

## Code Conventions
- **Style**: No excessive comments; follow existing patterns
- **Backend**: Async/await, dependency injection, centralized error handling
- **Frontend**: Functional components, custom hooks, JSX with Tailwind utilities
- **Naming**: PascalCase for components/classes, snake_case for Python, camelCase for JS variables
