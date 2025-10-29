# 🤖 AGENTS.md - AI Agent Development Guide

## 📦 Setup Commands

```bash
# Backend
cd backend
python -m venv venv              # Windows: venv\Scripts\activate
source venv/bin/activate         # macOS/Linux
pip install -r requirements.txt

# Frontend
cd frontend
yarn install                     # or npm install

# MongoDB (required)
# Windows: Install MongoDB Community Server
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

## 🛠️ Development Commands

- **Run Dev Server**: `.\launch.bat` (Windows) or `./launch.sh` (macOS/Linux)
- **Backend Only**: `cd backend && uvicorn server:app --host localhost --port 8001 --reload`
- **Frontend Only**: `cd frontend && yarn start`
- **Build Frontend**: `cd frontend && yarn build`
- **Run Tests**: `cd frontend && yarn test`
- **Lint**: No explicit lint script configured

## 🏗️ Architecture

**Stack**: FastAPI (backend) + React (frontend) + MongoDB + ComfyUI integration  
**Backend**: Service layer + Repository pattern + DTOs, API routes in `backend/server.py` and `backend/api/`  
**Frontend**: React components with Shadcn UI, React Router, state via hooks, drag-and-drop timeline  
**Structure**: Projects → Scenes → Clips hierarchy with character/style templates, queue management

## 📁 Key Directories

- `backend/services/` - Business logic layer
- `backend/repositories/` - Data access layer  
- `backend/dtos/` - Pydantic data transfer objects
- `frontend/src/components/` - React components
- `frontend/src/hooks/` - Custom React hooks

## 🎨 Code Style

- **Backend**: Service/repository pattern, async/await, type hints, Pydantic models
- **Frontend**: Functional components, hooks (useState/useEffect), Shadcn UI components
- **Naming**: snake_case (Python), camelCase (JavaScript), PascalCase (components)
- **No comments** unless complex logic requires explanation
- Follow existing patterns in neighboring files
