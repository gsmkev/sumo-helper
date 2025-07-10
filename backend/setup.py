#!/usr/bin/env python3
"""
Setup script for SUMO Helper Backend
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_sumo_installation():
    """Check if SUMO is installed"""
    try:
        result = subprocess.run(['sumo', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ SUMO is installed")
            return True
        else:
            print("❌ SUMO is not properly installed")
            return False
    except FileNotFoundError:
        print("❌ SUMO is not installed")
        print("Please install SUMO from: https://sumo.dlr.de/docs/Downloads.php")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "static",
        "static/maps",
        "static/networks", 
        "static/simulations",
        "static/uploads"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def main():
    print("🚀 Setting up SUMO Helper Backend...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check SUMO installation
    if not check_sumo_installation():
        print("\n⚠️  Please install SUMO before continuing")
        print("Ubuntu/Debian: sudo apt-get install sumo sumo-tools sumo-doc")
        print("macOS: brew install sumo")
        print("Windows: Download from https://sumo.dlr.de/docs/Downloads.php")
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_dependencies()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nTo start the backend server:")
    print("  python -m uvicorn main:app --reload --port 8000")
    print("\nTo start the frontend:")
    print("  cd ../frontend && npm run dev")

if __name__ == "__main__":
    main() 