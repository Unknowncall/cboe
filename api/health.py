import json
import os
import logging
from datetime import datetime
from http import HTTPStatus

# Import shared modules
from models import HealthResponse, ErrorResponse
from utils import generate_request_id

# Simple logging setup for serverless
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """Health check endpoint for Vercel serverless function"""
    request_id = generate_request_id()
    logger.info(f"Health check requested (Request: {request_id})")
    
    try:
        # For serverless, we can't test database connectivity in the same way
        # Return a simple health status
        response = HealthResponse(
            status="healthy",
            timestamp=int(datetime.utcnow().timestamp()),
            version="1.0.0",
            database_status="not_checked",  # Database check would need modification for serverless
            request_id=request_id
        )
        
        return {
            'statusCode': HTTPStatus.OK,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(response.model_dump())
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e} (Request: {request_id})")
        error_response = ErrorResponse(
            error="Health check failed",
            detail=str(e),
            request_id=request_id,
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