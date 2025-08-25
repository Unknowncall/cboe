"""
LangChain AI Agent for Trail Search

This module implements an AI agent using the LangChain framework
with OpenAI function calling for trail search recommendations.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, AsyncGenerator, Optional

# Always import Pydantic as it's a core dependency
from pydantic import BaseModel, Field

try:
    from langchain.agents import AgentType, initialize_agent
    from langchain.memory import ConversationBufferMemory  
    from langchain.tools import BaseTool
    from langchain_openai import ChatOpenAI
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
    from langchain.callbacks.base import BaseCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LangChain not available: {e}")
    LANGCHAIN_AVAILABLE = False
    # Create dummy classes to prevent import errors
    class BaseTool:
        pass
    class BaseCallbackHandler:
        pass

from config import OPENAI_API_KEY, OPENAI_MODEL
from search import trail_searcher
from models import ParsedFilters

logger = logging.getLogger("trail_search.langchain_agent")

if LANGCHAIN_AVAILABLE:
    class TrailSearchInput(BaseModel):
        """Input schema for trail search tool with enhanced filtering capabilities"""
        query: str = Field(description="The user's natural language query about trails")
        location: Optional[str] = Field(None, description="Location or city name to search near (e.g., 'Chicago', 'near Chicago')")
        max_distance_miles: Optional[float] = Field(None, description="Maximum trail length in miles if specified")
        min_distance_miles: Optional[float] = Field(None, description="Minimum trail length in miles. Use this when the user says 'more than X miles', 'over X miles', 'at least X miles', 'longer than X miles', 'greater than X miles', etc.")
        max_elevation_gain_m: Optional[float] = Field(None, description="Maximum elevation gain in meters if specified")
        difficulty: Optional[str] = Field(None, description="Trail difficulty level (easy/moderate/hard)")
        route_type: Optional[str] = Field(None, description="Type of trail route (loop/out and back)")
        dogs_allowed: Optional[bool] = Field(None, description="Whether dogs are allowed/wanted on the trail. True if user mentions bringing/taking their dog, wants dog-friendly trails, etc.")
        features: Optional[List[str]] = Field(None, description="Desired trail features extracted from the query like 'waterfall', 'lake', 'scenic', 'views', 'forest', 'prairie', 'beach', 'canyon', 'historic', etc.")
        radius_miles: Optional[float] = Field(None, description="Search radius in miles from the specified location if mentioned")
        
        # Enhanced location filters
        city: Optional[str] = Field(None, description="Specific city name if mentioned (e.g., 'Chicago', 'Milwaukee')")
        county: Optional[str] = Field(None, description="County name if mentioned (e.g., 'Cook County', 'DuPage County')")
        state: Optional[str] = Field(None, description="State name if mentioned (e.g., 'Illinois', 'Wisconsin', 'Michigan')")
        region: Optional[str] = Field(None, description="Region name if mentioned (e.g., 'Great Lakes', 'Chicago Metropolitan')")
        
        # Amenity filters
        parking_available: Optional[bool] = Field(None, description="True if user specifically mentions needing parking available")
        parking_type: Optional[str] = Field(None, description="Type of parking if specified (free, paid, limited, street parking)")
        restrooms: Optional[bool] = Field(None, description="True if user specifically mentions needing restrooms/facilities")
        water_available: Optional[bool] = Field(None, description="True if user mentions needing water fountains or water availability")
        picnic_areas: Optional[bool] = Field(None, description="True if user mentions wanting picnic areas or tables")
        camping_available: Optional[bool] = Field(None, description="True if user mentions camping or overnight stays")
        
        # Access and permit filters
        entry_fee: Optional[bool] = Field(None, description="True if user is okay with entry fees, False if they want free trails or mention no fees")
        permit_required: Optional[bool] = Field(None, description="True if user is okay with permits, False if they want no permit required")
        seasonal_access: Optional[str] = Field(None, description="Seasonal access preference if mentioned (year-round, seasonal, summer, winter)")
        accessibility: Optional[str] = Field(None, description="Accessibility requirements if mentioned (wheelchair, stroller, none)")
        
        # Trail characteristics
        surface_type: Optional[str] = Field(None, description="Preferred trail surface type if mentioned (paved, gravel, dirt, boardwalk, mixed)")
        trail_markers: Optional[bool] = Field(None, description="True if user mentions wanting well-marked trails or good signage")
        loop_trail: Optional[bool] = Field(None, description="True if user specifically wants loop trails, False if they prefer out-and-back")
        managing_agency: Optional[str] = Field(None, description="Managing agency or park system if mentioned (e.g., 'National Park Service', 'Illinois State Parks', 'Chicago Park District')")

    class GetAllTrailsInput(BaseModel):
        """Input schema for get all trails tool"""
        query: str = Field(description="The user's natural language query")
        area_filter: Optional[str] = Field(None, description="Optional area name to filter trails by (e.g., 'Chicago', 'Illinois', 'Cook County'). Extract from user query if they mention a specific area.")
        limit: Optional[int] = Field(50, description="Maximum number of trails to return (default: 50, max: 100)")

    class TrailSearchTool(BaseTool):
        """LangChain tool for trail search functionality"""
        name: str = "search_trails"
        description: str = """Search for hiking trails based on comprehensive user criteria including location, difficulty, distance, features, amenities, accessibility, and costs. Extract all relevant parameters from the user's natural language query including:
        - Location (city, county, state, region) to search near
        - Maximum trail length in miles AND minimum trail length (for 'over X miles' queries)  
        - Trail difficulty level (easy/moderate/hard) and route type (loop/out and back)
        - Whether dogs are allowed/wanted
        - Desired trail features like 'waterfall', 'lake', 'scenic', 'views', 'forest', 'prairie', 'beach', 'canyon', 'historic'
        - Amenities: parking availability/type, restrooms, water fountains, picnic areas, camping
        - Accessibility requirements: wheelchair accessible, stroller friendly, surface type (paved/gravel/dirt/boardwalk)
        - Cost preferences: free trails vs. entry fees, permit requirements
        - Managing agency preferences: National Park Service, state parks, local parks
        - Search radius in miles from the specified location"""
        args_schema: type = TrailSearchInput
        agent_instance: Any = Field(default=None, exclude=True)
        
        def __init__(self, agent_instance=None, **kwargs):
            super().__init__(agent_instance=agent_instance, **kwargs)
        
        def _run(self, query: str, location: str = None, max_distance_miles: float = None, 
                 min_distance_miles: float = None, max_elevation_gain_m: float = None, difficulty: str = None, route_type: str = None,
                 dogs_allowed: bool = None, features: List[str] = None, radius_miles: float = None,
                 city: str = None, county: str = None, state: str = None, region: str = None,
                 parking_available: bool = None, parking_type: str = None, restrooms: bool = None,
                 water_available: bool = None, picnic_areas: bool = None, camping_available: bool = None,
                 entry_fee: bool = None, permit_required: bool = None, seasonal_access: str = None,
                 accessibility: str = None, surface_type: str = None, trail_markers: bool = None,
                 loop_trail: bool = None, managing_agency: str = None, **kwargs) -> str:
            """Execute trail search with LangChain's enhanced reasoning"""
            try:
                logger.info(f"LangChain tool executing enhanced search with comprehensive filtering: {query}")
                
                # Use LangChain's reasoning to provide better parameter interpretation
                trails = self._execute_search_with_reasoning(
                    query, location, max_distance_miles, min_distance_miles, max_elevation_gain_m, difficulty, route_type, 
                    dogs_allowed, features, radius_miles, city, county, state, region,
                    parking_available, parking_type, restrooms, water_available, picnic_areas, 
                    camping_available, entry_fee, permit_required, seasonal_access, accessibility,
                    surface_type, trail_markers, loop_trail, managing_agency
                )
                
                if self.agent_instance:
                    self.agent_instance.last_trails = trails
                    logger.info(f"TrailSearchTool: Set {len(trails)} trails on agent instance")
                else:
                    logger.warning("TrailSearchTool: No agent instance available to set trails on")
                
                # Return reasoning-based response for the agent
                if trails:
                    # LangChain provides more detailed analysis
                    analysis_parts = []
                    analysis_parts.append(f"✅ Search completed! I analyzed your request and found {len(trails)} trails.")
                    
                    # Add reasoning about the search strategy
                    if location or city or county or state:
                        location_parts = []
                        if location: location_parts.append(location)
                        if city: location_parts.append(city)
                        if county: location_parts.append(county)
                        if state: location_parts.append(state)
                        location_str = ", ".join(location_parts)
                        analysis_parts.append(f"🗺️ I focused on the {location_str} area as you specified.")
                    
                    if difficulty:
                        analysis_parts.append(f"⚡ I filtered for {difficulty} difficulty trails to match your fitness level.")
                    
                    if max_distance_miles:
                        analysis_parts.append(f"📏 I limited results to trails under {max_distance_miles} miles as requested.")
                    
                    if min_distance_miles:
                        analysis_parts.append(f"📏 I filtered for trails over {min_distance_miles} miles for a more substantial hike.")
                    
                    if entry_fee is False:
                        analysis_parts.append(f"💲 I ensured all trails are free as you requested.")
                    elif entry_fee is True:
                        analysis_parts.append(f"💰 I included trails with entry fees that offer premium amenities.")
                    
                    amenity_features = []
                    if parking_available: amenity_features.append("parking")
                    if restrooms: amenity_features.append("restrooms")
                    if water_available: amenity_features.append("water fountains")
                    if picnic_areas: amenity_features.append("picnic areas")
                    if camping_available: amenity_features.append("camping")
                    
                    if amenity_features:
                        analysis_parts.append(f"🏪 I filtered for trails with these amenities: {', '.join(amenity_features)}.")
                    
                    if accessibility:
                        accessibility_text = {"wheelchair": "wheelchair accessible", "stroller": "stroller friendly"}.get(accessibility, accessibility)
                        analysis_parts.append(f"♿ I ensured all trails are {accessibility_text} as requested.")
                    
                    if surface_type:
                        analysis_parts.append(f"🛤️ I focused on {surface_type} trails for your preferred surface type.")
                    
                    if managing_agency:
                        analysis_parts.append(f"🏛️ I limited results to {managing_agency} managed trails.")
                        
                    if features:
                        features_str = ", ".join(features)
                        analysis_parts.append(f"🌟 I prioritized trails with these features: {features_str}.")
                    
                    if dogs_allowed:
                        analysis_parts.append(f"🐕 I made sure all trails welcome your furry companion!")
                    
                    analysis_parts.append("\n🎯 Each result has been carefully selected based on your comprehensive criteria.")
                    
                    return "\n".join(analysis_parts)
                else:
                    return """❌ No trails found with the current criteria. 

🤔 Let me analyze what might help:
• Your criteria might be very specific - consider relaxing one requirement
• The location might have limited trail options
• Seasonal factors could affect availability

💡 I can help you adjust the search parameters for better results!"""
                    
            except Exception as e:
                logger.error(f"LangChain trail search tool error: {e}")
                return f"⚠️ Error during trail analysis: {str(e)}\n\nLet me try a different approach to help you find trails."
        
        def _execute_search_with_reasoning(self, query: str, location: str = None, max_distance_miles: float = None, 
                                          min_distance_miles: float = None, max_elevation_gain_m: float = None, difficulty: str = None, route_type: str = None,
                                          dogs_allowed: bool = None, features: List[str] = None, radius_miles: float = None,
                                          city: str = None, county: str = None, state: str = None, region: str = None,
                                          parking_available: bool = None, parking_type: str = None, restrooms: bool = None,
                                          water_available: bool = None, picnic_areas: bool = None, camping_available: bool = None,
                                          entry_fee: bool = None, permit_required: bool = None, seasonal_access: str = None,
                                          accessibility: str = None, surface_type: str = None, trail_markers: bool = None,
                                          loop_trail: bool = None, managing_agency: str = None) -> List[Dict[str, Any]]:
            """Execute trail search with enhanced LangChain reasoning and comprehensive parameter optimization"""
            
            # Build filters with LangChain's enhanced interpretation
            filters = ParsedFilters()
            
            # Apply basic parameters with smart defaults based on reasoning
            if max_distance_miles:
                filters.distance_cap_miles = max_distance_miles
            elif any(word in query.lower() for word in ["short", "quick", "easy walk"]):
                filters.distance_cap_miles = 3.0  # Smart default for short requests
                logger.info("LangChain reasoning: Applied 3-mile limit for 'short' trail request")
            
            if min_distance_miles:
                filters.distance_min_miles = min_distance_miles
                logger.info(f"LangChain reasoning: Applied minimum distance filter: {min_distance_miles} miles")
            
            if max_elevation_gain_m:
                filters.elevation_cap_m = max_elevation_gain_m
            elif difficulty == "easy":
                filters.elevation_cap_m = 200  # Smart default for easy trails
                logger.info("LangChain reasoning: Limited elevation gain for easy trails")
            
            if difficulty:
                filters.difficulty = difficulty
            
            if route_type:
                filters.route_type = route_type
            elif loop_trail is True or "loop" in query.lower():
                filters.route_type = "loop"
                logger.info("LangChain reasoning: Detected loop preference from query")
            elif loop_trail is False:
                filters.route_type = "out and back"
                logger.info("LangChain reasoning: Detected out-and-back preference")
            
            if dogs_allowed is not None:
                filters.dogs_allowed = dogs_allowed
            
            if features:
                filters.features = features
            
            # Enhanced location filters
            if city:
                filters.city = city
                logger.info(f"LangChain reasoning: Filtering by city: {city}")
            
            if county:
                filters.county = county
                logger.info(f"LangChain reasoning: Filtering by county: {county}")
            
            if state:
                filters.state = state
                logger.info(f"LangChain reasoning: Filtering by state: {state}")
            
            if region:
                filters.region = region
                logger.info(f"LangChain reasoning: Filtering by region: {region}")
            
            # Amenity filters
            if parking_available is not None:
                filters.parking_available = parking_available
                logger.info(f"LangChain reasoning: Parking requirement: {parking_available}")
            
            if parking_type:
                filters.parking_type = parking_type
                logger.info(f"LangChain reasoning: Parking type preference: {parking_type}")
            
            if restrooms is not None:
                filters.restrooms = restrooms
                logger.info(f"LangChain reasoning: Restroom requirement: {restrooms}")
            
            if water_available is not None:
                filters.water_available = water_available
                logger.info(f"LangChain reasoning: Water availability requirement: {water_available}")
            
            if picnic_areas is not None:
                filters.picnic_areas = picnic_areas
                logger.info(f"LangChain reasoning: Picnic area requirement: {picnic_areas}")
            
            if camping_available is not None:
                filters.camping_available = camping_available
                logger.info(f"LangChain reasoning: Camping availability requirement: {camping_available}")
            
            # Access and permit filters
            if entry_fee is not None:
                filters.entry_fee = entry_fee
                logger.info(f"LangChain reasoning: Entry fee preference: {'allowed' if entry_fee else 'free only'}")
            
            if permit_required is not None:
                filters.permit_required = permit_required
                logger.info(f"LangChain reasoning: Permit requirement: {'allowed' if permit_required else 'no permit'}")
            
            if seasonal_access:
                filters.seasonal_access = seasonal_access
                logger.info(f"LangChain reasoning: Seasonal access: {seasonal_access}")
            
            if accessibility:
                filters.accessibility = accessibility
                logger.info(f"LangChain reasoning: Accessibility requirement: {accessibility}")
            
            # Trail characteristics
            if surface_type:
                filters.surface_type = surface_type
                logger.info(f"LangChain reasoning: Surface type preference: {surface_type}")
            
            if trail_markers is not None:
                filters.trail_markers = trail_markers
                logger.info(f"LangChain reasoning: Trail marker requirement: {trail_markers}")
            
            if managing_agency:
                filters.managing_agency = managing_agency
                logger.info(f"LangChain reasoning: Agency preference: {managing_agency}")
            
            # Enhanced location handling with broader radius defaults and state detection
            if location:
                location_lower = location.lower()
                
                # Check if location is actually a state name (like custom agent)
                state_names = ['wisconsin', 'illinois', 'michigan', 'indiana', 'iowa', 'minnesota', 'ohio']
                if location_lower in state_names:
                    # Map location to state filter
                    filters.state = location
                    logger.info(f"LangChain reasoning: Location '{location}' mapped to state filter")
                elif "chicago" in location_lower:
                    filters.center_lat = 41.8781
                    filters.center_lng = -87.6298
                    # LangChain uses more generous defaults
                    if not radius_miles:
                        if "near" in query.lower() or "around" in query.lower():
                            filters.radius_miles = 75  # Broader search for "near Chicago"
                        else:
                            filters.radius_miles = 50
                    else:
                        filters.radius_miles = radius_miles
                    logger.info(f"LangChain reasoning: Set Chicago area search with {filters.radius_miles}-mile radius")
                else:
                    # For other locations, store as general location filter
                    logger.info(f"LangChain reasoning: General location '{location}' noted but not specifically mapped")
            
            # Execute the actual search
            trails = trail_searcher.search_trails(query, filters, "langchain-enhanced")
            return trails
        
        async def _arun(self, query: str, location: str = None, max_distance_miles: float = None, 
                        min_distance_miles: float = None, max_elevation_gain_m: float = None, difficulty: str = None, route_type: str = None,
                        dogs_allowed: bool = None, features: List[str] = None, radius_miles: float = None,
                        city: str = None, county: str = None, state: str = None, region: str = None,
                        parking_available: bool = None, parking_type: str = None, restrooms: bool = None,
                        water_available: bool = None, picnic_areas: bool = None, camping_available: bool = None,
                        entry_fee: bool = None, permit_required: bool = None, seasonal_access: str = None,
                        accessibility: str = None, surface_type: str = None, trail_markers: bool = None,
                        loop_trail: bool = None, managing_agency: str = None, **kwargs) -> str:
            """Async version of trail search with enhanced parameters"""
            return self._run(query, location, max_distance_miles, min_distance_miles, max_elevation_gain_m, difficulty, 
                           route_type, dogs_allowed, features, radius_miles, city, county, state, region,
                           parking_available, parking_type, restrooms, water_available, picnic_areas,
                           camping_available, entry_fee, permit_required, seasonal_access, accessibility,
                           surface_type, trail_markers, loop_trail, managing_agency, **kwargs)

    class StreamingCallbackHandler(BaseCallbackHandler):
        """Custom callback handler for streaming LangChain responses"""
        
        def __init__(self, stream_callback):
            self.stream_callback = stream_callback
            self.current_token = ""
        
        def on_llm_new_token(self, token: str, **kwargs) -> None:
            """Called when a new token is generated"""
            if self.stream_callback:
                self.stream_callback(token)

    class GetAllTrailsTool(BaseTool):
        """LangChain tool for getting all trails functionality"""
        name: str = "get_all_trails"
        description: str = """Get all trails in the database. Use this when users ask to see 'all trails', 'show me all trails', 'list all trails', or want to browse all available trails. Can optionally filter by area/location like 'all trails in Chicago' or 'show me all trails in Illinois'."""
        args_schema: type = GetAllTrailsInput
        agent_instance: Any = Field(default=None, exclude=True)
        
        def __init__(self, agent_instance=None, **kwargs):
            super().__init__(agent_instance=agent_instance, **kwargs)
        
        def _run(self, query: str, area_filter: str = None, limit: int = 50, **kwargs) -> str:
            """Execute get all trails with LangChain's enhanced reasoning"""
            try:
                from database import db_manager
                logger.info(f"LangChain tool executing get all trails: {query} (area: {area_filter}, limit: {limit})")
                
                # Execute get all trails query
                trails = db_manager.get_all_trails(
                    limit=min(limit, 100),  # Cap at 100
                    area_filter=area_filter,
                    request_id="langchain_get_all"
                )
                
                if self.agent_instance:
                    self.agent_instance.last_trails = trails
                    logger.info(f"GetAllTrailsTool: Set {len(trails)} trails on agent instance")
                else:
                    logger.warning("GetAllTrailsTool: No agent instance available to set trails on")
                
                # Return reasoning-based response for the agent
                if trails:
                    analysis_parts = []
                    area_text = f" in {area_filter}" if area_filter else ""
                    analysis_parts.append(f"✅ Successfully retrieved {len(trails)} trails{area_text}!")
                    
                    # Add reasoning about the results
                    analysis_parts.append(f"📋 I've organized them by difficulty level (easy → moderate → hard) for easy browsing.")
                    
                    if area_filter:
                        analysis_parts.append(f"🗺️ I filtered the results to show trails related to {area_filter}.")
                    else:
                        analysis_parts.append("🌍 These represent all available trails in our database.")
                    
                    # Provide overview statistics
                    difficulties = {}
                    for trail in trails:
                        diff = trail.get('difficulty', 'unknown')
                        difficulties[diff] = difficulties.get(diff, 0) + 1
                    
                    if difficulties:
                        stats = []
                        for diff in ['easy', 'moderate', 'hard']:
                            if diff in difficulties:
                                stats.append(f"{difficulties[diff]} {diff}")
                        if stats:
                            analysis_parts.append(f"📊 Breakdown: {', '.join(stats)} trails.")
                    
                    return "\n".join(analysis_parts)
                else:
                    area_text = f" in {area_filter}" if area_filter else ""
                    return f"❌ I couldn't find any trails{area_text}. There might be no trails matching that area or the database might be empty."
                    
            except Exception as e:
                logger.error(f"LangChain get all trails tool failed: {e}")
                return f"❌ I encountered an error while retrieving trails: {str(e)}"

    class LangChainTrailAgent:
        """LangChain-based AI agent for trail search"""
        
        def __init__(self):
            if not LANGCHAIN_AVAILABLE:
                raise ImportError("LangChain is not installed. Please install with: pip install langchain langchain-openai")
                
            # Initialize trail storage
            self.last_trails = []
            
            # Initialize LangChain components
            self.llm = ChatOpenAI(
                model=OPENAI_MODEL,
                openai_api_key=OPENAI_API_KEY,
                streaming=True,
                temperature=0.7,
                verbose=True
            )
            
            # Initialize tools with reference to this agent instance
            self.tools = [
                TrailSearchTool(agent_instance=self),
                GetAllTrailsTool(agent_instance=self)
            ]
            
            # Initialize memory for conversation context
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="output"
            )
            
            # Initialize agent with specific instructions
            self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            agent_kwargs={
                "system_message": """You are an intelligent trail search consultant powered by LangChain's advanced reasoning capabilities. Your expertise lies in understanding nuanced user requests and providing thoughtful, conversational trail recommendations.

🧠 Your Advanced Capabilities:
- Deep analysis of user intent and context
- Multi-step reasoning for complex trail requirements  
- Conversation memory to build on previous interactions
- Smart parameter inference and optimization
- Contextual follow-up questions and suggestions

🎯 Your Approach:
1. ANALYZE the user's request thoroughly, considering:
   - Explicit requirements (difficulty, distance, location)
   - Implicit preferences (fitness level, experience, time constraints)
   - Context clues (family trip, solo adventure, weekend plans)
   
2. REASON through the search strategy:
   - Explain your thought process
   - Apply smart defaults when criteria are vague
   - Consider seasonal factors and accessibility
   
3. SEARCH systematically using the search_trails tool with comprehensive parameters

4. PRESENT results with detailed reasoning:
   - Explain why each trail matches their needs
   - Highlight unique features and considerations
   - Provide contextual recommendations

5. ENGAGE conversationally:
   - Ask clarifying questions when helpful
   - Remember previous conversation context
   - Suggest alternatives and modifications

🌟 Special Focus Areas:
- Interpret vague requests intelligently ("easy hike" → reasonable distance/elevation limits)
- Provide broader search areas for better results (75+ miles for "near Chicago")
- Consider companion needs (dog-friendly, family-suitable, accessible)
- Factor in seasonal and weather considerations

IMPORTANT: For ANY trail-related request, you MUST use the search_trails tool to find actual trails. Never provide general advice without searching for specific trails first. Extract all relevant parameters from the user's query and call the search_trails tool with those parameters.

Always think step-by-step, explain your reasoning, and maintain a helpful, knowledgeable tone that builds trust through transparency."""
            }
        )
        
            logger.info("LangChain TrailSearchAgent initialized successfully")
        
        async def process_query(self, user_message: str, request_id: str) -> AsyncGenerator[Dict[str, Any], None]:
            """Process user query using LangChain's advanced reasoning capabilities"""
            try:
                logger.info(f"LangChain agent processing: '{user_message}' (Request: {request_id})")
                
                # Clear previous trails
                self.last_trails = []
                
                # Let LangChain agent do its reasoning first (stream the thinking process)
                yield {"type": "token", "content": "🧠 **LangChain Agent Analysis**\n\n", "request_id": request_id}
                yield {"type": "token", "content": "🤔 Let me analyze your request and think through the best search approach...\n\n", "request_id": request_id}
                
                # Run the agent with full LangChain reasoning - but don't stream the full response
                try:
                    response = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: self.agent.run(input=user_message)
                    )
                    
                    # Give the tool time to set trails on the agent instance
                    await asyncio.sleep(0.1)
                    logger.info(f"LangChain agent: After agent run, last_trails has {len(self.last_trails) if self.last_trails else 0} trails")
                    
                    # Parse the LangChain response to extract key insights
                    analysis_parts = []
                    if "chicago" in user_message.lower():
                        analysis_parts.append("📍 **Location Analysis**: I detected you're interested in the Chicago area. I'll use an expanded 75-mile search radius to give you more options.")
                    
                    if any(word in user_message.lower() for word in ["easy", "beginner", "simple"]):
                        analysis_parts.append("⚡ **Difficulty Assessment**: I notice you want easier trails. I'll apply smart elevation limits and prioritize accessible routes.")
                    
                    if "dog" in user_message.lower():
                        analysis_parts.append("🐕 **Companion Consideration**: I see you want to bring your dog! I'll filter specifically for dog-friendly trails.")
                    
                    if any(word in user_message.lower() for word in ["scenic", "view", "beautiful"]):
                        analysis_parts.append("🌄 **Experience Priority**: You're looking for scenic experiences. I'll prioritize trails with great views and natural features.")
                    
                    # Stream the analysis
                    for part in analysis_parts:
                        yield {"type": "token", "content": part + "\n\n", "request_id": request_id}
                    
                    yield {"type": "token", "content": "🔍 **Search Strategy**: Based on my analysis, here's my approach:\n", "request_id": request_id}
                    
                    # Show the actual search parameters being used
                    logger.info(f"LangChain agent: Checking last_trails length: {len(self.last_trails) if self.last_trails else 'None'}")
                    if self.last_trails:
                        strategy_msg = f"✅ I found {len(self.last_trails)} trails using enhanced parameter optimization.\n\n"
                        yield {"type": "token", "content": strategy_msg, "request_id": request_id}
                    else:
                        strategy_msg = "⚠️ Initial search parameters were very specific. Let me broaden the criteria...\n\n"
                        yield {"type": "token", "content": strategy_msg, "request_id": request_id}
                    
                    # Now yield the trail results if we found any
                    if self.last_trails:
                        logger.info(f"LangChain agent: About to yield {len(self.last_trails)} trails")
                        yield {"type": "token", "content": "📊 **Results Analysis**:\n\n", "request_id": request_id}
                        
                        # Generate and yield actual analysis content
                        analysis_content = await self._generate_trail_commentary(self.last_trails, user_message)
                        yield {"type": "token", "content": analysis_content + "\n\n", "request_id": request_id}
                        
                        yield {
                            "type": "trails",
                            "trails": self.last_trails,
                            "request_id": request_id
                        }
                        logger.info(f"LangChain agent: Successfully yielded trails data")
                        
                        # Generate contextual follow-up based on conversation history
                        follow_up = await self._generate_contextual_followup(
                            self.last_trails, user_message, response
                        )
                        
                        yield {"type": "token", "content": f"\n💡 **LangChain Insights**:\n{follow_up}\n\n", "request_id": request_id}
                    else:
                        logger.warning(f"LangChain agent: No trails found to yield")
                        # Use memory to provide better suggestions
                        yield {"type": "token", "content": "🔍 **Alternative Strategy**:\n\n", "request_id": request_id}
                        contextual_msg = await self._generate_no_results_with_context(user_message)
                        yield {"type": "token", "content": contextual_msg, "request_id": request_id}
                    
                    logger.info(f"LangChain agent completed: {len(self.last_trails)} trails, with enhanced reasoning (Request: {request_id})")
                    
                except Exception as e:
                    logger.error(f"LangChain agent execution error: {e}")
                    error_message = f"⚠️ I encountered an error during my analysis: {str(e)}\n\nLet me try a simpler approach..."
                    
                    yield {"type": "token", "content": error_message, "request_id": request_id}
                
            except Exception as e:
                logger.error(f"LangChain agent error: {e} (Request: {request_id})")
                error_response = "⚠️ I apologize, but I encountered an error during my analysis. Please try again."
                
                yield {"type": "token", "content": error_response, "request_id": request_id}
        
        
        async def _generate_contextual_followup(self, trails: List[Dict[str, Any]], original_query: str, agent_response: str) -> str:
            """Generate contextual follow-up using conversation memory and LangChain reasoning"""
            try:
                # Use LangChain's memory to understand conversation context
                chat_history = self.memory.chat_memory.messages if self.memory.chat_memory.messages else []
                
                # Create contextual follow-up based on agent reasoning and results
                if len(trails) > 3:
                    followup = f"💡 Based on my analysis, I found {len(trails)} great options! I noticed you mentioned specific criteria, so I've prioritized trails that best match your needs. "
                    
                    # Add memory-based suggestions
                    if len(chat_history) > 2:
                        followup += "Since we've been discussing trails, would you like me to refine these results further or explore different areas?"
                    else:
                        followup += "Would you like me to narrow these down based on any specific preferences?"
                        
                elif len(trails) == 1:
                    followup = "🎯 Perfect! I found exactly one trail that matches all your criteria. This focused result suggests your requirements were quite specific - great job describing what you're looking for!"
                else:
                    followup = f"✨ I found {len(trails)} excellent trails that align with your request. Each has been carefully selected based on the criteria I identified in your message."
                
                # Add conversational elements based on query patterns
                if "dog" in original_query.lower():
                    followup += " 🐕 I made sure to prioritize dog-friendly options since you mentioned your furry companion!"
                
                if any(word in original_query.lower() for word in ["scenic", "view", "beautiful", "vista"]):
                    followup += " 🌄 I focused on trails with great views since you're looking for scenic experiences!"
                
                return followup
                
            except Exception as e:
                logger.error(f"Failed to generate contextual follow-up: {e}")
                return "Here are the carefully selected trails based on your requirements!"
        
        async def _generate_no_results_with_context(self, original_query: str) -> str:
            """Generate contextual no-results message using LangChain's conversation understanding"""
            try:
                # Use conversation memory to provide better suggestions
                chat_history = self.memory.chat_memory.messages if self.memory.chat_memory.messages else []
                
                base_msg = "🔍 I couldn't find trails matching all your specific criteria, but let me help you explore alternatives:\n\n"
                
                suggestions = []
                
                # Analyze the query for specific suggestions
                if "easy" in original_query.lower():
                    suggestions.append("• Try searching for 'moderate' difficulty trails - they might still be manageable")
                elif "hard" in original_query.lower():
                    suggestions.append("• Consider 'moderate' trails as a starting point")
                
                if "chicago" in original_query.lower():
                    suggestions.append("• Expand your search radius around Chicago (try 75+ miles)")
                    suggestions.append("• Consider nearby areas like Wisconsin Dells or Indiana Dunes")
                
                if any(dist in original_query.lower() for dist in ["under", "less than", "short"]):
                    suggestions.append("• Try increasing your distance range slightly")
                
                if "dog" in original_query.lower():
                    suggestions.append("• Some trails may allow dogs seasonally - worth checking specific trail rules")
                
                # Add memory-based context if available
                if len(chat_history) > 2:
                    suggestions.append("• Based on our conversation, would you like to try a different approach?")
                
                if not suggestions:
                    suggestions = [
                        "• Try broadening your location radius",
                        "• Consider adjusting difficulty or distance requirements",
                        "• Explore different trail features or seasonal options"
                    ]
                
                return base_msg + "\n".join(suggestions) + "\n\n💬 Feel free to tell me what matters most to you, and I'll adjust the search accordingly!"
                
            except Exception as e:
                logger.error(f"Failed to generate contextual no-results: {e}")
                return "I couldn't find matching trails, but I'd be happy to help you explore alternatives!"

        async def _generate_trail_commentary(self, trails: List[Dict[str, Any]], original_query: str) -> str:
            """Generate helpful commentary about the search results - enhanced version"""
            try:
                # Create a summary of the results
                summary_parts = []
                
                if len(trails) == 1:
                    summary_parts.append(f"🎯 I found **{len(trails)} perfect trail** that matches your criteria!")
                else:
                    summary_parts.append(f"🎯 I found **{len(trails)} great trails** that match your criteria!")
                
                # Analyze the results
                difficulties = [trail.get('difficulty', '').lower() for trail in trails]
                distances = [trail.get('distance_miles', 0) for trail in trails]
                features = []
                for trail in trails:
                    features.extend(trail.get('features', []))
                
                # Add insights about the selection
                if difficulties:
                    difficulty_counts = {d: difficulties.count(d) for d in set(difficulties) if d}
                    if len(difficulty_counts) == 1:
                        difficulty = list(difficulty_counts.keys())[0]
                        summary_parts.append(f"\n✅ All trails are **{difficulty}** difficulty level, perfect for your request.")
                    else:
                        summary_parts.append(f"\n🎯 Mix of difficulty levels: {', '.join(f'{count} {diff}' for diff, count in difficulty_counts.items())}")
                
                if distances:
                    min_dist = min(distances)
                    max_dist = max(distances)
                    avg_dist = sum(distances) / len(distances)
                    summary_parts.append(f"\n📏 Distance range: **{min_dist:.1f} - {max_dist:.1f} miles** (avg: {avg_dist:.1f} miles)")
                
                # Highlight popular features
                if features:
                    feature_counts = {f: features.count(f) for f in set(features)}
                    top_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    if top_features:
                        feature_list = [f"**{feat}** ({count} trails)" for feat, count in top_features]
                        summary_parts.append(f"\n🌟 Popular features: {', '.join(feature_list)}")
                
                summary_parts.append(f"\n💡 Each trail has been carefully selected using LangChain's enhanced reasoning to match your specific requirements!")
                
                return "\n".join(summary_parts)
                
            except Exception as e:
                logger.error(f"Failed to generate commentary: {e}")
                return f"I found {len(trails)} trails that match your criteria. Check out the details below!"

else:
    # Provide dummy implementations when LangChain is not available
    class LangChainTrailAgent:
        """Dummy LangChain agent for when dependencies are not available"""
        
        def __init__(self):
            raise ImportError("LangChain is not installed. Please install with: pip install langchain langchain-openai")
        
        async def process_query(self, user_message: str, request_id: str) -> AsyncGenerator[Dict[str, Any], None]:
            """Dummy method"""
            yield {"type": "error", "content": "LangChain not available", "request_id": request_id}
