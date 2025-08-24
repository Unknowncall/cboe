"""
Vercel serverless function entry point for CBOE Trail Search API
"""
import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import the main app from server
def create_app():
    """Create and configure the FastAPI app for Vercel"""
    try:
        # Import after path is set
        from main import app as main_app
        return main_app
    except ImportError as e:
        # Fallback minimal app if imports fail
        app = FastAPI(title="CBOE Trail Search API", version="1.0.0")
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure properly for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/health")
        async def health():
            return {"status": "ok", "message": "API is running"}
            
        @app.get("/api/health")
        async def api_health():
            return {"status": "ok", "message": "API is running"}
        
        return app

# Create the app instance
app = create_app()

# Vercel expects a handler function
def handler(request):
    """Vercel serverless function handler"""
    return app

# For local testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
