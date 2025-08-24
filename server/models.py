"""
Pydantic models for the CBOE Trail Search API
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=1000, description="User's search query for trails")
    agent_type: Optional[str] = Field("custom", description="Type of AI agent to use (custom or langchain)")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()
    
    @validator('agent_type')
    def validate_agent_type(cls, v):
        if v not in ["custom", "langchain"]:
            raise ValueError('Agent type must be "custom" or "langchain"')
        return v

class Trail(BaseModel):
    """Trail model for API responses"""
    id: int
    name: str
    distance_miles: float
    elevation_gain_m: int
    difficulty: str
    dogs_allowed: bool
    route_type: str
    features: List[str]
    latitude: float
    longitude: float
    description_snippet: str
    why: str

class TrailDetail(BaseModel):
    """Detailed trail model with full description"""
    id: int
    name: str
    distance_miles: float
    elevation_gain_m: int
    difficulty: str
    dogs_allowed: bool
    route_type: str
    features: List[str]
    latitude: float
    longitude: float
    description: str

class ParsedFilters(BaseModel):
    """Parsed search filters from user input"""
    distance_cap_miles: Optional[float] = None
    elevation_cap_m: Optional[int] = None
    difficulty: Optional[str] = None
    route_type: Optional[str] = None
    features: List[str] = []
    dogs_allowed: Optional[bool] = None
    radius_miles: Optional[float] = None
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None

class ToolTrace(BaseModel):
    """Tool execution trace for debugging"""
    tool: str
    duration_ms: int
    result_count: int

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    results: List[Trail]
    parsed_filters: ParsedFilters
    tool_traces: Optional[List[ToolTrace]] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str

class SeedResponse(BaseModel):
    """Database seed response"""
    message: str
    trails_count: int

class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str
    detail: str
    request_id: Optional[str] = None
    timestamp: str
