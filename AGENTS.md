# AGENTS.md - StoryCanvas Development Guide

## Commands

**Initial Setup:**
```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
yarn install  # or npm install
```

**Build:** `cd frontend && yarn build`

**Lint:** `cd frontend && npx eslint src/`

**Tests:** No test framework currently configured

**Dev Server:** `.\launch.bat` or `.\launch.ps1` (starts both backend & frontend)

## Tech Stack

- **Backend:** FastAPI, MongoDB (Motor), aiohttp, Pydantic
- **Frontend:** React 18, Shadcn UI, React Router, React DnD, Axios
- **Architecture:** Service layer + Repository pattern with DTOs

## Repo Structure

- `backend/` - FastAPI server with `server.py`, `services/`, `repositories/`, `dtos/`, `api/v1/`
- `frontend/src/` - React app with `components/`, `hooks/`, `utils/`, main `App.js`
- `docs/` - Documentation and implementation guides

## Code Style

- No comments unless complex logic requires explanation
- Follow existing patterns: check neighboring files for conventions
- Use TypeScript-style JSDoc for complex functions (frontend)
- Python: PEP 8 style, async/await for I/O operations
- React: Functional components with hooks, extract reusable logic to custom hooks
