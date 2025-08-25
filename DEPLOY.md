# Quick Start Guide for Vercel Deployment

## Deploy to Vercel in 3 Steps

### 1. Connect Repository
Click the "Deploy" button or connect your GitHub repository to Vercel:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Unknowncall/cboe)

### 2. Set Environment Variables
In your Vercel dashboard, add these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API key (required) |
| `OPENAI_MODEL` | `gpt-4` | OpenAI model to use |
| `LOG_LEVEL` | `INFO` | Logging level |

### 3. Deploy
Vercel will automatically:
- Build the React frontend
- Set up Python serverless functions
- Deploy your application

## What's Included

✅ **React Frontend** - Built with Vite and deployed as static site  
✅ **Python API** - Serverless functions for trail search  
✅ **Database** - SQLite with 70+ trails pre-loaded  
✅ **AI Integration** - OpenAI-powered trail recommendations  
✅ **CORS Configuration** - Properly configured for Vercel domains  

## API Endpoints

After deployment, your API will be available at:

- `GET /api/health` - Health check
- `GET /api/agents` - Available AI agents
- `POST /api/chat` - Trail search
- `GET /api/trail/[id]` - Trail details

## Key Features

- **Serverless Architecture** - Scales automatically with Vercel
- **Non-streaming Responses** - Optimized for serverless functions
- **Static Database** - No external database required
- **Mobile Responsive** - Works on all devices

## Development

For local development:

```bash
# Install dependencies
npm run install:all

# Run development server
npm run dev
```

## Troubleshooting

**Build Failures**: Ensure all environment variables are set in Vercel dashboard

**API Errors**: Check that OPENAI_API_KEY is properly configured

**CORS Issues**: Verify your domain is included in CORS_ORIGINS