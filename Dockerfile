# Multi-stage Docker build for CBOE full-stack application
# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/client

# Copy package files for better Docker layer caching
COPY client/package*.json ./
RUN npm ci

# Copy client source code and build
COPY client/ ./
RUN npm run build

# Stage 2: Setup Python backend and serve both frontend and backend
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV NODE_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy and install Python dependencies first (for better caching)
COPY server/requirements.txt ./server/
RUN pip install --no-cache-dir -r server/requirements.txt

# Copy server source code
COPY server/ ./server/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/client/dist ./server/static

# Copy root level files
COPY package.json trails.db ./

# Create startup script that serves frontend from FastAPI
RUN echo '#!/bin/bash\n\
cd /app/server && python main.py' > /app/start.sh && chmod +x /app/start.sh

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data

# Expose port (FastAPI will serve both backend API and frontend static files)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set working directory to app root
WORKDIR /app

# Start the application
CMD ["./start.sh"]