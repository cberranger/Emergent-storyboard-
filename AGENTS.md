# AGENTS.md

## 🚀 Commands

### Initial Setup
```bash
# Backend: Python 3.8+, create venv/ or .venv/ (see .gitignore)
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend: Node.js 16+, Yarn preferred
cd frontend
yarn install  # or npm install
```

### Build
```bash
cd frontend
yarn build  # or npm run build
```

### Lint
```bash
cd frontend
npx eslint src  # ESLint installed but no config file yet
```

### Tests
```bash
# Backend: test_*.py files exist but no framework configured
cd backend
python -m pytest  # if pytest is added

# Frontend: CRA test runner
cd frontend
yarn test  # or npm test
```

### Dev Server
```bash
# Automated: launch.bat or launch.ps1 (starts both)
.\launch.bat

# Manual Backend
cd backend
venv\Scripts\activate
uvicorn server:app --host localhost --port 8001 --reload

# Manual Frontend
cd frontend
yarn start  # or npm start (port 3000)
```

## 🏗️ Tech Stack

**Backend:** FastAPI, Motor (async MongoDB), Pydantic, aiohttp (ComfyUI client)  
**Frontend:** React 18, Shadcn UI (56 Radix components), React DnD, Axios, React Router  
**Database:** MongoDB  
**AI:** ComfyUI integration (image/video), RunPod serverless support, OpenAI (Sora)

## 📁 Architecture

- **Backend:** Service layer → Repository pattern → MongoDB
- **Frontend:** Component-based, API service layer in `src/services/`, hooks in `src/hooks/`
- **Key directories:** `backend/services/`, `backend/repositories/`, `frontend/src/components/`

## 🎨 Code Style

- **No comments** unless complex logic requires context
- Follow existing patterns: check imports, neighboring files, package.json for libs
- Backend: snake_case, type hints; Frontend: camelCase, functional components, destructured props
- Use Shadcn UI components (`@/components/ui/`), Tailwind utilities, dark theme defaults
