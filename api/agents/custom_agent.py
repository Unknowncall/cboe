"""
Custom AI Agent for Trail Search using Direct OpenAI API

This module implements a custom AI agent that directly uses OpenAI API
with function calling for trail search and recommendations.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, AsyncGenerator, Optional
from dataclasses import dataclass
import openai
from openai.types.chat import ChatCompletionChunk

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_COMPLETION_TOKENS
from search import trail_searcher
from models import ParsedFilters, Trail
from utils import generate_request_id

logger = logging.getLogger("trail_search.custom_agent")

@dataclass
class AgentTool:
    """Represents a tool available to the AI agent"""
    name: str
    description: str
    function: callable
    schema: Dict[str, Any]

class CustomTrailAgent:
    """
    Custom AI agent for intelligent trail search and recommendations.
    
    Uses direct OpenAI API with function calling to understand user queries
    and provide contextual trail recommendations using available search tools.
    """
    
    def __init__(self):
        # Log API key status for debugging
        if OPENAI_API_KEY:
            logger.info("OpenAI API key configured successfully")
        else:
            logger.error("OPENAI_API_KEY environment variable is not set!")
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        self.client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.tools = self._register_tools()
        self.model = OPENAI_MODEL
        self.max_tokens = OPENAI_MAX_COMPLETION_TOKENS

        # Model fallback order
        self.model_fallbacks = [
            OPENAI_MODEL,
        ]
        
        logger.info(f"Initialized CustomTrailAgent with primary model {self.model}")
    
    async def _try_model(self, model_name: str, messages: list, tools: list) -> bool:
        """Try a specific model and return True if successful"""
        logger.info(f"Attempting to use model: {model_name} with API key: {OPENAI_API_KEY[:8] if OPENAI_API_KEY else 'None'}...")
        
        # Add retry logic for rate limiting
        max_retries = 3
        base_delay = 1  # Start with 1 second delay
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries} for model {model_name} after {delay}s delay")
                    await asyncio.sleep(delay)
                
                response = await self.client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    stream=True,
                    max_tokens=self.max_tokens,
                    temperature=0.7,
                    timeout=30.0
                )
                # If we get here, the model works
                logger.info(f"Successfully connected to model: {model_name}")
                return True, response
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Attempt {attempt + 1}/{max_retries} - Full error details for model {model_name}: {error_msg}")
                
                # Check if this is a retryable error
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    if attempt < max_retries - 1:  # Don't sleep on the last attempt
                        logger.warning(f"Model {model_name} hit rate limit, will retry in {base_delay * (2 ** (attempt + 1))}s")
                        continue
                    else:
                        logger.error(f"Model {model_name} failed after {max_retries} attempts due to rate limiting")
                elif "insufficient_quota" in error_msg or "exceeded your current quota" in error_msg:
                    logger.warning(f"Model {model_name} failed due to quota limit: {e}")
                    break  # Don't retry quota errors
                elif "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                    logger.error(f"Model {model_name} failed due to invalid API key: {e}")
                    break  # Don't retry auth errors
                else:
                    logger.warning(f"Model {model_name} failed: {e}")
                    break  # Don't retry other errors
        
        return False, None
    
    def _register_tools(self) -> List[Dict[str, Any]]:
        """Register available tools for the agent"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_trails",
                    "description": "Search for hiking trails based on user criteria like location, difficulty, distance, and features. Extract all relevant parameters from the user's natural language query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The user's natural language query about trails"
                            },
                            "location": {
                                "type": "string", 
                                "description": "General location or city name to search near (e.g., 'Chicago', 'near Chicago'). Use this for cities, landmarks, or general areas. DO NOT use for state names - use the 'state' parameter for state names like Wisconsin, Illinois, etc."
                            },
                            "max_distance_miles": {
                                "type": "number",
                                "description": "Maximum trail length in miles. ONLY use this when the user explicitly says 'under X miles', 'less than X miles', 'max X miles', 'no more than X miles', 'shorter than X miles', 'below X miles', etc. This sets an UPPER BOUND - trails must be this distance or shorter. DO NOT use for 'greater than' or 'more than' queries."
                            },
                            "min_distance_miles": {
                                "type": "number",
                                "description": "Minimum trail length in miles. Use this when the user says 'more than X miles', 'over X miles', 'at least X miles', 'longer than X miles', 'greater than X miles', 'bigger than X miles', 'above X miles', etc. This sets a LOWER BOUND - trails must be this distance or longer."
                            },
                            "max_elevation_gain_m": {
                                "type": "number",
                                "description": "Maximum elevation gain in meters if specified"
                            },
                            "difficulty": {
                                "type": "string",
                                "enum": ["easy", "moderate", "hard"],
                                "description": "Trail difficulty level if specified"
                            },
                            "route_type": {
                                "type": "string",
                                "enum": ["loop", "out and back"],
                                "description": "Type of trail route if specified"
                            },
                            "dogs_allowed": {
                                "type": "boolean",
                                "description": "Whether dogs are allowed/wanted on the trail. True if user mentions bringing/taking their dog, wants dog-friendly trails, etc."
                            },
                            "features": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Desired trail features extracted from the query like 'waterfall', 'lake', 'scenic', 'views', 'forest', 'prairie', 'beach', 'canyon', 'historic', etc."
                            },
                            "radius_miles": {
                                "type": "number",
                                "description": "Search radius in miles from the specified location if mentioned"
                            },
                            "city": {
                                "type": "string",
                                "description": "Specific city name if mentioned (e.g., 'Chicago', 'Milwaukee')"
                            },
                            "county": {
                                "type": "string",
                                "description": "County name if mentioned (e.g., 'Cook County', 'DuPage County')"
                            },
                            "state": {
                                "type": "string",
                                "description": "State name when specifically mentioned (e.g., 'Illinois', 'Wisconsin', 'Michigan'). ALWAYS use this parameter for state names like Wisconsin, Illinois, Michigan, etc. Do not use 'location' for state names."
                            },
                            "region": {
                                "type": "string",
                                "description": "Region name if mentioned (e.g., 'Great Lakes', 'Chicago Metropolitan')"
                            },
                            "parking_available": {
                                "type": "boolean",
                                "description": "True if user specifically mentions needing parking available"
                            },
                            "parking_type": {
                                "type": "string",
                                "enum": ["free", "paid", "limited", "street"],
                                "description": "Type of parking if specified (free, paid, limited, street parking)"
                            },
                            "restrooms": {
                                "type": "boolean",
                                "description": "True if user specifically mentions needing restrooms/facilities"
                            },
                            "water_available": {
                                "type": "boolean",
                                "description": "True if user mentions needing water fountains or water availability"
                            },
                            "picnic_areas": {
                                "type": "boolean",
                                "description": "True if user mentions wanting picnic areas or tables"
                            },
                            "camping_available": {
                                "type": "boolean",
                                "description": "True if user mentions camping or overnight stays"
                            },
                            "entry_fee": {
                                "type": "boolean",
                                "description": "True if user is okay with entry fees, False if they want free trails or mention no fees"
                            },
                            "permit_required": {
                                "type": "boolean",
                                "description": "True if user is okay with permits, False if they want no permit required"
                            },
                            "seasonal_access": {
                                "type": "string",
                                "enum": ["year-round", "seasonal", "summer", "winter"],
                                "description": "Seasonal access preference if mentioned"
                            },
                            "accessibility": {
                                "type": "string",
                                "enum": ["wheelchair", "stroller", "none"],
                                "description": "Accessibility requirements if mentioned (wheelchair accessible, stroller friendly, etc.)"
                            },
                            "surface_type": {
                                "type": "string",
                                "enum": ["paved", "gravel", "dirt", "boardwalk", "mixed"],
                                "description": "Preferred trail surface type if mentioned"
                            },
                            "trail_markers": {
                                "type": "boolean",
                                "description": "True if user mentions wanting well-marked trails or good signage"
                            },
                            "loop_trail": {
                                "type": "boolean",
                                "description": "True if user specifically wants loop trails, False if they prefer out-and-back"
                            },
                            "managing_agency": {
                                "type": "string",
                                "description": "Managing agency or park system if mentioned (e.g., 'National Park Service', 'Illinois State Parks', 'Chicago Park District')"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_trails",
                    "description": "Get all trails in the database. Use this when users ask to see 'all trails', 'show me all trails', 'list all trails', or want to browse all available trails. Can optionally filter by area/location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The user's natural language query"
                            },
                            "area_filter": {
                                "type": "string",
                                "description": "Optional area name to filter trails by (e.g., 'Chicago', 'Illinois', 'Cook County'). Extract from user query if they mention a specific area."
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of trails to return (default: 50, max: 100)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    async def process_query(self, user_message: str, request_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Main agent reasoning loop with streaming responses.
        
        Processes user queries, calls appropriate tools, and streams back
        both reasoning and results in real-time.
        """
        logger.info(f"Processing query: '{user_message}' (Request: {request_id})")
        
        try:
            # Stream initial identifier
            yield {"type": "token", "content": "⚡ **Custom Agent** - Direct OpenAI API\n\n", "request_id": request_id}
            
            # System prompt defines the agent's role and behavior
            system_prompt = """You are a helpful and knowledgeable trail search assistant. Your job is to help users find the perfect hiking trails based on their specific needs and preferences.

Key responsibilities:
- Carefully analyze user queries to determine the appropriate tool to use
- Use the search_trails tool when users have specific criteria (difficulty, features, distance, etc.)
- Use the get_all_trails tool when users want to see all available trails or browse all trails
- Provide personalized recommendations based on user criteria
- Explain why certain trails match their requirements
- Be conversational and helpful in your responses

Tool Selection Guidelines:
- Use get_all_trails when users say: "show me all trails", "list all trails", "what trails do you have", "browse all trails", "all trails in [area]", or similar browsing requests
- Use search_trails when users have specific criteria like difficulty, features, distance, location preferences, etc.

When users ask about trails:
1. First determine if this is a browsing request (get_all_trails) or a specific search (search_trails)

2. For specific searches (search_trails), extract ALL relevant criteria:
   - Difficulty level (easy/moderate/hard)
   - Distance preferences (if they mention "under X miles" or similar)
   - Location preferences (near Chicago, etc.)
   - Trail features (scenic, waterfall, lake, forest, prairie, views, etc.)
   - Dog policy (if they mention bringing/taking their dog, wanting dog-friendly trails)
   - Route type (loop vs out and back)
   - Elevation preferences
   - Search radius

3. For browsing requests (get_all_trails), extract:
   - Area filter if they mention a specific location ("all trails in Chicago")
   - Limit if they specify how many trails they want to see

4. Present results in a friendly, informative way explaining matches or providing overview
5. Offer additional suggestions or ask clarifying questions if needed

Pay special attention to:
- Browsing keywords: "all trails", "show me all", "list all", "what trails", "browse", "all available"
- Dog-related keywords: "take my dog", "bring my dog", "with my dog", "dog-friendly"
- Scenic keywords: "scenic", "views", "beautiful", "vista", "panoramic", "overlook"
- Distance keywords: "under X miles", "less than", "max", "short", "long"
- Location keywords: "near Chicago", "around Chicago", "Chicago area", "in Illinois"

Always be encouraging and helpful, even if search results are limited."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Try the configured model only
            response = None
            working_model = None
            
            logger.info(f"Trying model: {self.model}")
            success, response = await self._try_model(self.model, messages, self.tools)
            if success:
                working_model = self.model
                logger.info(f"Successfully using model: {self.model}")
            
            if not response:
                logger.error(f"Model {self.model} failed - no fallback configured")
                raise Exception(f"Configured model {self.model} is not available")
            
            # Process streaming response
            tool_calls = []
            content_buffer = ""
            current_tool_call = None
            
            async for chunk in response:
                if not chunk.choices:
                    continue
                    
                choice = chunk.choices[0]
                delta = choice.delta
                
                # Handle content streaming
                if delta.content:
                    content_buffer += delta.content
                    yield {
                        "type": "token",
                        "content": delta.content,
                        "request_id": request_id
                    }
                
                # Handle tool calls
                if delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        if tool_call_delta.index is not None:
                            # Ensure we have enough slots in our tool_calls list
                            while len(tool_calls) <= tool_call_delta.index:
                                tool_calls.append({
                                    "id": "",
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""}
                                })
                            
                            current_tool_call = tool_calls[tool_call_delta.index]
                            
                            if tool_call_delta.id:
                                current_tool_call["id"] = tool_call_delta.id
                            
                            if tool_call_delta.function:
                                if tool_call_delta.function.name:
                                    current_tool_call["function"]["name"] = tool_call_delta.function.name
                                if tool_call_delta.function.arguments:
                                    current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments
            
            # Execute any tool calls
            if tool_calls:
                for tool_call in tool_calls:
                    if tool_call["function"]["name"] == "search_trails":
                        try:
                            # Parse tool arguments
                            args = json.loads(tool_call["function"]["arguments"])
                            
                            # Execute trail search and capture tool traces
                            yield {"type": "token", "content": "🔍 Searching for trails...\n\n", "request_id": request_id}
                            
                            # Execute trail search and collect results and tool traces
                            trails = []
                            async for search_chunk in self._execute_trail_search_with_traces(
                                args.get("query", user_message),
                                args,
                                request_id
                            ):
                                if search_chunk["type"] == "tool_trace":
                                    yield search_chunk
                                elif search_chunk["type"] == "trails":
                                    trails = search_chunk["trails"]
                            
                            # Stream trail results
                            yield {
                                "type": "trails",
                                "trails": trails,  # trails are already dictionaries from search
                                "request_id": request_id
                            }
                            
                            # Generate follow-up commentary about results
                            if trails:
                                commentary = await self._generate_trail_commentary(
                                    trails, user_message, args
                                )
                                yield {"type": "token", "content": commentary}
                            else:
                                # Generate helpful no-results message with suggestions
                                no_results_message = self._generate_no_results_message(args, user_message)
                                yield {
                                    "type": "token", 
                                    "content": no_results_message
                                }
                                
                        except Exception as e:
                            logger.error(f"Tool execution failed: {e} (Request: {request_id})")
                            yield {
                                "type": "token",
                                "content": f"\n\nI encountered an error while searching for trails: {str(e)}"
                            }
                    
                    elif tool_call["function"]["name"] == "get_all_trails":
                        try:
                            # Parse tool arguments
                            args = json.loads(tool_call["function"]["arguments"])
                            
                            # Execute get all trails and capture tool traces
                            area_filter = args.get("area_filter")
                            if area_filter:
                                yield {"type": "token", "content": f"📋 Getting all trails in {area_filter}...\n\n", "request_id": request_id}
                            else:
                                yield {"type": "token", "content": "📋 Getting all available trails...\n\n", "request_id": request_id}
                            
                            # Execute get all trails and collect results and tool traces
                            trails = []
                            async for search_chunk in self._execute_get_all_trails_with_traces(
                                args.get("query", user_message),
                                args,
                                request_id
                            ):
                                if search_chunk["type"] == "tool_trace":
                                    yield search_chunk
                                elif search_chunk["type"] == "trails":
                                    trails = search_chunk["trails"]
                            
                            # Stream trail results
                            yield {
                                "type": "trails",
                                "trails": trails,
                                "request_id": request_id
                            }
                            
                            # Generate follow-up commentary about results
                            if trails:
                                area_text = f" in {area_filter}" if area_filter else ""
                                commentary = f"\n\n✅ **Found {len(trails)} trails{area_text}**\n\n"
                                commentary += "Here are all the available trails, organized by difficulty level (easy → moderate → hard):\n\n"
                                yield {"type": "token", "content": commentary}
                            else:
                                area_text = f" in {area_filter}" if area_filter else ""
                                no_results_message = f"I couldn't find any trails{area_text}. There might be no trails in the database for this area. Try searching for a broader region or specific trail names."
                                yield {
                                    "type": "token", 
                                    "content": no_results_message
                                }
                                
                        except Exception as e:
                            logger.error(f"Get all trails tool execution failed: {e} (Request: {request_id})")
                            yield {
                                "type": "token",
                                "content": f"\n\nI encountered an error while getting all trails: {str(e)}"
                            }
            
            # If no tool calls were made, we still had a conversation
            if not tool_calls and content_buffer:
                logger.info(f"Completed conversational response without tools (Request: {request_id})")
            
        except Exception as e:
            logger.error(f"Agent processing failed: {e} (Request: {request_id})")
            yield {
                "type": "token",
                "content": "I apologize, but I encountered an error while processing your request. Please try rephrasing your query or try again later."
            }
    
    async def _execute_trail_search_with_traces(self, query: str, args: Dict[str, Any], request_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute trail search with comprehensive tool tracing and yield both results and traces.
        """
        from utils import PerformanceTimer
        import time
        
        # Start comprehensive tool trace
        tool_trace = {
            "tool": "ai_trail_search",
            "input_parameters": args.copy(),
            "reasoning": "",
            "function_call": {
                "name": "search_trails",
                "arguments": args,
                "extraction_confidence": 0.8  # Default confidence
            },
            "search_filters": {},
            "database_query": "",
            "ai_confidence": 0.0,
            "processing_steps": [],
            "errors": [],
            "success": False,
            "duration_ms": 0,
            "result_count": 0
        }

        try:
            start_time = time.time()
            
            # Step 1: Analyze and validate extracted parameters
            tool_trace["processing_steps"].append("🧠 Analyzing extracted parameters from user query")
            
            # Build reasoning explanation
            reasoning_parts = []
            reasoning_parts.append(f"**Query Analysis**: '{query}'")
            
            # Analyze each parameter and build confidence
            confidence_factors = []
            
            if args.get("location"):
                reasoning_parts.append(f"📍 **Location**: {args['location']}")
                confidence_factors.append(0.9)  # High confidence for explicit location
            
            if args.get("difficulty"):
                reasoning_parts.append(f"🎯 **Difficulty**: {args['difficulty']} (interpreted from user language)")
                confidence_factors.append(0.8)
            
            if args.get("max_distance_miles"):
                reasoning_parts.append(f"📏 **Distance Limit**: Under {args['max_distance_miles']} miles")
                confidence_factors.append(0.9)
            
            if args.get("min_distance_miles"):
                reasoning_parts.append(f"📏 **Minimum Distance**: Over {args['min_distance_miles']} miles")
                confidence_factors.append(0.9)
            
            if args.get("dogs_allowed") is not None:
                dog_status = "required (user mentioned bringing dog)" if args["dogs_allowed"] else "not specified"
                reasoning_parts.append(f"🐕 **Dog Policy**: {dog_status}")
                confidence_factors.append(0.85)
            
            if args.get("route_type"):
                reasoning_parts.append(f"🔄 **Route Type**: {args['route_type']}")
                confidence_factors.append(0.7)
            
            if args.get("features"):
                features_str = ", ".join(args["features"])
                reasoning_parts.append(f"🌟 **Features**: {features_str}")
                confidence_factors.append(0.75)
            
            if args.get("radius_miles"):
                reasoning_parts.append(f"📐 **Search Radius**: {args['radius_miles']} miles")
                confidence_factors.append(0.8)
            
            # Calculate overall confidence
            tool_trace["ai_confidence"] = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            tool_trace["reasoning"] = "\n".join(reasoning_parts)
            
            tool_trace["processing_steps"].append(f"✅ Parameter extraction complete (confidence: {tool_trace['ai_confidence']:.2f})")
            
            # Step 2: Convert AI parameters to search filters
            tool_trace["processing_steps"].append("🔄 Converting AI parameters to database search filters")
            
            filters = ParsedFilters()
            
            # Map AI extracted parameters to database filters
            if args.get("max_distance_miles"):
                filters.distance_cap_miles = float(args["max_distance_miles"])
            
            if args.get("min_distance_miles"):
                filters.distance_min_miles = float(args["min_distance_miles"])
            
            if args.get("max_elevation_gain_m"):
                filters.elevation_cap_m = int(args["max_elevation_gain_m"])
            
            if args.get("difficulty"):
                filters.difficulty = args["difficulty"].lower()
            
            if args.get("route_type"):
                filters.route_type = args["route_type"].lower()
            
            if args.get("features"):
                filters.features = args["features"]
            
            if args.get("dogs_allowed") is not None:
                filters.dogs_allowed = args["dogs_allowed"]
            
            if args.get("radius_miles"):
                filters.radius_miles = float(args["radius_miles"])

            # Location filters
            if args.get("city"):
                filters.city = args["city"]
            
            if args.get("county"):
                filters.county = args["county"]
            
            if args.get("state"):
                filters.state = args["state"]
            
            if args.get("region"):
                filters.region = args["region"]
            
            # Amenity filters
            if args.get("parking_available") is not None:
                filters.parking_available = args["parking_available"]
            
            if args.get("parking_type"):
                filters.parking_type = args["parking_type"]
            
            if args.get("restrooms") is not None:
                filters.restrooms = args["restrooms"]
            
            if args.get("water_available") is not None:
                filters.water_available = args["water_available"]
            
            if args.get("picnic_areas") is not None:
                filters.picnic_areas = args["picnic_areas"]
            
            if args.get("camping_available") is not None:
                filters.camping_available = args["camping_available"]
            
            # Access and permit filters
            if args.get("entry_fee") is not None:
                filters.entry_fee = args["entry_fee"]
            
            if args.get("permit_required") is not None:
                filters.permit_required = args["permit_required"]
            
            if args.get("seasonal_access"):
                filters.seasonal_access = args["seasonal_access"]
            
            if args.get("accessibility"):
                filters.accessibility = args["accessibility"]
            
            # Trail characteristics
            if args.get("surface_type"):
                filters.surface_type = args["surface_type"]
            
            if args.get("trail_markers") is not None:
                filters.trail_markers = args["trail_markers"]
            
            if args.get("loop_trail") is not None:
                filters.loop_trail = args["loop_trail"]
            
            if args.get("managing_agency"):
                filters.managing_agency = args["managing_agency"]

            # Handle location (default to Chicago if not specified)
            if args.get("location"):
                location = args["location"].lower()
                
                # Check if location is actually a state name
                state_names = ['wisconsin', 'illinois', 'michigan', 'indiana', 'iowa', 'minnesota', 'ohio']
                if location in state_names:
                    # Map location to state filter
                    filters.state = args["location"]
                    tool_trace["processing_steps"].append(f"📍 Location '{args['location']}' mapped to state filter")
                elif "chicago" in location:
                    filters.center_lat = 41.8781
                    filters.center_lng = -87.6298
                    if not filters.radius_miles:
                        filters.radius_miles = 50  # Default 50 mile radius around Chicago
                    tool_trace["processing_steps"].append(f"📍 Location mapped to Chicago coordinates (41.8781, -87.6298)")
                else:
                    # For other locations, try to map them as cities or general areas
                    # This could be expanded in the future for other cities
                    tool_trace["processing_steps"].append(f"📍 General location '{args['location']}' noted but not specifically mapped")
            
            tool_trace["search_filters"] = filters.model_dump()
            active_filters = len([k for k,v in filters.model_dump().items() if v is not None and v != [] and v != ""])
            tool_trace["processing_steps"].append(f"🎯 Search filters configured: {active_filters} active filters")
            
            # Step 3: Execute database search
            tool_trace["processing_steps"].append("🔍 Executing database search with generated filters")
            
            # Use the trail searcher to perform the actual search
            trails = trail_searcher.search_trails(query, filters, request_id)
            
            # Capture database query information (simulated for this example)
            query_parts = []
            if filters.difficulty:
                query_parts.append(f"difficulty = '{filters.difficulty}'")
            if filters.distance_cap_miles:
                query_parts.append(f"distance_miles <= {filters.distance_cap_miles}")
            if filters.dogs_allowed is not None:
                query_parts.append(f"dogs_allowed = {filters.dogs_allowed}")
            if filters.features:
                query_parts.append(f"features MATCH '{' OR '.join(filters.features)}'")
            if filters.center_lat and filters.center_lng and filters.radius_miles:
                query_parts.append(f"distance_from_point({filters.center_lat}, {filters.center_lng}) <= {filters.radius_miles}")
            
            tool_trace["database_query"] = f"SELECT * FROM trails WHERE {' AND '.join(query_parts)}" if query_parts else "SELECT * FROM trails"
            
            # Step 4: Analyze and rank results
            tool_trace["processing_steps"].append(f"📊 Found {len(trails)} trails, analyzing relevance")
            
            if trails:
                # Add relevance scoring explanation
                tool_trace["processing_steps"].append("🏆 Ranking results by relevance to user query")
                
                # Enhance trail data with AI reasoning
                for trail in trails:
                    if not trail.get("why"):
                        # Generate explanation for why this trail matches
                        match_reasons = []
                        
                        if filters.difficulty and trail.get("difficulty") == filters.difficulty:
                            match_reasons.append(f"matches {filters.difficulty} difficulty preference")
                        
                        if filters.distance_cap_miles and trail.get("distance_miles", 0) <= filters.distance_cap_miles:
                            match_reasons.append(f"distance ({trail.get('distance_miles', 0)} miles) is within your {filters.distance_cap_miles} mile limit")
                        
                        if filters.dogs_allowed and trail.get("dogs_allowed"):
                            match_reasons.append("allows dogs as requested")
                        
                        if filters.features:
                            trail_features = trail.get("features", [])
                            matching_features = [f for f in filters.features if f.lower() in [tf.lower() for tf in trail_features]]
                            if matching_features:
                                match_reasons.append(f"has desired features: {', '.join(matching_features)}")
                        
                        trail["why"] = f"This trail {', '.join(match_reasons)}." if match_reasons else "This trail matches your general search criteria."
                
                # Add ranking details to processing steps
                if len(trails) > 1:
                    tool_trace["processing_steps"].append(f"📈 Results ranked by: distance match, feature relevance, difficulty alignment")
                
            else:
                tool_trace["processing_steps"].append("⚠️ No trails found matching all criteria, consider broadening search")
            
            tool_trace["result_count"] = len(trails)
            tool_trace["processing_steps"].append(f"✅ Search completed successfully with {len(trails)} relevant results")
            tool_trace["success"] = True
            
            # Record final timing
            end_time = time.time()
            tool_trace["duration_ms"] = int((end_time - start_time) * 1000)
            
            # Yield the comprehensive tool trace
            yield {
                "type": "tool_trace",
                "tool_trace": tool_trace,
                "request_id": request_id
            }
            
            # Yield the trails result
            yield {
                "type": "trails",
                "trails": trails,
                "request_id": request_id
            }
            
            # Log the comprehensive tool trace
            logger.info(f"AI Trail Search Tool Trace (Request: {request_id}): {json.dumps(tool_trace, default=str)}")
            
        except Exception as e:
            end_time = time.time()
            tool_trace["success"] = False
            tool_trace["errors"].append(str(e))
            tool_trace["processing_steps"].append(f"❌ Search failed: {str(e)}")
            tool_trace["duration_ms"] = int((end_time - start_time) * 1000) if 'start_time' in locals() else 0
            
            # Yield error tool trace
            yield {
                "type": "tool_trace",
                "tool_trace": tool_trace,
                "request_id": request_id
            }
            
            logger.error(f"AI trail search failed (Request: {request_id}): {e}")

    async def _execute_get_all_trails_with_traces(self, query: str, args: Dict[str, Any], request_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute get all trails with comprehensive tool tracing and yield both results and traces.
        """
        from database import db_manager
        from utils import PerformanceTimer
        import time
        
        # Start comprehensive tool trace
        tool_trace = {
            "tool": "get_all_trails",
            "input_parameters": args.copy(),
            "reasoning": "",
            "function_call": {
                "name": "get_all_trails",
                "arguments": args,
                "extraction_confidence": 0.9  # High confidence for simple all trails request
            },
            "search_filters": {},
            "database_query": "",
            "ai_confidence": 0.9,
            "processing_steps": [],
            "errors": [],
            "success": False,
            "duration_ms": 0,
            "result_count": 0
        }
        
        try:
            start_time = time.time()
            
            # Step 1: Analyze and validate extracted parameters
            tool_trace["processing_steps"].append("🧠 Analyzing request to get all trails")
            
            # Build reasoning explanation
            reasoning_parts = []
            reasoning_parts.append(f"**Query Analysis**: '{query}'")
            
            area_filter = args.get("area_filter")
            limit = args.get("limit", 100)
            
            if area_filter:
                reasoning_parts.append(f"📍 **Area Filter**: {area_filter}")
                tool_trace["search_filters"]["area_filter"] = area_filter
            else:
                reasoning_parts.append("🌍 **Scope**: All available trails")
            
            reasoning_parts.append(f"📊 **Limit**: {limit} trails maximum")
            tool_trace["search_filters"]["limit"] = limit
            
            # Compile reasoning
            tool_trace["reasoning"] = "\n".join(reasoning_parts)
            
            # Step 2: Execute database query
            tool_trace["processing_steps"].append("🔍 Querying database for all trails")
            
            try:
                trails = db_manager.get_all_trails(
                    limit=limit, 
                    area_filter=area_filter, 
                    request_id=request_id
                )
                
                tool_trace["processing_steps"].append(f"✅ Database query successful: {len(trails)} trails found")
                tool_trace["result_count"] = len(trails)
                
            except Exception as db_error:
                error_msg = f"Database query failed: {str(db_error)}"
                tool_trace["errors"].append(error_msg)
                tool_trace["processing_steps"].append(f"❌ {error_msg}")
                raise db_error
            
            # Step 3: Format results
            tool_trace["processing_steps"].append("📋 Formatting trail results")
            
            # Trails are already formatted from database manager
            formatted_trails = trails
            
            # Step 4: Finalize tool trace
            end_time = time.time()
            tool_trace["success"] = True
            tool_trace["duration_ms"] = int((end_time - start_time) * 1000)
            tool_trace["processing_steps"].append(f"🎯 Successfully retrieved {len(formatted_trails)} trails")
            
            # Yield tool trace
            yield {
                "type": "tool_trace",
                "tool_trace": tool_trace,
                "request_id": request_id
            }
            
            # Yield results
            yield {
                "type": "trails",
                "trails": formatted_trails,
                "request_id": request_id
            }
            
            # Log the comprehensive tool trace
            logger.info(f"Get All Trails Tool Trace (Request: {request_id}): {json.dumps(tool_trace, default=str)}")
            
        except Exception as e:
            end_time = time.time()
            tool_trace["success"] = False
            tool_trace["errors"].append(str(e))
            tool_trace["processing_steps"].append(f"❌ Get all trails failed: {str(e)}")
            tool_trace["duration_ms"] = int((end_time - start_time) * 1000) if 'start_time' in locals() else 0
            
            # Yield error tool trace
            yield {
                "type": "tool_trace",
                "tool_trace": tool_trace,
                "request_id": request_id
            }
            
            logger.error(f"Get all trails failed (Request: {request_id}): {e}")

    async def _execute_trail_search(self, query: str, args: Dict[str, Any], request_id: str) -> List[Dict[str, Any]]:
        """
        Execute trail search with comprehensive tool tracing and reasoning capture.
        
        This method provides detailed insights into the AI's decision-making process,
        including parameter extraction, search strategy, and result selection.
        """
        from utils import PerformanceTimer
        import time
        
        # Start comprehensive tool trace
        tool_trace = {
            "tool": "ai_trail_search",
            "input_parameters": args.copy(),
            "reasoning": "",
            "function_call": {
                "name": "search_trails",
                "arguments": args,
                "extraction_confidence": 0.8  # Default confidence
            },
            "search_filters": {},
            "database_query": "",
            "ai_confidence": 0.0,
            "processing_steps": [],
            "errors": [],
            "success": False,
            "duration_ms": 0,
            "result_count": 0
        }

        try:
            start_time = time.time()
            
            # Step 1: Analyze and validate extracted parameters
            tool_trace["processing_steps"].append("🧠 Analyzing extracted parameters from user query")
            
            # Build reasoning explanation
            reasoning_parts = []
            reasoning_parts.append(f"**Query Analysis**: '{query}'")
            
            # Analyze each parameter and build confidence
            confidence_factors = []
            
            if args.get("location"):
                reasoning_parts.append(f"📍 **Location**: {args['location']}")
                confidence_factors.append(0.9)  # High confidence for explicit location
            
            if args.get("difficulty"):
                reasoning_parts.append(f"🎯 **Difficulty**: {args['difficulty']} (interpreted from user language)")
                confidence_factors.append(0.8)
            
            if args.get("max_distance_miles"):
                reasoning_parts.append(f"📏 **Distance Limit**: Under {args['max_distance_miles']} miles")
                confidence_factors.append(0.9)
            
            if args.get("min_distance_miles"):
                reasoning_parts.append(f"📏 **Minimum Distance**: Over {args['min_distance_miles']} miles")
                confidence_factors.append(0.9)
            
            if args.get("dogs_allowed") is not None:
                dog_status = "required (user mentioned bringing dog)" if args["dogs_allowed"] else "not specified"
                reasoning_parts.append(f"🐕 **Dog Policy**: {dog_status}")
                confidence_factors.append(0.85)
            
            if args.get("route_type"):
                reasoning_parts.append(f"🔄 **Route Type**: {args['route_type']}")
                confidence_factors.append(0.7)
            
            if args.get("features"):
                features_str = ", ".join(args["features"])
                reasoning_parts.append(f"🌟 **Features**: {features_str}")
                confidence_factors.append(0.75)
            
            if args.get("radius_miles"):
                reasoning_parts.append(f"📐 **Search Radius**: {args['radius_miles']} miles")
                confidence_factors.append(0.8)
            
            # Calculate overall confidence
            tool_trace["ai_confidence"] = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            tool_trace["reasoning"] = "\n".join(reasoning_parts)
            
            tool_trace["processing_steps"].append(f"✅ Parameter extraction complete (confidence: {tool_trace['ai_confidence']:.2f})")
            
            # Step 2: Convert AI parameters to search filters
            tool_trace["processing_steps"].append("🔄 Converting AI parameters to database search filters")
            
            filters = ParsedFilters()
            
            # Map AI extracted parameters to database filters
            if args.get("max_distance_miles"):
                filters.distance_cap_miles = float(args["max_distance_miles"])
            
            if args.get("min_distance_miles"):
                filters.distance_min_miles = float(args["min_distance_miles"])
            
            if args.get("max_elevation_gain_m"):
                filters.elevation_cap_m = int(args["max_elevation_gain_m"])
            
            if args.get("difficulty"):
                filters.difficulty = args["difficulty"].lower()
            
            if args.get("route_type"):
                filters.route_type = args["route_type"].lower()
            
            if args.get("features"):
                filters.features = args["features"]
            
            if args.get("dogs_allowed") is not None:
                filters.dogs_allowed = args["dogs_allowed"]
            
            if args.get("radius_miles"):
                filters.radius_miles = float(args["radius_miles"])

            # Location filters
            if args.get("city"):
                filters.city = args["city"]
            
            if args.get("county"):
                filters.county = args["county"]
            
            if args.get("state"):
                filters.state = args["state"]
            
            if args.get("region"):
                filters.region = args["region"]
            
            # Amenity filters
            if args.get("parking_available") is not None:
                filters.parking_available = args["parking_available"]
            
            if args.get("parking_type"):
                filters.parking_type = args["parking_type"]
            
            if args.get("restrooms") is not None:
                filters.restrooms = args["restrooms"]
            
            if args.get("water_available") is not None:
                filters.water_available = args["water_available"]
            
            if args.get("picnic_areas") is not None:
                filters.picnic_areas = args["picnic_areas"]
            
            if args.get("camping_available") is not None:
                filters.camping_available = args["camping_available"]
            
            # Access and permit filters
            if args.get("entry_fee") is not None:
                filters.entry_fee = args["entry_fee"]
            
            if args.get("permit_required") is not None:
                filters.permit_required = args["permit_required"]
            
            if args.get("seasonal_access"):
                filters.seasonal_access = args["seasonal_access"]
            
            if args.get("accessibility"):
                filters.accessibility = args["accessibility"]
            
            # Trail characteristics
            if args.get("surface_type"):
                filters.surface_type = args["surface_type"]
            
            if args.get("trail_markers") is not None:
                filters.trail_markers = args["trail_markers"]
            
            if args.get("loop_trail") is not None:
                filters.loop_trail = args["loop_trail"]
            
            if args.get("managing_agency"):
                filters.managing_agency = args["managing_agency"]

            # Handle location (default to Chicago if not specified)
            if args.get("location"):
                location = args["location"].lower()
                
                # Check if location is actually a state name
                state_names = ['wisconsin', 'illinois', 'michigan', 'indiana', 'iowa', 'minnesota', 'ohio']
                if location in state_names:
                    # Map location to state filter
                    filters.state = args["location"]
                    tool_trace["processing_steps"].append(f"📍 Location '{args['location']}' mapped to state filter")
                elif "chicago" in location:
                    filters.center_lat = 41.8781
                    filters.center_lng = -87.6298
                    if not filters.radius_miles:
                        filters.radius_miles = 50  # Default 50 mile radius around Chicago
                    tool_trace["processing_steps"].append(f"📍 Location mapped to Chicago coordinates (41.8781, -87.6298)")
                else:
                    # For other locations, try to map them as cities or general areas
                    # This could be expanded in the future for other cities
                    tool_trace["processing_steps"].append(f"📍 General location '{args['location']}' noted but not specifically mapped")
            
            tool_trace["search_filters"] = filters.model_dump()
            active_filters = len([k for k,v in filters.model_dump().items() if v is not None and v != [] and v != ""])
            tool_trace["processing_steps"].append(f"🎯 Search filters configured: {active_filters} active filters")
            
            # Step 3: Execute database search
            tool_trace["processing_steps"].append("🔍 Executing database search with generated filters")
            
            # Use the trail searcher to perform the actual search
            trails = trail_searcher.search_trails(query, filters, request_id)
            
            # Capture database query information (simulated for this example)
            query_parts = []
            if filters.difficulty:
                query_parts.append(f"difficulty = '{filters.difficulty}'")
            if filters.distance_cap_miles:
                query_parts.append(f"distance_miles <= {filters.distance_cap_miles}")
            if filters.dogs_allowed is not None:
                query_parts.append(f"dogs_allowed = {filters.dogs_allowed}")
            if filters.features:
                query_parts.append(f"features MATCH '{' OR '.join(filters.features)}'")
            if filters.center_lat and filters.center_lng and filters.radius_miles:
                query_parts.append(f"distance_from_point({filters.center_lat}, {filters.center_lng}) <= {filters.radius_miles}")
            
            tool_trace["database_query"] = f"SELECT * FROM trails WHERE {' AND '.join(query_parts)}" if query_parts else "SELECT * FROM trails"
            
            # Step 4: Analyze and rank results
            tool_trace["processing_steps"].append(f"📊 Found {len(trails)} trails, analyzing relevance")
            
            if trails:
                # Add relevance scoring explanation
                tool_trace["processing_steps"].append("🏆 Ranking results by relevance to user query")
                
                # Enhance trail data with AI reasoning
                for trail in trails:
                    if not trail.get("why"):
                        # Generate explanation for why this trail matches
                        match_reasons = []
                        
                        if filters.difficulty and trail.get("difficulty") == filters.difficulty:
                            match_reasons.append(f"matches {filters.difficulty} difficulty preference")
                        
                        if filters.distance_cap_miles and trail.get("distance_miles", 0) <= filters.distance_cap_miles:
                            match_reasons.append(f"distance ({trail.get('distance_miles', 0)} miles) is within your {filters.distance_cap_miles} mile limit")
                        
                        if filters.dogs_allowed and trail.get("dogs_allowed"):
                            match_reasons.append("allows dogs as requested")
                        
                        if filters.features:
                            trail_features = trail.get("features", [])
                            matching_features = [f for f in filters.features if f.lower() in [tf.lower() for tf in trail_features]]
                            if matching_features:
                                match_reasons.append(f"has desired features: {', '.join(matching_features)}")
                        
                        trail["why"] = f"This trail {', '.join(match_reasons)}." if match_reasons else "This trail matches your general search criteria."
                
                # Add ranking details to processing steps
                if len(trails) > 1:
                    tool_trace["processing_steps"].append(f"📈 Results ranked by: distance match, feature relevance, difficulty alignment")
                
            else:
                tool_trace["processing_steps"].append("⚠️ No trails found matching all criteria, consider broadening search")
            
            tool_trace["result_count"] = len(trails)
            tool_trace["processing_steps"].append(f"✅ Search completed successfully with {len(trails)} relevant results")
            tool_trace["success"] = True
            
            # Record final timing
            end_time = time.time()
            tool_trace["duration_ms"] = int((end_time - start_time) * 1000)
            
            # Log the comprehensive tool trace
            logger.info(f"AI Trail Search Tool Trace (Request: {request_id}): {json.dumps(tool_trace, default=str)}")
            
            return trails
            
        except Exception as e:
            end_time = time.time()
            tool_trace["success"] = False
            tool_trace["errors"].append(str(e))
            tool_trace["processing_steps"].append(f"❌ Search failed: {str(e)}")
            tool_trace["duration_ms"] = int((end_time - start_time) * 1000) if 'start_time' in locals() else 0
            
            logger.error(f"AI trail search failed (Request: {request_id}): {e}")
            return []
    
    def _generate_no_results_message(self, search_args: Dict[str, Any], original_query: str) -> str:
        """Generate helpful message when no trails are found, with specific suggestions"""
        
        # Analyze the search criteria to provide targeted suggestions
        criteria = []
        suggestions = []
        
        # Analyze each search parameter
        if search_args.get("difficulty"):
            criteria.append(f"{search_args['difficulty']} difficulty")
            if search_args["difficulty"] == "hard":
                suggestions.append("Try searching for 'moderate' difficulty trails instead")
        
        if search_args.get("location") or search_args.get("state") or search_args.get("city"):
            location = search_args.get("location") or search_args.get("state") or search_args.get("city")
            criteria.append(f"in {location}")
            if "chicago" in location.lower():
                suggestions.append("Try expanding to 'Illinois' or 'near Chicago' for a wider search area")
            else:
                suggestions.append(f"Try searching nearby states or cities around {location}")
        
        if search_args.get("max_distance_miles"):
            criteria.append(f"under {search_args['max_distance_miles']} miles long")
            suggestions.append(f"Try increasing the distance limit to {search_args['max_distance_miles'] + 2} miles")
        
        if search_args.get("min_distance_miles"):
            criteria.append(f"over {search_args['min_distance_miles']} miles long")
            suggestions.append(f"Try reducing the minimum distance to {max(1, search_args['min_distance_miles'] - 1)} miles")
        
        if search_args.get("features"):
            features = ", ".join(search_args["features"])
            criteria.append(f"with features: {features}")
            suggestions.append("Try searching for trails with different features or remove some feature requirements")
        
        if search_args.get("dogs_allowed") is not None:
            dog_status = "dog-friendly" if search_args["dogs_allowed"] else "no-dogs-allowed"
            criteria.append(f"that are {dog_status}")
            suggestions.append("Try removing the dog policy requirement to see more options")
        
        # Build the response message
        message_parts = []
        
        # Main message
        if criteria:
            criteria_text = ", ".join(criteria)
            message_parts.append(f"🔍 **No trails found** matching your search for trails {criteria_text}.")
        else:
            message_parts.append("🔍 **No trails found** matching your search criteria.")
        
        # Add specific suggestions
        if suggestions:
            message_parts.append("\n💡 **Suggestions to find more trails:**")
            for i, suggestion in enumerate(suggestions[:3], 1):  # Limit to top 3 suggestions
                message_parts.append(f"{i}. {suggestion}")
        
        # Add general suggestions
        message_parts.append("\n🗺️ **Alternative searches you could try:**")
        message_parts.append("• 'Show me all trails in [your area]' to see what's available")
        message_parts.append("• Search for a specific trail name if you have one in mind") 
        message_parts.append("• Try broader terms like 'hiking trails near me'")
        
        return "\n".join(message_parts)
    
    async def _generate_trail_commentary(self, trails: List[Dict[str, Any]], original_query: str, search_args: Dict[str, Any]) -> str:
        """Generate helpful commentary about the search results"""
        try:
            # Create a summary of the results
            summary_parts = []
            
            if len(trails) == 1:
                summary_parts.append("✅ **Search Complete** - Found 1 trail that matches your criteria.")
            else:
                summary_parts.append(f"✅ **Search Complete** - Found {len(trails)} trails that match your criteria.")
            
            # Highlight key matches with more direct language
            if search_args.get("difficulty"):
                summary_parts.append(f"All results are {search_args['difficulty']} difficulty level.")
            
            if search_args.get("max_distance_miles"):
                summary_parts.append(f"All trails are under {search_args['max_distance_miles']} miles long.")
            
            if search_args.get("features"):
                features_str = ", ".join(search_args["features"])
                summary_parts.append(f"Filtered for: {features_str}.")
            
            # Add direct, practical recommendations
            summary_parts.append("\n🎯 **Quick Tip**: Review the distance and elevation details above to pick the best trail for your fitness level.")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate commentary: {e}")
            return "Search completed successfully!"
