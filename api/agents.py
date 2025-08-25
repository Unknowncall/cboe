import json
import logging
from http import HTTPStatus

# Import shared modules  
from agent_factory import get_available_agents
from utils import generate_request_id

# Simple logging setup for serverless
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """Get available AI agent types for Vercel serverless function"""
    request_id = generate_request_id()
    logger.info(f"Agents endpoint requested (Request: {request_id})")
    
    try:
        agents = get_available_agents()
        
        return {
            'statusCode': HTTPStatus.OK,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(agents)
        }
        
    except Exception as e:
        logger.error(f"Agents endpoint failed: {e} (Request: {request_id})")
        
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "error": "Failed to retrieve agents",
                "detail": str(e),
                "request_id": request_id
            })
        }