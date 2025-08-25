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
    """Trail model for API responses with enhanced information"""
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
    
    # Enhanced location information
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    
    # Amenities and access information
    parking_available: Optional[bool] = None
    parking_type: Optional[str] = None
    restrooms: Optional[bool] = None
    water_available: Optional[bool] = None
    picnic_areas: Optional[bool] = None
    camping_available: Optional[bool] = None
    
    # Access and permit information
    entry_fee: Optional[bool] = None
    permit_required: Optional[bool] = None
    seasonal_access: Optional[str] = None
    accessibility: Optional[str] = None
    
    # Trail characteristics
    surface_type: Optional[str] = None
    trail_markers: Optional[bool] = None
    loop_trail: Optional[bool] = None
    
    # Contact and website
    managing_agency: Optional[str] = None
    website_url: Optional[str] = None
    phone_number: Optional[str] = None

class TrailDetail(BaseModel):
    """Detailed trail model with full description and all amenities"""
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
    
    # Enhanced location information
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    
    # Amenities and access information
    parking_available: Optional[bool] = None
    parking_type: Optional[str] = None
    restrooms: Optional[bool] = None
    water_available: Optional[bool] = None
    picnic_areas: Optional[bool] = None
    camping_available: Optional[bool] = None
    
    # Access and permit information
    entry_fee: Optional[bool] = None
    permit_required: Optional[bool] = None
    seasonal_access: Optional[str] = None
    accessibility: Optional[str] = None
    
    # Trail characteristics
    surface_type: Optional[str] = None
    trail_markers: Optional[bool] = None
    loop_trail: Optional[bool] = None
    
    # Contact and website
    managing_agency: Optional[str] = None
    website_url: Optional[str] = None
    phone_number: Optional[str] = None

class ParsedFilters(BaseModel):
    """Enhanced parsed search filters from user input"""
    distance_cap_miles: Optional[float] = None
    distance_min_miles: Optional[float] = None
    elevation_cap_m: Optional[int] = None
    difficulty: Optional[str] = None
    route_type: Optional[str] = None
    features: List[str] = []
    dogs_allowed: Optional[bool] = None
    radius_miles: Optional[float] = None
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    
    # Enhanced location filters
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    
    # Amenity filters - using consistent field names with database
    parking_available: Optional[bool] = None
    parking_type: Optional[str] = None  # 'free', 'paid', 'limited', 'street'
    restrooms: Optional[bool] = None
    water_available: Optional[bool] = None
    picnic_areas: Optional[bool] = None
    camping_available: Optional[bool] = None
    
    # Access and permit filters
    entry_fee: Optional[bool] = None  # True for trails WITH fees, False for free trails
    permit_required: Optional[bool] = None
    seasonal_access: Optional[str] = None  # 'year-round', 'seasonal', 'summer', 'winter'
    accessibility: Optional[str] = None  # 'wheelchair', 'stroller', 'none'
    
    # Trail characteristics
    surface_type: Optional[str] = None  # 'paved', 'gravel', 'dirt', 'boardwalk', 'mixed'
    trail_markers: Optional[bool] = None
    loop_trail: Optional[bool] = None
    
    # Managing agency filter
    managing_agency: Optional[str] = None

class ToolTrace(BaseModel):
    """Enhanced tool execution trace for debugging and transparency"""
    tool: str
    duration_ms: int
    result_count: Optional[int] = None
    input_parameters: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    search_filters: Optional[Dict[str, Any]] = None
    database_query: Optional[str] = None
    ai_confidence: Optional[float] = None
    processing_steps: List[str] = []
    errors: List[str] = []
    success: bool = True

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
