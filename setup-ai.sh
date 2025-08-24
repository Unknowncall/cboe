#!/bin/bash

# CBOE Trail Search - Setup Script
# This script sets up the development environment for the AI-powered trail search application

set -e  # Exit on any error

echo "🏔️  CBOE Trail Search - Setup Script"
echo "=================================="

# Check if we're in the right directory
if [[ ! -f "package.json" ]] || [[ ! -d "server" ]] || [[ ! -d "client" ]]; then
    echo "❌ Error: Please run this script from the root of the cboe project directory"
    exit 1
fi

echo "📁 Setting up backend environment..."

# Setup Python environment for server
cd server

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    echo "🔧 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Please edit server/.env and add your OpenAI API key"
    echo "   Get your API key from: https://platform.openai.com/api-keys"
    echo "   Set OPENAI_API_KEY=your_actual_api_key"
else
    echo "✅ .env file already exists"
fi

cd ..

echo "📁 Setting up frontend environment..."

# Setup Node.js environment for client
cd client

# Check if Node.js is available
if ! command -v npm &> /dev/null; then
    echo "❌ Error: Node.js and npm are required but not installed"
    echo "   Install from: https://nodejs.org/"
    exit 1
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "   1. Make sure you've added your OpenAI API key to server/.env"
echo "   2. Run: ./start-dev.sh"
echo ""
echo "📚 For more information, see README.md"
