# Docker Deployment Guide

This document explains how to deploy the CBOE Trail Search application using Docker.

## Overview

The application uses a multi-stage Docker build that:
1. Builds the React frontend in a Node.js environment
2. Sets up a Python environment with FastAPI backend
3. Serves both frontend and backend from a single container

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)
- OpenAI API key (required for AI features)

## Quick Start

### Method 1: Using the Docker Management Script (Recommended)

```bash
# Make the script executable (already done)
chmod +x docker.sh

# Build and run the application
./docker.sh build
./docker.sh run

# Or use Docker Compose (recommended)
./docker.sh up
```

### Method 2: Manual Docker Commands

```bash
# Build the image
docker build -t cboe-app .

# Run the container
docker run -d \
  --name cboe-app \
  -p 8000:8000 \
  --env-file server/.env \
  cboe-app
```

### Method 3: Docker Compose

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down
```

## Configuration

### Environment Variables

Create a `server/.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=500
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:8000
DATABASE_URL=trails.db
LOG_LEVEL=INFO
```

### Docker Environment Variables

You can also set environment variables when running Docker:

```bash
docker run -d \
  --name cboe-app \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -e OPENAI_MODEL=gpt-4 \
  cboe-app
```

## Access Points

Once running, the application will be available at:

- **Main Application**: http://localhost:8000

## Docker Management Script Commands

The `docker.sh` script provides convenient commands:

```bash
./docker.sh build          # Build the Docker image
./docker.sh run            # Run single container
./docker.sh stop           # Stop and remove container
./docker.sh up             # Start with Docker Compose
./docker.sh down           # Stop Docker Compose services
./docker.sh dev            # Start development environment
./docker.sh logs           # Show container logs
./docker.sh logs compose   # Show Docker Compose logs
./docker.sh help           # Show help message
```

## Development Mode

For development with hot-reload:

```bash
# Start development environment
./docker.sh dev

# This will start:
# - Frontend with hot-reload at http://localhost:3000
# - Backend with auto-reload at http://localhost:8001
```

## Persistent Data

The Docker setup includes volume mounts for:

- **Database**: `./trails.db:/app/server/trails.db`
- **Logs**: `./logs:/app/logs`

This ensures your data persists between container restarts.

## Troubleshooting

### Container won't start
```bash
# Check logs
./docker.sh logs

# Or for Docker Compose
./docker.sh logs compose
```

### Environment issues
```bash
# Verify .env file exists
ls -la server/.env

# Check environment variables in container
docker exec cboe-app env | grep OPENAI
```

### Build issues
```bash
# Clean rebuild
docker system prune
./docker.sh build
```

### Port conflicts
```bash
# Check what's using port 8000
lsof -i :8000

# Use different port
docker run -p 8080:8000 cboe-app
```

## Production Deployment

For production deployment, consider:

1. **Security**: Remove development dependencies and debug modes
2. **Environment**: Use production environment variables
3. **Reverse Proxy**: Use nginx or similar for SSL/TLS termination
4. **Monitoring**: Add proper logging and monitoring
5. **Backup**: Implement database backup strategies

### Production Docker Compose

```yaml
version: '3.8'
services:
  cboe-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - LOG_LEVEL=WARNING
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Performance Optimization

The Docker image is optimized with:

- Multi-stage builds to reduce final image size
- Layer caching for faster rebuilds
- Minimal base images (Alpine Linux for Node, slim Python)
- Only production dependencies in final image

## Security Considerations

- Environment variables are not exposed in the image
- Request size limits are enforced
- CORS is properly configured
- No unnecessary ports are exposed
- Non-root user execution (can be added if needed)

## Monitoring and Logging

Access logs:
```bash
# Application logs
./docker.sh logs

# Follow logs in real-time
docker logs -f cboe-app

# Specific service logs with Docker Compose
docker-compose logs cboe-app
```
