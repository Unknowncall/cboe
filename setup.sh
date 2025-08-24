#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Setting up CBOE Development Environment${NC}"

# Setup Python virtual environment for server
echo -e "${GREEN}🐍 Setting up Python server environment...${NC}"
cd server

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

echo -e "${YELLOW}Activating virtual environment and installing dependencies...${NC}"
source venv/bin/activate
pip install -r requirements.txt

cd ..

# Setup Node.js dependencies for client
echo -e "${GREEN}⚛️  Setting up React client environment...${NC}"
cd client
echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
npm install
cd ..

echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${GREEN}You can now run:${NC}"
echo -e "${YELLOW}  npm run dev          ${NC}# Start both servers with npm"
echo -e "${YELLOW}  ./start-dev.sh       ${NC}# Start both servers with shell script"
echo -e "${YELLOW}  npm run server       ${NC}# Start only Python server"
echo -e "${YELLOW}  npm run client       ${NC}# Start only React client"
