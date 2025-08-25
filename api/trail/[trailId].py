import json
import logging
from http import HTTPStatus
from datetime import datetime

# Import shared modules
from models import TrailDetail, ErrorResponse
from utils import generate_request_id
from database import DatabaseManager

# Simple logging setup for serverless
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database manager
db_manager = None

def init_db():
    """Initialize database manager"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager("trails.db")

def handler(request):
    """Get trail details by ID for Vercel serverless function"""
    try:
        init_db()
        
        # Handle CORS preflight
        if request.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': ''
            }
        
        # Extract trail ID from path parameters
        path_params = request.get('pathParameters', {})
        trail_id_str = path_params.get('trailId')
        
        if not trail_id_str:
            return {
                'statusCode': HTTPStatus.BAD_REQUEST,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Trail ID is required'
                })
            }
        
        try:
            trail_id = int(trail_id_str)
        except ValueError:
            return {
                'statusCode': HTTPStatus.BAD_REQUEST,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid trail ID format'
                })
            }
        
        request_id = generate_request_id()
        logger.info(f"Trail details requested for ID: {trail_id} (Request: {request_id})")
        
        # Get trail details from database
        trail_details = db_manager.get_trail_details(trail_id, request_id)
        
        if not trail_details:
            return {
                'statusCode': HTTPStatus.NOT_FOUND,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f'Trail with ID {trail_id} not found'
                })
            }
        
        return {
            'statusCode': HTTPStatus.OK,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(trail_details)
        }
        
    except Exception as e:
        logger.error(f"Trail details endpoint failed: {e}")
        error_response = ErrorResponse(
            error="Failed to retrieve trail details",
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