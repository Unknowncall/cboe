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
            logger.info(f"OpenAI API key found: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 12 else '[short]'}")
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
                    temperature=0.7
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
                                "description": "Location or city name to search near (e.g., 'Chicago', 'near Chicago')"
                            },
                            "max_distance_miles": {
                                "type": "number",
                                "description": "Maximum trail length in miles if specified"
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
- Carefully analyze user queries to extract ALL relevant search criteria
- Use the search_trails tool to find matching trails with comprehensive parameter extraction
- Provide personalized recommendations based on user criteria
- Explain why certain trails match their requirements
- Be conversational and helpful in your responses

When users ask about trails:
1. Extract ALL relevant criteria from their query including:
   - Difficulty level (easy/moderate/hard)
   - Distance preferences (if they mention "under X miles" or similar)
   - Location preferences (near Chicago, etc.)
   - Trail features (scenic, waterfall, lake, forest, prairie, views, etc.)
   - Dog policy (if they mention bringing/taking their dog, wanting dog-friendly trails)
   - Route type (loop vs out and back)
   - Elevation preferences
   - Search radius

2. Use the search_trails tool with ALL extracted parameters - don't miss any criteria
3. Present results in a friendly, informative way explaining why each trail matches
4. Highlight specific features that match their criteria
5. Offer additional suggestions or ask clarifying questions if needed

Pay special attention to:
- Dog-related keywords: "take my dog", "bring my dog", "with my dog", "dog-friendly"
- Scenic keywords: "scenic", "views", "beautiful", "vista", "panoramic", "overlook"
- Distance keywords: "under X miles", "less than", "max", "short", "long"
- Location keywords: "near Chicago", "around Chicago", "Chicago area"

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
                            
                            # Execute trail search
                            yield {"type": "token", "content": "🔍 Searching for trails...\n\n", "request_id": request_id}
                            
                            trails = await self._execute_trail_search(
                                args.get("query", user_message),
                                args,
                                request_id
                            )
                            
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
                                yield {
                                    "type": "token", 
                                    "content": "I couldn't find any trails matching your specific criteria. You might want to try expanding your search area or adjusting your requirements."
                                }
                                
                        except Exception as e:
                            logger.error(f"Tool execution failed: {e} (Request: {request_id})")
                            yield {
                                "type": "token",
                                "content": f"\n\nI encountered an error while searching for trails: {str(e)}"
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
    
    async def _execute_trail_search(self, query: str, args: Dict[str, Any], request_id: str) -> List[Dict[str, Any]]:
        """Execute trail search using AI-extracted parameters only"""
        try:
            logger.info(f"AI-only search execution for: '{query}' (Request: {request_id})")
            logger.info(f"AI-extracted parameters: {args} (Request: {request_id})")
            
            # Build filters from AI-extracted parameters only
            filters = ParsedFilters()
            
            # Use AI-extracted parameters as the only source
            if "max_distance_miles" in args:
                filters.distance_cap_miles = args["max_distance_miles"]
            if "max_elevation_gain_m" in args:
                filters.elevation_cap_m = args["max_elevation_gain_m"]
            if "difficulty" in args:
                filters.difficulty = args["difficulty"]
            if "route_type" in args:
                filters.route_type = args["route_type"]
            if "dogs_allowed" in args:
                filters.dogs_allowed = args["dogs_allowed"]
            if "features" in args:
                filters.features = args["features"]
            if "radius_miles" in args:
                filters.radius_miles = args["radius_miles"]
            
            # Parse location if provided by AI
            if "location" in args and args["location"]:
                location = args["location"].lower()
                if "chicago" in location:
                    filters.center_lat = 41.8781
                    filters.center_lng = -87.6298
                    if not filters.radius_miles:
                        filters.radius_miles = 50  # Default 50 mile radius around Chicago
            
            logger.info(f"Final AI-only filters: {filters.model_dump()} (Request: {request_id})")
            
            # Execute search with AI-provided filters
            trails = trail_searcher.search_trails(query, filters, request_id)
            
            logger.info(f"AI-only trail search completed: {len(trails)} results (Request: {request_id})")
            return trails
            
        except Exception as e:
            logger.error(f"AI-only trail search execution failed: {e} (Request: {request_id})")
            return []
    
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
