#!/bin/bash

# SUMO Helper Installation Script
# This script sets up the development environment

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed. Please install Python 3.11+ first."
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [ "$(printf '%s\n' "3.11" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.11" ]; then
        warning "Python version $PYTHON_VERSION detected. Python 3.11+ is recommended."
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js is not installed. Please install Node.js 18+ first."
    fi
    
    # Check Node.js version
    NODE_VERSION=$(node -v | cut -d'v' -f2)
    if [ "$(printf '%s\n' "18.0.0" "$NODE_VERSION" | sort -V | head -n1)" != "18.0.0" ]; then
        warning "Node.js version $NODE_VERSION detected. Node.js 18+ is recommended."
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        error "npm is not installed. Please install npm first."
    fi
    
    success "Prerequisites check passed"
}

# Install backend dependencies
install_backend() {
    log "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    log "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    log "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install development dependencies if file exists
    if [ -f "requirements-dev.txt" ]; then
        log "Installing development dependencies..."
        pip install -r requirements-dev.txt
    fi
    

    
    cd ..
    success "Backend setup completed"
}

# Install frontend dependencies
install_frontend() {
    log "Setting up frontend..."
    
    cd frontend
    
    # Install Node.js dependencies
    log "Installing Node.js dependencies..."
    npm install
    
    cd ..
    success "Frontend setup completed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p static/exports
    mkdir -p static/uploads
    mkdir -p logs
    
    # Set proper permissions
    chmod 755 static/exports
    chmod 755 static/uploads
    chmod 755 logs
    
    success "Directories created successfully"
}

# Show next steps
show_next_steps() {
    echo ""
    success "Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Start development servers: ./start.sh dev"
    echo "  2. Access the application:"
    echo "     - Frontend: http://localhost:5173"
    echo "     - Backend API: http://localhost:8000"
    echo "     - API Documentation: http://localhost:8000/docs"
    echo ""
    echo "For production deployment:"
    echo "  ./deploy.sh"
    echo ""
    echo "For more information, see the README.md file."
}

# Main installation function
main() {
    echo "SUMO Helper Installation Script"
    echo "================================"
    echo ""
    
    check_prerequisites
    create_directories
    install_backend
    install_frontend
    show_next_steps
}

# Handle script arguments
case "${1:-}" in
    "backend")
        check_prerequisites
        install_backend
        success "Backend installation completed"
        ;;
    "frontend")
        check_prerequisites
        install_frontend
        success "Frontend installation completed"
        ;;
    "help"|"-h"|"--help")
        echo "SUMO Helper Installation Script"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Install everything (default)"
        echo "  backend    Install only backend dependencies"
        echo "  frontend   Install only frontend dependencies"
        echo "  help       Show this help message"
        ;;
    "")
        main
        ;;
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 