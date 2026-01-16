#!/bin/bash

# StoryCanvas Local Development Launcher
echo "🎬 StoryCanvas - AI Storyboarding App"
echo "====================================="
echo ""

# Function to ask for user input with default
ask_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    echo -n "$prompt [$default]: "
    read user_input
    
    if [[ -z "$user_input" ]]; then
        eval "$var_name='$default'"
    else
        eval "$var_name='$user_input'"
    fi
}

# Get configuration from user
echo "Configuration Setup:"
echo "--------------------"

ask_with_default "Frontend host:port" "0.0.0.0:3000" "FRONTEND_HOST"
ask_with_default "Backend host:port" "0.0.0.0:8001" "BACKEND_HOST"

# Extract host and port for backend
BACKEND_PROTOCOL="http"
BACKEND_URL="$BACKEND_PROTOCOL://$BACKEND_HOST"

# For frontend, we need the full backend URL that the browser can reach
if [[ $BACKEND_HOST == "0.0.0.0:"* ]]; then
    BACKEND_PORT=${BACKEND_HOST#*:}
    REACT_APP_BACKEND_URL="http://localhost:$BACKEND_PORT"
else
    REACT_APP_BACKEND_URL="$BACKEND_URL"
fi

echo ""
echo "📋 Configuration Summary:"
echo "   Frontend: http://$FRONTEND_HOST"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend will connect to: $REACT_APP_BACKEND_URL"
echo ""

# Create backend .env file
echo "🔧 Creating backend configuration..."
cat > backend/.env << EOF
# Database Configuration
MONGO_URL=mongodb://localhost:27017/storycanvas
DB_NAME=storyboard

# CORS Policy (allow-all)
CORS_ORIGINS=*

# Server Configuration
HOST=${BACKEND_HOST%:*}
PORT=${BACKEND_HOST#*:}
EOF

# Create frontend .env file
echo "🔧 Creating frontend configuration..."
cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
PORT=${FRONTEND_HOST#*:}
HOST=${FRONTEND_HOST%:*}
EOF

# Check if MongoDB is running
echo "🗄️  Checking MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB is not running. Starting MongoDB..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl start mongod
    elif command -v brew &> /dev/null && brew services list | grep mongodb; then
        brew services start mongodb-community
    else
        echo "❌ Please start MongoDB manually"
        echo "   Ubuntu/Debian: sudo systemctl start mongod"
        echo "   macOS: brew services start mongodb-community"
        exit 1
    fi
fi

# Install dependencies
echo "📦 Installing dependencies..."

echo "  - Installing backend dependencies..."
cd backend
if [[ ! -d "venv" ]]; then
    echo "    Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
cd ..

echo "  - Installing frontend dependencies..."
cd frontend
if [[ ! -d "node_modules" ]]; then
    if command -v yarn &> /dev/null; then
        yarn install
    else
        npm install
    fi
fi
cd ..

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [[ ! -z "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null
        echo "   Backend stopped"
    fi
    if [[ ! -z "$FRONTEND_PID" ]]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   Frontend stopped" 
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo ""
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate
BACKEND_PORT=${BACKEND_HOST#*:}
BACKEND_BIND_HOST=${BACKEND_HOST%:*}
uvicorn server:app --host $BACKEND_BIND_HOST --port $BACKEND_PORT --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "   Waiting for backend to start..."
sleep 3

# Test backend
if curl -s "$REACT_APP_BACKEND_URL/api/" > /dev/null; then
    echo "   ✅ Backend is running at $BACKEND_URL"
else
    echo "   ⚠️  Backend may still be starting up..."
fi

# Start frontend
echo ""
echo "🚀 Starting frontend server..."
cd frontend
if command -v yarn &> /dev/null; then
    yarn start &
else
    npm start &
fi
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 StoryCanvas is starting up!"
echo "================================"
echo "📱 Frontend: http://$FRONTEND_HOST"
echo "⚙️  Backend:  $BACKEND_URL"
echo "🗄️  Database: MongoDB (local)"
echo ""
echo "🔗 Add your ComfyUI servers:"
echo "   - Local: http://192.168.1.10:7820-7824"  
echo "   - RunPod: https://api.runpod.ai/v2/your-endpoint-id"
echo "   - Ngrok: https://abc123.ngrok-free.app"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
