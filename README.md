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

### Core Functionality
- **Project Management**: Create and organize storyboard projects
- **Scene & Clip System**: Hierarchical structure for complex storyboards
- **Timeline Editor**: Professional drag-and-drop timeline with alternates support
- **ComfyUI Integration**: Support for standard ComfyUI and RunPod serverless
- **Multi-Server Support**: Connect multiple ComfyUI instances
- **Music Upload**: Upload audio for music video projects
- **Version Control**: Multiple versions per clip with comparison

### Advanced Features
- **Character Management**: Create and apply consistent characters across clips
- **Style Templates**: Save and reuse generation parameters
- **Queue Management**: Smart queue with load balancing across servers
- **Batch Generation**: Generate multiple clips simultaneously
- **Export Formats**: Final Cut Pro XML, Adobe Premiere EDL, DaVinci Resolve
- **Generation Pool**: Shared library for reusing generated content
- **Presentation Mode**: Full-screen storyboard presentations
- **Hotkey System**: 40+ keyboard shortcuts for power users
- **Civitai Integration**: Sync models with Civitai database
- **Model Presets**: Default presets for all major model types

### Model Support
- **SDXL**: Full support with custom presets
- **Flux**: Flux Dev, Flux Schnell, Flux Pro variants
- **Pony Diffusion**: Optimized presets
- **Illustrious**: Professional anime presets
- **Wan 2.1/2.2**: Video generation presets
- **LTX-Video**: Lightning-fast video generation
- **Hunyuan Video**: Tencent's video model
- **Qwen Image**: Alibaba's image models
- **And more**: Extensible preset system for new models

## 🏗️ Architecture

### Backend (FastAPI)
- **Service Layer**: Clean separation of business logic
- **Repository Pattern**: Abstracted database operations
- **API Versioning**: `/api/v1` endpoints with backward compatibility
- **Dependency Injection**: Proper service management
- **Error Handling**: Consistent error responses
- **Queue Management**: Smart load balancing across servers

### Frontend (React)
- **Component Architecture**: Modular, reusable components
- **State Management**: Efficient state handling
- **Real-time Updates**: Live queue status and progress
- **Professional UI**: Dark theme with modern design
- **Accessibility**: Proper ARIA labels and keyboard navigation

## 📊 Current Status

### Completed Features ✅
- Phase 1: Critical bug fixes and stability improvements
- Phase 2: Architecture refactoring with service layer
- Phase 2.5: Frontend-backend integration (Character Manager, Style Templates, Queue Dashboard)
- Phase 2.6: Timeline system with alternates support
- Phase 2.7: Generation pool for content reuse
- All major backend APIs implemented
- ComfyUI integration with multi-server support
- Export functionality for professional editors

### In Progress 🔄
- Enhanced model presets system
- Civitai integration improvements
- Performance optimizations

### Planned 📋
- Phase 3: Security & Authentication
- Phase 4: Advanced content features
- Phase 5: Frontend improvements (state management)
- Phase 6: Data management features
- Phase 7: Monitoring & analytics
- Phase 8: Testing & CI/CD

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
│   ├── services/      # Business logic layer
│   ├── repositories/  # Data access layer
│   ├── models/        # Pydantic models
│   ├── utils/         # Utilities and helpers
│   ├── requirements.txt
│   └── .env           # Created by launch script
├── frontend/          # React frontend  
│   ├── src/
│   │   ├── components/
│   │   ├── services/   # API service layer
│   │   ├── hooks/      # Custom React hooks
│   │   └── App.js
│   ├── package.json
│   └── .env           # Created by launch script
├── docs/              # Documentation
│   ├── archive/       # Completed phase docs
│   ├── CHARACTER_CREATION_BEST_PRACTICES.md
│   └── FACEFUSION_INTEGRATION.md
├── launch.ps1         # PowerShell launcher
├── launch.bat         # Batch launcher
└── README.md
```

## 🔧 Development

- **Backend**: FastAPI + MongoDB + aiohttp
- **Frontend**: React + Shadcn UI + React DnD
- **ComfyUI**: Direct API integration + RunPod serverless support
- **Architecture**: Service layer + Repository pattern + DTOs

## 📸 Screenshots

The app features a professional dark theme with:
- Modern sidebar navigation
- Project cards with metadata
- Timeline editor with drag-and-drop clips
- ComfyUI server management
- Generation dialogs with parameter controls
- Character and template libraries
- Queue management dashboard
- Export functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Built for professional storyboarding and music video production workflows.*
