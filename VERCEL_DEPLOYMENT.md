# CBOE Trail Search - Vercel Deployment

This project is now configured for deployment on Vercel with serverless functions.

## Architecture

- **Frontend**: React + Vite (deployed as static site)
- **Backend**: Python serverless functions in `/api` directory
- **Database**: SQLite database file included in deployment

## Deployment on Vercel

### Prerequisites

1. Vercel account
2. OpenAI API key

### Environment Variables

Set the following environment variables in your Vercel dashboard:

```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
LOG_LEVEL=INFO
CORS_ORIGINS=https://*.vercel.app
```

### Deploy Steps

1. **Connect Repository**: Link your GitHub repository to Vercel
2. **Environment Variables**: Set the required environment variables in Vercel dashboard
3. **Deploy**: Vercel will automatically build and deploy

The `vercel.json` configuration handles:
- Building the React frontend
- Setting up Python serverless functions
- Routing API requests to appropriate functions
- Serving the frontend as a static site

### API Endpoints

The following serverless functions are available:

- `GET /api/health` - Health check
- `GET /api/agents` - Get available AI agents
- `POST /api/chat` - Trail search (non-streaming for serverless)
- `GET /api/trail/[id]` - Get trail details

### Local Development

For local development, you can still use the original Docker setup:

```bash
# Build and run with Docker
./docker.sh up

# Or run separately
npm run dev
```

### Key Changes for Vercel

1. **Non-streaming Chat**: The chat endpoint now returns complete responses instead of streaming
2. **Serverless Functions**: Each API endpoint is a separate Python function
3. **Static Database**: SQLite database is included as a static file
4. **CORS Configuration**: Properly configured for Vercel domains

### File Structure

```
/
├── api/                    # Vercel serverless functions
│   ├── agents.py          # Get available agents
│   ├── chat.py            # Trail search
│   ├── health.py          # Health check
│   ├── trail/[trailId].py # Trail details
│   ├── trails.db          # SQLite database
│   └── [shared modules]   # Copied from server/
├── client/                # React frontend
│   └── dist/              # Built frontend (generated)
├── vercel.json            # Vercel configuration
└── requirements.txt       # Python dependencies
```

This configuration provides a scalable, serverless deployment while maintaining the core functionality of the trail search application.