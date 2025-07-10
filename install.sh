#!/bin/bash

# SUMO Helper - Installation Script
# This script installs and configures the complete SUMO Helper application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install SUMO based on OS
install_sumo() {
    local os=$(detect_os)
    
    print_status "Detected OS: $os"
    
    case $os in
        "linux")
            if command_exists apt-get; then
                print_status "Installing SUMO via apt-get..."
                sudo apt-get update
                sudo apt-get install -y sumo sumo-tools sumo-doc
            elif command_exists yum; then
                print_status "Installing SUMO via yum..."
                sudo yum install -y sumo sumo-tools sumo-doc
            else
                print_error "Package manager not supported. Please install SUMO manually."
                return 1
            fi
            ;;
        "macos")
            if command_exists brew; then
                print_status "Installing SUMO via Homebrew..."
                brew install sumo
            else
                print_error "Homebrew not found. Please install Homebrew first or install SUMO manually."
                return 1
            fi
            ;;
        "windows")
            print_warning "Please install SUMO manually from: https://sumo.dlr.de/docs/Downloads.php"
            print_warning "After installation, make sure SUMO is added to your PATH"
            return 1
            ;;
        *)
            print_error "Unsupported operating system"
            return 1
            ;;
    esac
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        local version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)
        
        if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
            print_success "Python $version detected"
            return 0
        else
            print_error "Python 3.8+ required, found $version"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Function to check Node.js version
check_node() {
    if command_exists node; then
        local version=$(node --version | sed 's/v//')
        local major=$(echo $version | cut -d. -f1)
        
        if [ "$major" -ge 16 ]; then
            print_success "Node.js $version detected"
            return 0
        else
            print_error "Node.js 16+ required, found $version"
            return 1
        fi
    else
        print_error "Node.js not found"
        return 1
    fi
}

# Function to check SUMO installation
check_sumo() {
    if command_exists sumo; then
        local version=$(sumo --version | head -n1)
        print_success "SUMO detected: $version"
        return 0
    else
        print_warning "SUMO not found"
        return 1
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "backend/venv" ]; then
        print_status "Creating Python virtual environment..."
        cd backend
        python3 -m venv venv
        cd ..
    fi
    
    # Activate virtual environment and install dependencies
    cd backend
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    
    print_success "Python dependencies installed"
}

# Function to install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    
    # Install monorepo dependencies
    npm install
    
    # Install frontend dependencies
    cd frontend
    npm install
    cd ..
    
    print_success "Node.js dependencies installed"
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    source venv/bin/activate
    python setup.py
    cd ..
    
    print_success "Backend setup completed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p backend/static/{maps,networks,simulations,uploads}
    mkdir -p frontend/dist
    
    print_success "Directories created"
}

# Function to create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    cat > backend/.env << EOF
# Server configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# SUMO configuration
SUMO_HOME=/usr/share/sumo
SUMO_BINARY=sumo

# File storage
UPLOAD_DIR=static/uploads
MAPS_DIR=static/maps
NETWORKS_DIR=static/networks
SIMULATIONS_DIR=static/simulations
EOF
    
    print_success "Environment file created"
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test Python backend
    cd backend
    source venv/bin/activate
    python -c "import fastapi, uvicorn, sumolib, traci, osmnx; print('✅ Backend dependencies OK')"
    cd ..
    
    # Test Node.js frontend
    cd frontend
    npm run build --silent
    cd ..
    
    print_success "Installation test completed"
}

# Main installation function
main() {
    echo "🚀 SUMO Helper - Installation Script"
    echo "====================================="
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! check_python; then
        print_error "Python 3.8+ is required"
        exit 1
    fi
    
    if ! check_node; then
        print_error "Node.js 16+ is required"
        exit 1
    fi
    
    # Check/Install SUMO
    if ! check_sumo; then
        print_status "SUMO not found. Attempting to install..."
        if ! install_sumo; then
            print_warning "SUMO installation failed. Please install manually and run this script again."
            print_warning "Installation URLs:"
            print_warning "  - Linux: sudo apt-get install sumo sumo-tools sumo-doc"
            print_warning "  - macOS: brew install sumo"
            print_warning "  - Windows: https://sumo.dlr.de/docs/Downloads.php"
        fi
    fi
    
    # Create directories
    create_directories
    
    # Install dependencies
    install_python_deps
    install_node_deps
    
    # Setup backend
    setup_backend
    
    # Create environment file
    create_env_file
    
    # Test installation
    test_installation
    
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Start the development server:"
    echo "   npm run dev"
    echo ""
    echo "2. Or start services separately:"
    echo "   Backend:  npm run dev:backend"
    echo "   Frontend: npm run dev:frontend"
    echo ""
    echo "3. Open your browser to:"
    echo "   http://localhost:5173"
    echo ""
    echo "For more information, see README.md"
}

# Run main function
main "$@" 