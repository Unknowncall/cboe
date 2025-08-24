# Vercel Deployment Guide

This guide explains how to deploy the CBOE Trail Search application to Vercel.

## Overview

The CBOE application is configured for Vercel deployment with:
- **Frontend**: React app built with Vite (served as static files)
- **Backend**: FastAPI converted to Vercel serverless functions
- **Database**: SQLite (can be upgraded to Vercel's database solutions)

## Project Structure for Vercel

```
cboe/
├── vercel.json              # Vercel configuration
├── build-vercel.sh          # Build preparation script
├── client/                  # React frontend
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
├── api/                     # Vercel serverless functions
│   ├── health.py           # Health check endpoint
│   ├── search.py           # Trail search endpoint
│   ├── index.py            # Main API handler
│   └── requirements.txt    # Python dependencies
└── server/                  # Original FastAPI code (referenced by API)
```

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to GitHub
3. **OpenAI API Key**: Required for AI features

## Method 1: Deploy via Vercel Dashboard (Recommended)

### Step 1: Connect Repository

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Select the `cboe` repository

### Step 2: Configure Project

Vercel should automatically detect the configuration from `vercel.json`. If not:

- **Framework Preset**: Vite
- **Root Directory**: `.` (leave empty)
- **Build Command**: `cd client && npm run build`
- **Output Directory**: `client/dist`
- **Install Command**: `cd client && npm install`

### Step 3: Set Environment Variables

In the Vercel dashboard, add these environment variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=500
DATABASE_URL=memory://
LOG_LEVEL=INFO
```

### Step 4: Deploy

Click "Deploy" and wait for the build to complete.

## Method 2: Deploy via Vercel CLI

### Step 1: Install Vercel CLI

```bash
npm i -g vercel
```

### Step 2: Prepare Build

```bash
# Run the build preparation script
./build-vercel.sh
```

### Step 3: Login and Deploy

```bash
# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

### Step 4: Set Environment Variables

```bash
# Set environment variables via CLI
vercel env add OPENAI_API_KEY production
vercel env add OPENAI_MODEL production
vercel env add OPENAI_MAX_TOKENS production
```

## Configuration Details

### vercel.json Explanation

```json
{
  "version": 2,
  "builds": [
    {
      "src": "client/package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "dist" }
    },
    {
      "src": "api/**/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    { "src": "/api/health", "dest": "/api/health.py" },
    { "src": "/api/search", "dest": "/api/search.py" },
    { "src": "/api/(.*)", "dest": "/api/index.py" },
    { "src": "/(.*)", "dest": "/client/dist/index.html" }
  ]
}
```

### API Endpoints

After deployment, your API will be available at:

- **Health Check**: `https://your-app.vercel.app/api/health`
- **Trail Search**: `https://your-app.vercel.app/api/search`
- **Main App**: `https://your-app.vercel.app/`

## Environment Variables

Set these in the Vercel dashboard under Settings > Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-...` |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` |
| `OPENAI_MAX_TOKENS` | Maximum tokens per request | `500` |
| `DATABASE_URL` | Database connection (for SQLite use `memory://`) | `memory://` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Database Considerations

### Current Setup (SQLite)
- The current SQLite database won't persist on Vercel
- Data will be lost between deployments
- Good for testing and development

### Production Recommendations

1. **Vercel KV** (Redis-compatible):
   ```bash
   vercel env add KV_URL production
   ```

2. **Vercel Postgres**:
   ```bash
   vercel env add POSTGRES_URL production
   ```

3. **External Database**:
   - Supabase
   - PlanetScale
   - Railway
   - MongoDB Atlas

## Custom Domain

1. Go to Vercel Dashboard > Your Project > Settings > Domains
2. Add your custom domain
3. Update DNS records as instructed
4. SSL certificate is automatically provided

## Monitoring and Logs

### View Logs
```bash
# View function logs
vercel logs

# View logs for specific deployment
vercel logs [deployment-url]
```

### Analytics
- Vercel provides built-in analytics
- View in Dashboard > Your Project > Analytics

## Troubleshooting

### Build Failures

1. **Client Build Issues**:
   ```bash
   # Test locally
   cd client && npm run build
   ```

2. **API Function Issues**:
   - Check Python version compatibility (3.11)
   - Verify all dependencies in `api/requirements.txt`
   - Test functions locally

### Environment Variable Issues

```bash
# List all environment variables
vercel env ls

# Remove and re-add problematic variables
vercel env rm OPENAI_API_KEY production
vercel env add OPENAI_API_KEY production
```

### Route Issues

- Check `vercel.json` routes configuration
- Ensure API endpoints match function names
- Verify static file routing

### Database Issues

For persistent storage, consider upgrading to:

```bash
# Add Vercel Postgres
vercel env add POSTGRES_URL production

# Or add external database
vercel env add DATABASE_URL production
```

## Performance Optimization

### Frontend
- Vite automatically optimizes the React build
- Assets are automatically CDN-cached by Vercel

### Backend
- Serverless functions auto-scale
- Cold start optimization through smaller bundle sizes
- Consider upgrading to Vercel Pro for better performance

## Security

### Environment Variables
- Never commit secrets to code
- Use Vercel's encrypted environment variables
- Rotate API keys regularly

### CORS Configuration
- Update CORS settings in `api/search.py` for production
- Restrict origins to your domain

### Rate Limiting
- Consider adding rate limiting for API endpoints
- Use Vercel's Edge Functions for advanced middleware

## Cost Considerations

### Vercel Free Tier Limits
- 100GB bandwidth per month
- 1000 serverless function invocations per day
- 10 deployments per day

### Upgrade to Pro
- Consider Pro plan for production apps
- Better performance and higher limits
- Custom domains and team collaboration

## Continuous Deployment

### Automatic Deployments
- Push to `main` branch triggers production deployment
- Push to other branches creates preview deployments
- Pull requests get automatic preview URLs

### Manual Control
```bash
# Deploy specific branch
vercel --prod --confirm

# Create preview deployment
vercel
```

## Next Steps

1. **Test the deployment** thoroughly
2. **Set up monitoring** and error tracking
3. **Configure custom domain** if needed
4. **Upgrade database** for production data persistence
5. **Set up CI/CD** for automated testing before deployment

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)
- [FastAPI on Vercel Guide](https://vercel.com/guides/deploying-fastapi-with-vercel)
