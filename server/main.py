"""
CBOE Trail Search API - Main FastAPI Application

A modular trail search API with enhanced logging and debugging capabilities.
Refactored into separate modules for better maintainability.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import os

# Import our modular components
from config import (
    API_TITLE, API_VERSION, ALLOWED_ORIGINS, HOST, OPENAI_API_KEY, PORT, 
    WORDS_PER_CHUNK, STREAM_DELAY_MS, MAX_REQUEST_SIZE, DB_POOL_SIZE, setup_logging
)
from models import (
    ChatRequest, Trail, TrailDetail, ParsedFilters, ToolTrace,
    ChatResponse, HealthResponse, SeedResponse, ErrorResponse
)
from database import db_manager
from search import trail_searcher
from agent_factory import get_agent, get_available_agents, AgentType
from utils import generate_request_id, log_request, PerformanceTimer

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request size for security"""
    def __init__(self, app, max_size: int = 1024):  # 1KB limit for search requests
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        if hasattr(request, 'headers') and 'content-length' in request.headers:
            content_length = int(request.headers['content-length'])
            if content_length > self.max_size:
                raise HTTPException(status_code=413, detail="Request payload too large")
        return await call_next(request)

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE, 
    version=API_VERSION,
    description="Enhanced trail search API with comprehensive logging and modular architecture"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Now properly restricted to localhost only
    allow_credentials=False,  # Disabled for security unless specifically needed
    allow_methods=["GET", "POST"],  # Only allow necessary methods
    allow_headers=["Content-Type", "Authorization"],  # Restrict headers
)

# Add request size limit middleware for security
app.add_middleware(RequestSizeLimitMiddleware, max_size=MAX_REQUEST_SIZE)

# Mount static files for serving the React frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Serve React app for any route that doesn't match API routes
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve React app for all non-API routes"""
        # Don't serve React for API routes
        if full_path.startswith("api/") or full_path.startswith("health") or full_path.startswith("docs") or full_path.startswith("openapi"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for all other routes (React Router will handle routing)
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")

# Global error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=f"HTTP {exc.status_code}",
            request_id=request.headers.get("X-Request-ID"),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            request_id=request.headers.get("X-Request-ID"),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )

logger.info(f"FastAPI app initialized: {API_TITLE} v{API_VERSION}")

async def generate_stream_response(request_id: str, message: str, agent_type: str = "custom"):
    """Generate AI-powered streaming response for chat request"""
    logger.info(f"Starting AI agent response generation (Request: {request_id}, Agent: {agent_type})")
    
    # Debug logging for agent type
    logger.info(f"DEBUG: Received agent_type parameter: '{agent_type}' (type: {type(agent_type)})")

    try:
        # Get the AI agent instance based on type
        logger.info(f"DEBUG: Creating AgentType enum from: '{agent_type}'")
        agent_enum = AgentType(agent_type)
        logger.info(f"DEBUG: Created AgentType enum: {agent_enum}")
        
        agent = get_agent(agent_enum)
        logger.info(f"DEBUG: get_agent returned: {type(agent).__name__} for agent_type: {agent_type}")
        
        if not agent:
            raise Exception(f"Failed to create {agent_type} agent")
        
        # Track tool execution for debugging
        tool_traces = []
        parsed_filters = None
        trails = []
        
        # Stream AI agent response
        async for chunk in agent.process_query(message, request_id):
            if chunk["type"] == "token":
                # Stream AI-generated content
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(STREAM_DELAY_MS / 1000.0)
                
            elif chunk["type"] == "trails":
                # Capture trails for final response
                trails = chunk["trails"]
                
                # Add tool trace for search operation
                tool_traces.append({
                    'tool': 'ai_agent_search',
                    'duration_ms': 0,  # Will be calculated by agent
                    'result_count': len(trails)
                })
                
            elif chunk["type"] == "error":
                # Handle agent errors
                logger.error(f"AI agent error: {chunk.get('message', 'Unknown error')} (Request: {request_id})")
                yield f"data: {json.dumps(chunk)}\n\n"
        
        # Create parsed filters from AI agent if available (fallback to text parser)
        try:
            parsed_filters = trail_searcher.text_parser.parse_user_input(message, request_id)
        except Exception as e:
            logger.warning(f"Fallback filter parsing failed: {e} (Request: {request_id})")
            parsed_filters = ParsedFilters()
        
        # Final results with comprehensive data
        results_data = {
            'type': 'done',
            'results': trails,
            'parsed_filters': parsed_filters.model_dump() if parsed_filters else {},
            'tool_traces': tool_traces,
            'request_id': request_id
        }
        
        yield f"data: {json.dumps(results_data)}\n\n"
        logger.info(f"AI agent response completed (Request: {request_id})")
        
    except Exception as e:
        error_msg = f"AI agent processing failed: {str(e)}"
        logger.error(f"AI agent error: {e} (Request: {request_id})")
        
        # Fallback to traditional search if AI agent fails
        logger.info(f"Falling back to traditional search (Request: {request_id})")
        
        try:
            # Parse filters using traditional method
            filters = trail_searcher.text_parser.parse_user_input(message, request_id)
            
            # Perform traditional search
            trails = trail_searcher.search_trails(message, filters, request_id)
            
            # Generate basic response
            fallback_content = f"I encountered an issue with AI processing, but found {len(trails)} trails using traditional search."
            yield f"data: {json.dumps({'type': 'token', 'content': fallback_content})}\n\n"
            
            # Return results
            results_data = {
                'type': 'done',
                'results': trails,
                'parsed_filters': filters.model_dump(),
                'tool_traces': [{'tool': 'fallback_search', 'result_count': len(trails)}],
                'request_id': request_id,
                'errors': [error_msg]
            }
            
            yield f"data: {json.dumps(results_data)}\n\n"
            
        except Exception as fallback_error:
            logger.error(f"Fallback search also failed: {fallback_error} (Request: {request_id})")
            error_response = {
                'type': 'done',
                'results': [],
                'parsed_filters': {},
                'tool_traces': [],
                'request_id': request_id,
                'errors': [error_msg, str(fallback_error)]
            }
            yield f"data: {json.dumps(error_response)}\n\n"


# API Routes

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    logger.debug("Root endpoint accessed")
    return {
        "message": f"Welcome to {API_TITLE}",
        "version": API_VERSION,
        "status": "healthy"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with database connectivity test"""
    request_id = generate_request_id()
    logger.info(f"Health check requested (Request: {request_id})")
    
    try:
        # Test database connectivity
        trail_count = db_manager.get_trail_count(request_id)
        status = "healthy"
        message = f"Trail search server is running with {trail_count} trails available"
        
        logger.info(f"Health check passed: {trail_count} trails (Request: {request_id})")
        
    except Exception as e:
        status = "unhealthy"
        message = f"Database connection failed: {str(e)}"
        logger.error(f"Health check failed: {e} (Request: {request_id})")
    
    return HealthResponse(status=status, message=message)


