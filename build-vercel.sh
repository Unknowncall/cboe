#!/bin/bash

# CBOE Vercel Deployment Build Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[CBOE VERCEL BUILD]${NC} $1"
}

print_header "Starting Vercel deployment preparation..."

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    print_error "vercel.json not found. Please run this script from the project root."
    exit 1
fi

# Install client dependencies
print_status "Installing client dependencies..."
cd client
npm install
print_status "Client dependencies installed successfully!"

# Build the React app
print_status "Building React application..."
npm run build
print_status "React application built successfully!"

# Go back to root
cd ..

# Check if API directory exists
if [ ! -d "api" ]; then
    print_error "API directory not found. Please ensure API serverless functions are set up."
    exit 1
fi

# Verify environment variables setup
print_status "Checking environment setup..."
if [ ! -f "server/.env.example" ]; then
    print_warning "No .env.example found. Make sure to set environment variables in Vercel dashboard."
else
    print_status "Environment example file found. Remember to set these in Vercel:"
    echo "  - OPENAI_API_KEY"
    echo "  - OPENAI_MODEL"
    echo "  - OPENAI_MAX_TOKENS"
    echo "  - DATABASE_URL"
    echo "  - LOG_LEVEL"
fi

print_status "Build preparation complete!"
echo ""
print_header "Next steps for Vercel deployment:"
echo "1. Install Vercel CLI: npm i -g vercel"
echo "2. Login to Vercel: vercel login"
echo "3. Deploy: vercel --prod"
echo ""
echo "Or connect your GitHub repository to Vercel dashboard for automatic deployments."
echo ""
print_status "Remember to set environment variables in Vercel dashboard!"

exit 0
