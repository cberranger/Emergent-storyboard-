# 🎬 StoryCanvas - AI Storyboarding App

A professional storyboarding application with ComfyUI integration for AI-powered image and video generation.

## 🚀 Quick Start (Windows)

### Option 1: PowerShell (Recommended)
```powershell
.\launch.ps1
```

### Option 2: Batch File
```cmd
launch.bat
```

Both scripts will:
- Ask for frontend/backend ports (defaults: frontend=3000, backend=8001)
- Create proper `.env` files
- Install dependencies
- Start both frontend and backend servers

## 📋 Prerequisites

### Required:
- **Node.js** (v16+) - [Download](https://nodejs.org/)
- **Python** (3.8+) - [Download](https://python.org/downloads/)
- **MongoDB** - [Download Community Server](https://www.mongodb.com/try/download/community)

### Optional:
- **Yarn** (recommended over npm)
- **Git** (for cloning)

## 🔗 ComfyUI Integration

### Local ComfyUI
If running ComfyUI locally (e.g., Unraid Docker):
```
http://192.168.1.10:7820  # Example local IP:port
```

### RunPod Serverless
For RunPod endpoints:
```
https://api.runpod.ai/v2/your-endpoint-id
```
*Requires API key*

### Ngrok Tunnel
To expose local ComfyUI publicly:
```bash
# Install ngrok
winget install ngrok

# Expose ComfyUI (assuming port 8188)
ngrok http 8188

# Use the provided https URL in StoryCanvas
```

## 🛠️ Manual Setup

If you prefer manual setup:

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create backend/.env
MONGO_URL=mongodb://localhost:27017/storycanvas
DB_NAME=storycanvas
CORS_ORIGINS=http://localhost:3000
HOST=localhost
PORT=8001

# Start server
uvicorn server:app --host localhost --port 8001 --reload
```

### Frontend
```bash
cd frontend
npm install  # or yarn install

# Create frontend/.env  
REACT_APP_BACKEND_URL=http://localhost:8001
PORT=3000
HOST=localhost

# Start development server
npm start  # or yarn start
```

## 🎯 Features

- **Project Management**: Create and organize storyboard projects
- **Scene & Clip System**: Hierarchical structure for complex storyboards
- **Timeline Editor**: Professional drag-and-drop timeline interface
- **ComfyUI Integration**: Support for standard ComfyUI and RunPod serverless
- **Multi-Server Support**: Connect multiple ComfyUI instances
- **Music Upload**: Upload audio for music video projects
- **Version Control**: Multiple versions per clip with comparison

## 🐛 Troubleshooting

### MongoDB Issues
- **Windows**: Install MongoDB Community Server or use MongoDB Atlas
- **Check if running**: Task Manager → Look for `mongod.exe`
- **Alternative**: Use MongoDB Atlas (cloud) and update MONGO_URL in backend/.env

### Port Conflicts
- Change ports in launch script when prompted
- Default ports: Frontend=3000, Backend=8001

### ComfyUI Connection Issues
- Ensure ComfyUI is accessible from your network
- For Docker/Unraid: Check port forwarding and `--listen 0.0.0.0` flag
- Use ngrok for external access

### Environment Variables
- If API calls show "undefined", restart the frontend server
- Check that `.env` files were created properly

## 📁 Project Structure

```
storycanvas/
├── backend/           # FastAPI backend
│   ├── server.py      # Main API server
│   ├── requirements.txt
│   └── .env           # Created by launch script
├── frontend/          # React frontend  
│   ├── src/
│   │   ├── components/
│   │   └── App.js
│   ├── package.json
│   └── .env           # Created by launch script
├── launch.ps1         # PowerShell launcher
├── launch.bat         # Batch launcher
└── README.md
```

## 🔧 Development

- Backend: FastAPI + MongoDB + aiohttp
- Frontend: React + Shadcn UI + React DnD
- ComfyUI: Direct API integration + RunPod serverless support

## 📸 Screenshots

The app features a professional dark theme with:
- Modern sidebar navigation
- Project cards with metadata
- Timeline editor with drag-and-drop clips
- ComfyUI server management
- Generation dialogs with parameter controls

---

*Built for professional storyboarding and music video production workflows.*
