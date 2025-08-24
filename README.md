# CBOE AI-Powered Trail Search Application

An intelligent trail search application that uses AI agents to understand natural language queries and provide personalized trail recommendations. Built with Python FastAPI backend featuring multiple AI agents (custom OpenAI and LangChain) and a modern React + TypeScript frontend.

## 🌲 What This Application Does

This application helps users find hiking trails through natural language search queries. Users can ask questions like:
- "Find me easy trails near Chicago for families with dogs"
- "I want a challenging 5+ mile hike with great views"
- "Show me moderate trails within 30 miles that allow pets"

The AI agents understand context, extract search criteria, and provide intelligent recommendations with explanations.

## 🏗️ Project Architecture

```
cboe/
├── server/                 # Python FastAPI backend with AI agents
│   ├── main.py            # FastAPI application and API routes
│   ├── config.py          # Configuration and environment settings
│   ├── models.py          # Pydantic models for API validation
│   ├── database.py        # SQLite database operations with FTS5 search
│   ├── search.py          # Search logic and filter parsing
│   ├── agent_factory.py   # AI agent management and instantiation
│   ├── utils.py           # Utility functions and performance monitoring
│   ├── agents/            # AI agent implementations
│   │   ├── custom_agent.py    # Direct OpenAI API integration
│   │   └── langchain_agent.py # LangChain-based implementation
│   ├── trails.db          # SQLite database with Chicago-area trails
│   └── requirements.txt   # Python dependencies
├── client/                # React frontend with streaming interface
│   ├── src/
│   │   ├── components/    # React components for search and results
│   │   ├── hooks/        # Custom hooks for API integration
│   │   ├── types/        # TypeScript type definitions
│   │   └── App.tsx       # Main application component
│   └── package.json      # Node.js dependencies
├── docker-compose.yml     # Docker orchestration
├── Dockerfile            # Multi-stage Docker build
├── docker.sh            # Docker management script
└── package.json         # Root scripts for development
```

## 🚀 Quick Start Guide

### Prerequisites

1. **OpenAI API Key** (required for AI features)
2. **Node.js 18+** and **Python 3.11+**
3. **Docker** (optional, for containerized deployment)

### Option 1: Development Setup (Recommended)

```bash
# 1. Clone and navigate to project
cd cboe

# 2. Create environment file
cp server/.env.example server/.env
# Edit server/.env and add your OpenAI API key

# 3. Install all dependencies
npm run install:all

# 4. Start both servers in development mode
npm run dev
```

### Option 2: Docker Deployment

```bash
# 1. Setup environment
cp server/.env.example server/.env
# Edit server/.env with your configuration

# 2. Build and run with Docker
./docker.sh build
./docker.sh run

# Or use Docker Compose
./docker.sh up
```

### Option 3: Manual Setup

```bash
# Backend setup
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Frontend setup
cd client
npm install
cd ..

# Run servers (separate terminals)
npm run server  # Terminal 1: Backend on port 8000
npm run client  # Terminal 2: Frontend on port 5173
```

## 🌐 Application Access Points

- **Main Application**: http://localhost:5173 (development) or http://localhost:8000 (production/Docker)
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **API Health Check**: http://localhost:8000/api/health
- **Alternative API Docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Application welcome and status
- `GET /api/health` - Health check with database connectivity
- `POST /api/chat` - AI-powered streaming trail search
- `GET /api/agents` - Available AI agent types
- `GET /api/trail/{id}` - Detailed trail information

### Development & Debug Endpoints
- `POST /api/debug/parse` - Test text parsing without AI
- `POST /api/seed` - Re-seed database with trail data

### Example API Usage

```bash
# Search for trails using AI agent
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me easy trails near Chicago with dogs allowed",
    "agent_type": "custom"
  }'

# Get detailed trail information
curl "http://localhost:8000/api/trail/1"

# Check application health
curl "http://localhost:8000/api/health"
```

## 🤖 AI Agent System

### Available Agents

1. **Custom Agent** (`custom`) - Direct OpenAI API integration
   - Uses function calling for structured responses
   - Optimized for trail search use cases
   - Faster response times

2. **LangChain Agent** (`langchain`) - LangChain framework integration
   - Advanced reasoning capabilities
   - Extensible tool system
   - More complex query handling

### Agent Configuration

