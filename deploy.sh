#!/bin/bash

# SUMO Helper Production Deployment Script
# This script automates the deployment of SUMO Helper in production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="sumo-helper"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if the docker-compose.yml file exists
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        error "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
    fi
    
    success "Prerequisites check passed"
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

# Load environment variables
load_environment() {
    log "Loading environment variables..."
    
    if [ -f "$ENV_FILE" ]; then
        export $(cat $ENV_FILE | grep -v '^#' | xargs)
        success "Environment variables loaded from $ENV_FILE"
    else
        warning "No .env file found. Using default environment variables."
    fi
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    
    docker-compose build --no-cache
    
    if [ $? -eq 0 ]; then
        success "Docker images built successfully"
    else
        error "Failed to build Docker images"
    fi
}

# Stop existing containers
stop_containers() {
    log "Stopping existing containers..."
    
    docker-compose down --remove-orphans
    
    success "Existing containers stopped"
}

# Start services
start_services() {
    log "Starting services..."
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        success "Services started successfully"
    else
        error "Failed to start services"
    fi
}

# Wait for services to be healthy
wait_for_health() {
    log "Waiting for services to be healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps | grep -q "healthy"; then
            success "All services are healthy"
            return 0
        fi
        
        log "Waiting for services to be healthy... (attempt $attempt/$max_attempts)"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    warning "Some services may not be healthy. Check with 'docker-compose ps'"
}

# Show service status
show_status() {
    log "Service status:"
    docker-compose ps
    
    echo ""
    log "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Health Check: http://localhost:8000/health"
}

# Show logs
show_logs() {
    log "Recent logs:"
    docker-compose logs --tail=20
}

# Backup function
backup_data() {
    log "Creating backup of existing data..."
    
    local backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    if [ -d "static/exports" ]; then
        cp -r static/exports "$backup_dir/"
    fi
    
    if [ -d "static/uploads" ]; then
        cp -r static/uploads "$backup_dir/"
    fi
    
    success "Backup created in $backup_dir"
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    
    # Remove unused Docker images
    docker image prune -f
    
    # Remove unused Docker volumes
    docker volume prune -f
    
    success "Cleanup completed"
}

# Main deployment function
deploy() {
    log "Starting SUMO Helper deployment..."
    
    check_prerequisites
    create_directories
    load_environment
    backup_data
    stop_containers
    build_images
    start_services
    wait_for_health
    cleanup
    
    success "Deployment completed successfully!"
    echo ""
    show_status
    echo ""
    log "To view logs, run: docker-compose logs -f"
    log "To stop services, run: docker-compose down"
}

# Rollback function
rollback() {
    log "Rolling back deployment..."
    
    docker-compose down
    docker-compose up -d --force-recreate
    
    success "Rollback completed"
}

# Usage function
usage() {
    echo "SUMO Helper Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     Deploy the application (default)"
    echo "  rollback   Rollback to previous version"
    echo "  status     Show service status"
    echo "  logs       Show recent logs"
    echo "  stop       Stop all services"
    echo "  start      Start all services"
    echo "  restart    Restart all services"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 status"
    echo "  $0 logs"
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    stop)
        docker-compose down
        success "Services stopped"
        ;;
    start)
        docker-compose up -d
        success "Services started"
        ;;
    restart)
        docker-compose restart
        success "Services restarted"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        error "Unknown command: $1"
        usage
        exit 1
        ;;
esac 