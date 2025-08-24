"""
Utility functions for the CBOE Trail Search API
"""
import math
import time
import json
import uuid
import logging
from typing import Dict, Any

logger = logging.getLogger("trail_search.utils")

# Unit conversion constants
KM_TO_MILES = 0.621371
MILES_TO_KM = 1.609344

def km_to_miles(km: float) -> float:
    """Convert kilometers to miles"""
    return km * KM_TO_MILES

def miles_to_km(miles: float) -> float:
    """Convert miles to kilometers"""
    return miles * MILES_TO_KM

def generate_request_id() -> str:
    """Generate a unique request ID"""
    request_id = str(uuid.uuid4())
    logger.debug(f"Generated request ID: {request_id}")
    return request_id

def log_request(request_id: str, tool: str, duration_ms: int, result_count: int, **kwargs):
    """Log request details as JSON lines with enhanced debugging info"""
    log_data = {
        "timestamp": time.time(),
        "request_id": request_id,
        "tool": tool,
        "duration_ms": duration_ms,
        "result_count": result_count,
        **kwargs
    }
    
    # Log as JSON for structured logging
    logger.info(f"TOOL_TRACE: {json.dumps(log_data)}")
    
    # Also print for backward compatibility
    print(json.dumps(log_data))

def log_search_query(request_id: str, query: str, filters: Dict[str, Any]):
    """Log search query details for debugging"""
    log_data = {
        "timestamp": time.time(),
        "request_id": request_id,
        "event": "search_query",
        "query": query,
        "filters": filters
    }
    logger.debug(f"SEARCH_QUERY: {json.dumps(log_data)}")

def log_database_operation(request_id: str, operation: str, table: str, duration_ms: int, affected_rows: int = 0):
    """Log database operation details"""
    log_data = {
        "timestamp": time.time(),
        "request_id": request_id,
        "event": "database_operation",
        "operation": operation,
        "table": table,
        "duration_ms": duration_ms,
        "affected_rows": affected_rows
    }
    logger.debug(f"DB_OPERATION: {json.dumps(log_data)}")

def log_filter_application(request_id: str, filter_type: str, input_count: int, output_count: int, filter_value: Any):
    """Log filter application for debugging"""
    log_data = {
        "timestamp": time.time(),
        "request_id": request_id,
        "event": "filter_applied",
        "filter_type": filter_type,
        "input_count": input_count,
        "output_count": output_count,
        "filter_value": filter_value
    }
    logger.debug(f"FILTER_APPLIED: {json.dumps(log_data)}")

def geo_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate Haversine distance between two points in miles
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
    
    Returns:
        Distance in miles
    """
    logger.debug(f"Calculating distance between ({lat1}, {lon1}) and ({lat2}, {lon2})")
    
    R = 3958.8  # Earth's radius in miles
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    logger.debug(f"Calculated distance: {distance:.2f} miles")
    return distance

def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate latitude and longitude coordinates"""
    if not (-90 <= lat <= 90):
        logger.warning(f"Invalid latitude: {lat}")
        return False
    if not (-180 <= lng <= 180):
        logger.warning(f"Invalid longitude: {lng}")
        return False
    return True

def format_distance(distance_miles: float) -> str:
    """Format distance for display"""
    if distance_miles < 0.1:
        return f"{distance_miles * 5280:.0f}ft"
    else:
        return f"{distance_miles:.1f}mi"

def format_elevation(elevation_m: int) -> str:
    """Format elevation for display"""
    return f"{elevation_m}m"

def truncate_description(description: str, max_length: int = 200) -> str:
    """Truncate description to specified length"""
    if len(description) <= max_length:
        return description
    return description[:max_length] + "..."

class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str, request_id: str = None):
        self.operation_name = operation_name
        self.request_id = request_id or "unknown"
        self.start_time = None
        self.duration_ms = 0
        
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting operation: {self.operation_name} (Request: {self.request_id})")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = int((time.time() - self.start_time) * 1000)
        if exc_type is None:
            logger.debug(f"Completed operation: {self.operation_name} in {self.duration_ms}ms (Request: {self.request_id})")
        else:
            logger.error(f"Failed operation: {self.operation_name} after {self.duration_ms}ms (Request: {self.request_id}): {exc_val}")
    
    def get_duration_ms(self) -> int:
        """Get the current duration in milliseconds"""
        if self.start_time is None:
            return 0
        return int((time.time() - self.start_time) * 1000)
