# StoryCanvas Local Development Launcher (PowerShell)
param(
    [string]$FrontendHost = "localhost:3000",
    [string]$BackendHost = "localhost:8001"
)

Write-Host "🎬 StoryCanvas - AI Storyboarding App" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Function to prompt with default
function Get-UserInput {
    param(
        [string]$Prompt,
        [string]$Default
    )
    
    $input = Read-Host "$Prompt [$Default]"
    if ([string]::IsNullOrEmpty($input)) {
        return $Default
    }
    return $input
}

# Get configuration from user
Write-Host "Configuration Setup:" -ForegroundColor Yellow
Write-Host "--------------------"

$FrontendHost = Get-UserInput "Frontend host:port" $FrontendHost
$BackendHost = Get-UserInput "Backend host:port" $BackendHost

# Build URLs
$BackendUrl = "http://$BackendHost"
if ($BackendHost -like "0.0.0.0:*") {
    $BackendPort = $BackendHost.Split(':')[1]
    $ReactAppBackendUrl = "http://localhost:$BackendPort"
} else {
    $ReactAppBackendUrl = $BackendUrl
}

Write-Host ""
Write-Host "📋 Configuration Summary:" -ForegroundColor Green
Write-Host "   Frontend: http://$FrontendHost"
Write-Host "   Backend:  $BackendUrl"
Write-Host "   Frontend will connect to: $ReactAppBackendUrl"
Write-Host ""

# Create backend .env file
Write-Host "🔧 Creating backend configuration..." -ForegroundColor Yellow
$BackendEnv = @"
# Database Configuration
MONGO_URL=mongodb://localhost:27017/storycanvas
DB_NAME=storycanvas

# CORS Configuration  
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://0.0.0.0:3000

# Server Configuration
HOST=$($BackendHost.Split(':')[0])
PORT=$($BackendHost.Split(':')[1])
"@

$BackendEnv | Out-File -FilePath "backend/.env" -Encoding UTF8

# Create frontend .env file
Write-Host "🔧 Creating frontend configuration..." -ForegroundColor Yellow
$FrontendEnv = @"
REACT_APP_BACKEND_URL=$ReactAppBackendUrl
PORT=$($FrontendHost.Split(':')[1])
HOST=$($FrontendHost.Split(':')[0])
"@

$FrontendEnv | Out-File -FilePath "frontend/.env" -Encoding UTF8

# Check if MongoDB is running (Windows)
Write-Host "🗄️ Checking MongoDB..." -ForegroundColor Yellow
$mongoProcess = Get-Process -Name "mongod" -ErrorAction SilentlyContinue
if (-not $mongoProcess) {
    Write-Host "⚠️  MongoDB is not running." -ForegroundColor Yellow
    Write-Host "   Please start MongoDB manually or install MongoDB Community Server"
    Write-Host "   Download: https://www.mongodb.com/try/download/community"
    Write-Host "   Or use MongoDB Atlas (cloud): https://www.mongodb.com/atlas"
    Write-Host ""
}

# Install backend dependencies
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
Push-Location "backend"

if (-not (Test-Path "venv")) {
    Write-Host "    Creating virtual environment..."
    python -m venv venv
}

if (Test-Path "venv/Scripts/activate.ps1") {
    & "venv/Scripts/activate.ps1"
} elseif (Test-Path "venv/Scripts/activate.bat") {
    & "venv/Scripts/activate.bat"
}

pip install -r requirements.txt
Pop-Location

# Install frontend dependencies
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location "frontend"

if (-not (Test-Path "node_modules")) {
    if (Get-Command yarn -ErrorAction SilentlyContinue) {
        yarn install
    } else {
        npm install
    }
}
Pop-Location

# Function to cleanup
function Stop-Services {
    Write-Host ""
    Write-Host "🛑 Shutting down services..." -ForegroundColor Red
    
    if ($BackendJob) {
        Stop-Job $BackendJob
        Remove-Job $BackendJob
        Write-Host "   Backend stopped"
    }
    
    if ($FrontendJob) {
        Stop-Job $FrontendJob  
        Remove-Job $FrontendJob
        Write-Host "   Frontend stopped"
    }
    
    # Kill any remaining processes on our ports
    $BackendPort = $BackendHost.Split(':')[1]
    $FrontendPort = $FrontendHost.Split(':')[1]
    
    $BackendPid = (netstat -ano | Select-String ":$BackendPort " | ForEach-Object { $_.ToString().Split()[-1] } | Select-Object -First 1)
    $FrontendPid = (netstat -ano | Select-String ":$FrontendPort " | ForEach-Object { $_.ToString().Split()[-1] } | Select-Object -First 1)
    
    if ($BackendPid) { Stop-Process -Id $BackendPid -Force -ErrorAction SilentlyContinue }
    if ($FrontendPid) { Stop-Process -Id $FrontendPid -Force -ErrorAction SilentlyContinue }
}

# Set up Ctrl+C handler
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Stop-Services }

# Start backend
Write-Host ""
Write-Host "🚀 Starting backend server..." -ForegroundColor Green
Push-Location "backend"

$BackendScript = {
    if (Test-Path "venv/Scripts/activate.ps1") {
        & "venv/Scripts/activate.ps1"
    }
    $BackendPort = $using:BackendHost.Split(':')[1]
    $BackendBindHost = $using:BackendHost.Split(':')[0]
    uvicorn server:app --host $BackendBindHost --port $BackendPort --reload
}

$BackendJob = Start-Job -ScriptBlock $BackendScript
Pop-Location

# Wait for backend
Write-Host "   Waiting for backend to start..."
Start-Sleep 5

# Test backend
try {
    $response = Invoke-WebRequest -Uri "$ReactAppBackendUrl/api/" -TimeoutSec 5
    Write-Host "   ✅ Backend is running at $BackendUrl" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Backend may still be starting up..." -ForegroundColor Yellow
}

# Start frontend
Write-Host ""
Write-Host "🚀 Starting frontend server..." -ForegroundColor Green
Push-Location "frontend"

$FrontendScript = {
    if (Get-Command yarn -ErrorAction SilentlyContinue) {
        yarn start
    } else {
        npm start
    }
}

$FrontendJob = Start-Job -ScriptBlock $FrontendScript
Pop-Location

Write-Host ""
Write-Host "🎉 StoryCanvas is starting up!" -ForegroundColor Cyan
Write-Host "================================"
Write-Host "📱 Frontend: http://$FrontendHost" -ForegroundColor Green
Write-Host "⚙️  Backend:  $BackendUrl" -ForegroundColor Green
Write-Host "🗄️  Database: MongoDB (local)" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Add your ComfyUI servers:" -ForegroundColor Yellow
Write-Host "   - Local: http://192.168.1.10:7820-7824"  
Write-Host "   - RunPod: https://api.runpod.ai/v2/your-endpoint-id"
Write-Host "   - Ngrok: https://abc123.ngrok-free.app"
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Red
Write-Host ""

# Keep script running and monitor jobs
try {
    while ($true) {
        Start-Sleep 1
        
        # Check if jobs are still running
        if ($BackendJob.State -eq "Failed" -or $BackendJob.State -eq "Completed") {
            Write-Host "❌ Backend job ended unexpectedly" -ForegroundColor Red
            break
        }
        
        if ($FrontendJob.State -eq "Failed" -or $FrontendJob.State -eq "Completed") {
            Write-Host "❌ Frontend job ended unexpectedly" -ForegroundColor Red  
            break
        }
    }
} finally {
    Stop-Services
}