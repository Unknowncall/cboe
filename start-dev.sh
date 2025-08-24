#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting CBOE Development Servers${NC}"

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    jobs -p | xargs kill 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Check if server dependencies are installed
if [ ! -f "server/venv/bin/activate" ] && [ ! -f "server/.venv/bin/activate" ]; then
    echo -e "${YELLOW}⚠️  Python virtual environment not found. Please set up your Python environment first.${NC}"
    echo -e "${YELLOW}You can run: python -m venv server/venv && source server/venv/bin/activate && pip install -r server/requirements.txt${NC}"
fi

# Check if client dependencies are installed
if [ ! -d "client/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Client dependencies not found. Installing...${NC}"
    cd client && npm install && cd ..
fi

echo -e "${GREEN}🐍 Starting Python FastAPI server...${NC}"
cd server
python main.py &
SERVER_PID=$!
cd ..

# Wait a moment for server to start
sleep 2

echo -e "${GREEN}⚛️  Starting React development server...${NC}"
cd client
npm run dev &
CLIENT_PID=$!
cd ..

echo -e "${GREEN}✅ Both servers are starting up!${NC}"
echo -e "${GREEN}📡 Python API: http://localhost:8000${NC}"
echo -e "${GREEN}🌐 React App: http://localhost:5173${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Wait for both processes
wait
