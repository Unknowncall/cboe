"""
Trail search endpoint for Vercel
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import json
import asyncio
from datetime import datetime

# Add server path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from models import ChatRequest, ChatResponse, ErrorResponse
    from config import OPENAI_API_KEY
    from agent_factory import get_agent
    from utils import generate_request_id
except ImportError as e:
    # Fallback if imports fail
    from pydantic import BaseModel
    
    class ChatRequest(BaseModel):
        message: str
        agent_type: str = "custom"
    
    class ChatResponse(BaseModel):
        response: str
        request_id: str
        timestamp: str
    
    class ErrorResponse(BaseModel):
        error: str
        request_id: str
        timestamp: str

@app.post("/")
async def search_trails(request: ChatRequest):
    """Search trails endpoint"""
    try:
        # Generate request ID
        request_id = f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Simple response for now (you can enhance this)
        response = f"Received search request: {request.message}"
        
        return ChatResponse(
            response=response,
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

# For Vercel
def handler(request):
    return app