@app.get("/api/agents")
async def get_agents():
    """Get available AI agent types"""
    request_id = generate_request_id()
    logger.info(f"Agents list requested (Request: {request_id})")
    
    agents = get_available_agents()
    return {
        "agents": agents,
        "default": "custom",
        "request_id": request_id
    }


@app.post("/api/chat")
async def chat_stream(request: ChatRequest):
    """Stream trail search results with enhanced logging and error handling"""
    request_id = generate_request_id()
    logger.info(f"Chat request received: '{request.message}' using {request.agent_type} agent (Request: {request_id})")
    
    # Debug logging for request
    logger.info(f"DEBUG: ChatRequest.agent_type = '{request.agent_type}' (type: {type(request.agent_type)})")
    logger.info(f"DEBUG: Full request object: {request.model_dump()}")
    
    def generate():
        """Generator function for streaming response"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def async_gen():
                async for chunk in generate_stream_response(request_id, request.message, request.agent_type):
                    yield chunk
            
            # Run the async generator in the event loop
            gen = async_gen()
            while True:
                try:
                    chunk = loop.run_until_complete(gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        except Exception as e:
            logger.error(f"Stream generation failed: {e} (Request: {request_id})")
            error_response = json.dumps({
                'type': 'error',
                'content': f'Internal server error: {str(e)}',
                'request_id': request_id
            })
            yield f"data: {error_response}\n\n"
        finally:
            loop.close()
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Request-ID": request_id,
        }
    )


@app.get("/api/trail/{trail_id}", response_model=TrailDetail)
async def get_trail_details(trail_id: int):
    """Get detailed trail information by ID"""
    request_id = generate_request_id()
    logger.info(f"Trail details requested for ID: {trail_id} (Request: {request_id})")
    
    trail = db_manager.get_trail_by_id(trail_id, request_id)
    if not trail:
        logger.warning(f"Trail {trail_id} not found (Request: {request_id})")
        raise HTTPException(status_code=404, detail=f"Trail with ID {trail_id} not found")
    
    logger.info(f"Trail details returned for: {trail['name']} (Request: {request_id})")
    return TrailDetail(**trail)


@app.post("/api/debug/parse", response_model=ParsedFilters)
async def debug_parse_filters(request: ChatRequest):
    """Debug endpoint to test filter parsing"""
    request_id = generate_request_id()
    logger.info(f"Debug parse request: '{request.message}' (Request: {request_id})")
    
    filters = trail_searcher.text_parser.parse_user_input(request.message, request_id)
    logger.info(f"Debug parse result: {filters.model_dump()} (Request: {request_id})")
    
    return filters


@app.post("/api/seed", response_model=SeedResponse)
async def seed_database():
    """Initialize and seed the database with trail data"""
    request_id = generate_request_id()
    logger.info(f"Database seed requested (Request: {request_id})")
    
    try:
        # Initialize database structure
        if not db_manager.init_database(request_id):
            raise HTTPException(status_code=500, detail="Failed to initialize database")
        
        # Seed with trail data
        trails_count = db_manager.seed_trails(request_id)
        if trails_count == 0:
            raise HTTPException(status_code=500, detail="Failed to seed database")
        
        logger.info(f"Database seeded successfully with {trails_count} trails (Request: {request_id})")
        return SeedResponse(
            message=f"Database seeded successfully with {trails_count} trails",
            trails_count=trails_count
        )
        
    except Exception as e:
        logger.error(f"Database seeding failed: {e} (Request: {request_id})")
        raise HTTPException(status_code=500, detail=f"Database seeding failed: {str(e)}")


# Application lifecycle events

async def startup_event():
    """Initialize database on application startup"""
    startup_id = "startup"
    logger.info("Application startup initiated")
    
    try:
        # Initialize database structure
        db_manager.init_database(startup_id)
        
        # Check if we need to seed
        trail_count = db_manager.get_trail_count(startup_id)
        
        if trail_count == 0:
            trails_seeded = db_manager.seed_trails(startup_id)
            logger.info(f"Database seeded automatically on startup with {trails_seeded} trails")
        else:
            logger.info(f"Database already contains {trail_count} trails")
            
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise


async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Application shutdown initiated")
    # Add any cleanup logic here if needed
    logger.info("Application shutdown completed")


# Register event handlers
app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)


if __name__ == "__main__":
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    uvicorn.run(
        "main:app", 
        host=HOST, 
        port=PORT, 
        reload=True,
        log_level="info"
    )
