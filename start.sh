#!/bin/bash

# SUMO Helper Development Start Script
# This script starts the application in development mode

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running in development mode
if [ "$1" != "dev" ]; then
    echo "This script is for development only."
    echo "For production deployment, use: ./deploy.sh"
    exit 1
fi

log "Starting SUMO Helper in development mode..."

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "Error: Backend directory not found"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "Error: Frontend directory not found"
    exit 1
fi

# Start backend
log "Starting backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    warning "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/lib/python*/site-packages/fastapi" ]; then
    log "Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Start backend in background
log "Starting FastAPI server..."
python main.py &
BACKEND_PID=$!

cd ..

# Start frontend
log "Starting frontend development server..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    log "Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
log "Starting Vite development server..."
npm run dev &
FRONTEND_PID=$!

cd ..

# Wait a moment for services to start
sleep 3

# Show status
success "Development servers started!"
echo ""
echo "Service URLs:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    log "Stopping development servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    success "Development servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait 