# CBOE Vercel Deployment - Quick Start

## 🚀 Quick Deployment Steps

### Option 1: Vercel Dashboard (Easiest)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Vercel configuration"
   git push origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

3. **Set Environment Variables** in Vercel Dashboard:
   ```
   OPENAI_API_KEY=your_key_here
   OPENAI_MODEL=gpt-4
   OPENAI_MAX_TOKENS=500
   DATABASE_URL=memory://
   LOG_LEVEL=INFO
   ```

4. **Deploy**: Click Deploy!

### Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Prepare build
./build-vercel.sh

# Login and deploy
vercel login
vercel --prod
```

## 📁 What Was Added

- `vercel.json` - Vercel configuration
- `api/` - Serverless functions directory
- `build-vercel.sh` - Build preparation script
- `VERCEL.md` - Complete deployment guide
- `.vercelignore` - Deployment optimization
- `.github/workflows/` - CI/CD automation

## 🌐 Your App Structure on Vercel

- **Frontend**: React app at `https://your-app.vercel.app/`
- **API Health**: `https://your-app.vercel.app/api/health`
- **API Search**: `https://your-app.vercel.app/api/search`

## ⚠️ Important Notes

1. **Database**: SQLite won't persist on Vercel. For production, consider:
   - Vercel Postgres
   - Supabase
   - PlanetScale

2. **Environment Variables**: Must be set in Vercel Dashboard

3. **CORS**: Update in production for your domain

## 📖 Full Documentation

See `VERCEL.md` for complete deployment guide with troubleshooting, monitoring, and production tips.
