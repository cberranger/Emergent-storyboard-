@echo off
setlocal EnableDelayedExpansion

:: StoryCanvas Local Development Launcher (Batch)
echo 🎬 StoryCanvas - AI Storyboarding App
echo =====================================
echo.

:: Default values
set "FRONTEND_HOST=localhost:3000"
set "BACKEND_HOST=localhost:8001"

:: Get user input with defaults
echo Configuration Setup:
echo --------------------

set /p "USER_FRONTEND=Frontend host:port [%FRONTEND_HOST%]: "
if not "!USER_FRONTEND!"=="" set "FRONTEND_HOST=!USER_FRONTEND!"

set /p "USER_BACKEND=Backend host:port [%BACKEND_HOST%]: "
if not "!USER_BACKEND!"=="" set "BACKEND_HOST=!USER_BACKEND!"

echo.
set /p "OPENAI_API_KEY_INPUT=OpenAI API key (leave blank to skip): "

:: Parse hosts and ports
for /f "tokens=1,2 delims=:" %%a in ("%BACKEND_HOST%") do (
    set "BACKEND_IP=%%a"
    set "BACKEND_PORT=%%b"
)

for /f "tokens=1,2 delims=:" %%a in ("%FRONTEND_HOST%") do (
    set "FRONTEND_IP=%%a" 
    set "FRONTEND_PORT=%%b"
)

:: Build URLs
set "BACKEND_URL=http://%BACKEND_HOST%"
if "%BACKEND_IP%"=="0.0.0.0" (
    set "REACT_APP_BACKEND_URL=http://localhost:!BACKEND_PORT!"
) else (
    set "REACT_APP_BACKEND_URL=!BACKEND_URL!"
)

echo.
echo 📋 Configuration Summary:
echo    Frontend: http://%FRONTEND_HOST%
echo    Backend:  %BACKEND_URL%  
:: Create backend .env file
echo Creating backend configuration...
(
echo # Database Configuration
echo MONGO_URL=mongodb://192.168.1.10:27017
echo DB_NAME=storyboard
echo.
echo # CORS Configuration
echo CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://0.0.0.0:3000
echo.
echo # Server Configuration
echo PORT=%BACKEND_PORT%
) > backend\.env

:: Optionally append OpenAI API key for Sora integration
if defined OPENAI_API_KEY_INPUT (
    echo OPENAI_API_KEY=%OPENAI_API_KEY_INPUT%>> backend\.env
    echo 🔑 Added OpenAI API key to backend\.env
) else (
    echo ⚠️  OPENAI_API_KEY not provided. Sora generation will be unavailable until set.
)

:: Create frontend .env file  
echo 🔧 Creating frontend configuration...
(
echo REACT_APP_BACKEND_URL=!REACT_APP_BACKEND_URL!
echo PORT=%FRONTEND_PORT%
echo HOST=%FRONTEND_IP%
) > frontend\.env

:: Check MongoDB
echo 🗄️ Checking MongoDB connection...
echo    Remote MongoDB at 192.168.1.10:27017

:: Install backend dependencies
echo 📦 Installing backend dependencies...
cd backend

if not exist "venv" (
    echo     Creating virtual environment...
    python -m venv venv
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

cd ..

:: Install frontend dependencies  
echo 📦 Installing frontend dependencies...
cd frontend

if not exist "node_modules" (
    where yarn >nul 2>&1
    if not errorlevel 1 (
        yarn install
    ) else (
        npm install  
    )
)

cd ..

:: Start backend
echo.
echo 🚀 Starting backend server...
cd backend
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
start "StoryCanvas Backend" cmd /k "uvicorn server:app --host %BACKEND_IP% --port %BACKEND_PORT% --reload"
cd ..

:: Wait for backend
echo    Waiting for backend to start...
timeout /t 5 /nobreak >nul

:: Test backend  
echo    Testing backend connection...
curl -s "!REACT_APP_BACKEND_URL!/api/" >nul 2>&1
if not errorlevel 1 (
    echo    ✅ Backend is running at %BACKEND_URL%
) else (
    echo    ⚠️  Backend may still be starting up...
)

:: Start frontend
echo.  
echo 🚀 Starting frontend server...
cd frontend
where yarn >nul 2>&1
if not errorlevel 1 (
    start "StoryCanvas Frontend" cmd /k "yarn start"
) else (
    start "StoryCanvas Frontend" cmd /k "npm start"  
)
cd ..

echo.
echo 🎉 StoryCanvas is starting up!
echo ================================
echo 📱 Frontend: http://%FRONTEND_HOST%
echo ⚙️  Backend:  %BACKEND_URL%
echo 🗄️  Database: MongoDB (192.168.1.10)
echo.
echo 🔗 Add your ComfyUI servers:
echo    - Local: http://192.168.1.10:7820-7824
echo    - RunPod: https://api.runpod.ai/v2/your-endpoint-id  
echo    - Ngrok: https://abc123.ngrok-free.app
echo.
echo Both services are starting in separate windows.
echo Close those windows to stop the services.
echo.
pause