"""
Health check endpoint for Vercel
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import os

# Add server path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

app = FastAPI()

@app.get("/")
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "ok", 
        "message": "CBOE Trail Search API is running on Vercel",
        "version": "1.0.0"
    })

# For Vercel
def handler(request):
    return app