Edit `server/.env` to configure AI behavior:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=500
```

## 🛠️ Available Scripts

### Root Directory Scripts
- `npm run dev` - Start both servers with hot-reload
- `npm run server` - Start only the Python backend
- `npm run client` - Start only the React frontend  
- `npm run install:all` - Install all dependencies
- `npm run install:server` - Install Python dependencies only
- `npm run install:client` - Install Node.js dependencies only
- `npm run build:client` - Build React app for production
- `npm run start:prod` - Start both servers in production mode

### Docker Scripts
- `./docker.sh build` - Build Docker image
- `./docker.sh run` - Run container
- `./docker.sh up` - Start with Docker Compose
- `./docker.sh down` - Stop Docker Compose services
- `./docker.sh logs` - View container logs

## 🎨 Technology Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **OpenAI API** - GPT-4 for natural language processing
- **LangChain** - AI agent framework and tooling
- **SQLite + FTS5** - Full-text search database
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server with WebSocket support

### Frontend
- **React 18** - Component-based UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern accessible UI components
- **Lucide Icons** - Beautiful icon library

### Infrastructure
- **Docker** - Containerization with multi-stage builds
- **SQLite** - Embedded database with FTS5 search
- **Streaming API** - Real-time response streaming
- **CORS** - Cross-origin resource sharing

## 🔧 Development Guide

### Environment Configuration

Required environment variables in `server/.env`:

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=500

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Database Configuration
DATABASE_URL=trails.db

# Performance Configuration
WORDS_PER_CHUNK=3
STREAM_DELAY_MS=80
MAX_REQUEST_SIZE_BYTES=1024
DB_POOL_SIZE=5

# Logging Configuration
LOG_LEVEL=INFO
```

### Adding New Trail Data

The application includes a seeded database of Chicago-area trails. To add more trails:

1. Edit `server/database.py` in the `seed_trails()` function
2. Restart the server or call `POST /api/seed` to refresh data

### Extending AI Agents

To create new AI agents:

1. Create a new agent class in `server/agents/`
2. Register it in `server/agent_factory.py`
3. Add the agent type to the frontend selector

### Frontend Development

The React frontend features:
- Real-time streaming responses
- Agent type selection
- Tool trace visualization
- Responsive trail cards
- Error boundaries

Key components:
- `SearchForm` - Query input and agent selection
- `StreamingPanel` - Real-time AI response display
- `TrailList` - Search results with trail cards
- `ToolTrace` - Performance and debugging information

## 🚀 Deployment Options

### Production Deployment

1. **Docker (Recommended)**:
   ```bash
   ./docker.sh build
   ./docker.sh run
   ```

2. **Manual Production Setup**:
   ```bash
   # Build frontend
   cd client && npm run build
   
   # Deploy backend with static files
   cd server
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Environment Considerations

- Set `LOG_LEVEL=WARNING` in production
- Use reverse proxy (nginx) for SSL/TLS
- Implement database backups for trail data
- Monitor OpenAI API usage and costs
- Configure proper CORS origins for your domain

## 🔍 Example Interactions

### Natural Language Queries

The AI agents can understand and respond to various query types:

**Basic Search**:
- "Find trails near Chicago"
- "Show me hiking trails"

**Filtered Search**:
- "Easy trails under 3 miles with dogs allowed"
- "Challenging hikes with elevation gain over 500 feet"
- "Family-friendly loops within 20 miles of downtown"

**Contextual Search**:
- "I want a moderate trail for a weekend hike with my kids"
- "Find a scenic trail where I can bring my dog and get good exercise"
- "Show me trails similar to the lakefront path but more challenging"

### Response Format

The AI agents provide:
- **Streaming responses** with real-time feedback
- **Trail recommendations** with explanations
- **Parsed filters** showing understood criteria
- **Tool traces** for performance monitoring
- **Why explanations** for each recommended trail

## 📊 Monitoring and Debugging

### Logging Features

- **Structured JSON logs** for analysis
- **Request ID tracking** across components
- **Performance timing** for all operations
- **Tool traces** for AI agent debugging
- **Database operation monitoring**

### Log Files

- `server/trail_search.log` - Application logs
- Console output during development
- Docker logs via `./docker.sh logs`

### Performance Monitoring

The application includes built-in performance monitoring:
- Database query timing
- AI agent response times
- Search operation metrics
- Memory and connection usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the logs: `./docker.sh logs` or `server/trail_search.log`
2. Verify environment configuration in `server/.env`
3. Test with the health endpoint: `GET /api/health`
4. Review the API documentation at `/docs`
