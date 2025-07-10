#!/bin/bash

# SUMO Helper - Quick Start Script
# This script starts both backend and frontend services

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    print_status "Virtual environment not found. Running installation..."
    ./install.sh
fi

print_status "Starting SUMO Helper..."

# Start both services
npm run dev

print_success "SUMO Helper is starting up!"
print_success "Backend: http://localhost:8000"
print_success "Frontend: http://localhost:5173"
print_success "API Docs: http://localhost:8000/docs" 