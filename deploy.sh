#!/bin/bash

# SUMO Helper Production Deployment Script
# This script automates the deployment process for production environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="sumo-helper"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Generate environment file
generate_env_file() {
    log_info "Generating environment file..."
    
    if [[ ! -f "$ENV_FILE" ]]; then
        cat > "$ENV_FILE" << EOF
# SUMO Helper Production Environment Variables
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
SUMO_HOME=/opt/sumo
OSM_TIMEOUT=30
OSM_MAX_AREA_SIZE=0.01
DEFAULT_SIMULATION_TIME=3600
MAX_SIMULATION_TIME=7200
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
EOF
        log_success "Environment file created: $ENV_FILE"
    else
        log_warning "Environment file already exists: $ENV_FILE"
    fi
}

# Build and start services
deploy_services() {
    log_info "Deploying services..."
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose down --remove-orphans
    
    # Build images
    log_info "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    log_info "Starting services..."
    docker-compose up -d
    
    log_success "Services deployed successfully"
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for backend
    log_info "Waiting for backend service..."
    timeout=60
    while [[ $timeout -gt 0 ]]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_success "Backend service is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [[ $timeout -eq 0 ]]; then
        log_error "Backend service failed to start within 60 seconds"
        exit 1
    fi
    
    # Wait for frontend
    log_info "Waiting for frontend service..."
    timeout=60
    while [[ $timeout -gt 0 ]]; do
        if curl -f http://localhost:3000 &> /dev/null; then
            log_success "Frontend service is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [[ $timeout -eq 0 ]]; then
        log_error "Frontend service failed to start within 60 seconds"
        exit 1
    fi
}

# Show deployment status
show_status() {
    log_info "Deployment status:"
    echo
    
    # Show running containers
    log_info "Running containers:"
    docker-compose ps
    echo
    
    # Show service URLs
    log_info "Service URLs:"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/health"
    echo
    
    # Show logs
    log_info "Recent logs:"
    docker-compose logs --tail=10
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    docker-compose down --remove-orphans
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    log_info "Starting SUMO Helper production deployment..."
    echo
    
    # Check if not running as root
    check_root
    
    # Check prerequisites
    check_prerequisites
    
    # Generate environment file
    generate_env_file
    
    # Deploy services
    deploy_services
    
    # Wait for services
    wait_for_services
    
    # Show status
    show_status
    
    log_success "Deployment completed successfully!"
    echo
    log_info "You can now access the application at:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo
    log_info "To view logs: docker-compose logs -f"
    log_info "To stop services: docker-compose down"
}

# Handle script arguments
case "${1:-}" in
    "cleanup")
        cleanup
        ;;
    "status")
        show_status
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "restart")
        log_info "Restarting services..."
        docker-compose restart
        wait_for_services
        show_status
        ;;
    "update")
        log_info "Updating services..."
        docker-compose pull
        deploy_services
        wait_for_services
        show_status
        ;;
    "help"|"-h"|"--help")
        echo "SUMO Helper Deployment Script"
        echo
        echo "Usage: $0 [COMMAND]"
        echo
        echo "Commands:"
        echo "  (no args)  Deploy the application"
        echo "  cleanup    Stop and remove all containers"
        echo "  status     Show deployment status"
        echo "  logs       Show service logs"
        echo "  restart    Restart all services"
        echo "  update     Update and redeploy services"
        echo "  help       Show this help message"
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 