import json
import logging
import asyncio
from http import HTTPStatus
from datetime import datetime

# Import shared modules
from models import ChatRequest, ErrorResponse
from utils import generate_request_id
from database import DatabaseManager
from search import TrailSearcher
from agent_factory import get_agent

# Simple logging setup for serverless
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components (these will be reused across function calls)
db_manager = None
trail_searcher = None

def init_components():
    """Initialize database and search components"""
    global db_manager, trail_searcher
    if db_manager is None:
        db_manager = DatabaseManager("trails.db")
        trail_searcher = TrailSearcher(db_manager)

def handler(request):
    """Chat endpoint for streaming trail search"""
    try:
        # Initialize components
        init_components()
        
        # Parse request body
        if request.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': ''
            }
        
        body = json.loads(request.get('body', '{}'))
        chat_request = ChatRequest(**body)
        request_id = generate_request_id()
        
        logger.info(f"Chat request received: {chat_request.message[:100]}... (Request: {request_id})")
        
        # For serverless, we can't do streaming responses in the same way
        # We'll return a single response with all the data
        
        # Get the AI agent
        agent = get_agent(chat_request.agent_type)
        
        # Process the search
        response_content = ""
        trails = []
        tool_traces = []
        
        # Use the agent to process the request
        try:
            # Simplified processing for serverless environment
            agent_response = agent.process(chat_request.message, request_id)
            
            if agent_response.get('trails'):
                trails = agent_response['trails']
            
            if agent_response.get('content'):
                response_content = agent_response['content']
                
            if agent_response.get('tool_traces'):
                tool_traces = agent_response['tool_traces']
                
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            # Fallback to basic search
            filters = trail_searcher.text_parser.parse_user_input(chat_request.message, request_id)
            trails = trail_searcher.search_trails(chat_request.message, filters, request_id)
            response_content = f"Found {len(trails)} trails matching your criteria."
        
        # Return complete response
        response_data = {
            'type': 'complete',
            'content': response_content,
            'results': trails,
            'tool_traces': tool_traces,
            'request_id': request_id
        }
        
        return {
            'statusCode': HTTPStatus.OK,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}")
        error_response = ErrorResponse(
            error="Chat request failed",
            detail=str(e),
            request_id=request_id if 'request_id' in locals() else generate_request_id(),
            timestamp=datetime.utcnow().isoformat()
        )
        
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(error_response.model_dump())
        }