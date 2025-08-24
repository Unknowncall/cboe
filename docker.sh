#!/bin/bash

# CBOE Docker Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f "server/.env" ]; then
        print_warning ".env file not found in server directory"
        if [ -f "server/.env.example" ]; then
            print_status "Copying .env.example to .env"
            cp server/.env.example server/.env
            print_warning "Please edit server/.env with your actual configuration values"
        else
            print_error "No .env.example found. Please create server/.env manually"
            exit 1
        fi
    fi
}

# Build the Docker image
build() {
    print_status "Building CBOE Docker image..."
    docker build -t cboe-app .
    print_status "Build completed successfully!"
}

# Run the container
run() {
    print_status "Starting CBOE container..."
    docker run -d \
        --name cboe-app \
        -p 8000:8000 \
        --env-file server/.env \
        cboe-app
    print_status "Container started successfully!"
    print_status "Application available at: http://localhost:8000"
}

# Stop and remove container
stop() {
    print_status "Stopping CBOE container..."
    docker stop cboe-app 2>/dev/null || true
    docker rm cboe-app 2>/dev/null || true
    print_status "Container stopped and removed!"
}

# Run with docker-compose
compose_up() {
    print_status "Starting with Docker Compose..."
    docker-compose up -d
    print_status "Services started successfully!"
    print_status "Application available at: http://localhost:8000"
}

# Stop docker-compose services
compose_down() {
    print_status "Stopping Docker Compose services..."
    docker-compose down
    print_status "Services stopped!"
}

# Show logs
logs() {
    if [ "$2" = "compose" ]; then
        docker-compose logs -f
    else
        docker logs -f cboe-app
    fi
}

# Development mode with docker-compose
dev() {
    print_status "Starting development environment..."
    docker-compose --profile development up -d
    print_status "Development environment started!"
    print_status "Frontend: http://localhost:3000"
    print_status "Backend: http://localhost:8001"
}

# Show help
show_help() {
    echo "CBOE Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build           Build the Docker image"
    echo "  run             Run the container (single container)"
    echo "  stop            Stop and remove the container"
    echo "  up              Start with Docker Compose"
    echo "  down            Stop Docker Compose services"
    echo "  dev             Start development environment"
    echo "  logs [compose]  Show container logs"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build && $0 run    # Build and run single container"
    echo "  $0 up                 # Start with Docker Compose"
    echo "  $0 dev                # Start development environment"
    echo "  $0 logs               # Show container logs"
    echo "  $0 logs compose       # Show Docker Compose logs"
}

# Main script logic
case "$1" in
    build)
        check_env_file
        build
        ;;
    run)
        check_env_file
        stop  # Stop any existing container
        run
        ;;
    stop)
        stop
        ;;
    up)
        check_env_file
        compose_up
        ;;
    down)
        compose_down
        ;;
    dev)
        check_env_file
        dev
        ;;
    logs)
        logs "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        print_error "No command specified"
        show_help
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
