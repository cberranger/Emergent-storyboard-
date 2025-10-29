# 🤖 AGENTS.md - StoryCanvas Developer Quick Reference

## 📦 Initial Setup
```powershell
# Create backend venv in .venv/ directory
cd backend; python -m venv .venv; .venv\Scripts\activate; pip install -r requirements.txt; cd ..

# Install frontend dependencies
cd frontend; npm install; cd ..
```

## 🛠️ Commands
- **Build**: Frontend only - `cd frontend; npm run build`
- **Lint**: Frontend only - `cd frontend; npx eslint src/`
- **Test**: Frontend - `cd frontend; npm test` | Backend - `cd backend; pytest` (tests in root/backend as test_*.py)
- **Dev Server**: `.\launch.bat` (prompts for config) or manually: Backend `cd backend; uvicorn server:app --reload` + Frontend `cd frontend; npm start`

## 🏗️ Tech Stack
- **Backend**: FastAPI + Motor (MongoDB) + aiohttp (ComfyUI integration) + Pydantic
- **Frontend**: React 18 + Shadcn UI + React Router + React DnD + Axios
- **Database**: MongoDB (local or 192.168.1.10:27017)
- **Architecture**: Service Layer + Repository Pattern + DTOs

## 📁 Structure
- `backend/` - FastAPI server with services/, repositories/, api/, dtos/, utils/
- `frontend/src/` - React components, hooks, utils
- Launch scripts create .env files automatically

## 🎨 Code Style
- **Backend**: Snake_case, Pydantic models, async/await, service layer pattern
- **Frontend**: JSX (not TSX), camelCase, functional components with hooks, Shadcn UI components
- **Minimal comments** - code should be self-documenting
- Follow existing patterns in neighboring files
