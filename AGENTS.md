# StoryCanvas Developer Guide

## Setup & Commands

### Initial Setup
```bash
# Backend (Python 3.8+, MongoDB required)
cd backend
python -m venv venv  # or .venv
venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt

# Frontend (Node.js 16+)
cd frontend
yarn install  # or npm install
```

### Run Commands
- **Dev Server**: `.\launch.bat` or `.\launch.sh` (starts both frontend & backend)
- **Backend Only**: `cd backend && uvicorn server:app --host localhost --port 8001 --reload`
- **Frontend Only**: `cd frontend && yarn start`
- **Build**: `cd frontend && yarn build`
- **Lint**: No lint configured (ESLint dependencies present but not configured)
- **Tests**: No test framework configured

## Tech Stack
- **Backend**: FastAPI + Motor (MongoDB) + aiohttp
- **Frontend**: React 18 + Shadcn UI + Radix UI + React DnD + Tailwind CSS
- **Architecture**: Service layer pattern with repositories, DTOs, and API versioning (`/api/v1`)

## Code Conventions
- **Python**: Service layer for business logic, repository pattern for data access, Pydantic models for validation
- **React**: Functional components with hooks, shadcn/ui components via CVA (class-variance-authority), utility-first CSS with Tailwind
- **Naming**: camelCase (JS), snake_case (Python)
- **Styling**: Dark theme, `cn()` utility for class merging, CVA for component variants
