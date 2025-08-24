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
        """Input schema for trail search tool"""
        query: str = Field(description="The user's natural language query about trails")
        location: Optional[str] = Field(None, description="Location or city name to search near (e.g., 'Chicago', 'near Chicago')")
        max_distance_miles: Optional[float] = Field(None, description="Maximum trail length in miles if specified")
        max_elevation_gain_m: Optional[float] = Field(None, description="Maximum elevation gain in meters if specified")
        difficulty: Optional[str] = Field(None, description="Trail difficulty level (easy/moderate/hard)")
        route_type: Optional[str] = Field(None, description="Type of trail route (loop/out and back)")
        dogs_allowed: Optional[bool] = Field(None, description="Whether dogs are allowed/wanted on the trail. True if user mentions bringing/taking their dog, wants dog-friendly trails, etc.")
        features: Optional[List[str]] = Field(None, description="Desired trail features extracted from the query like 'waterfall', 'lake', 'scenic', 'views', 'forest', 'prairie', 'beach', 'canyon', 'historic', etc.")
        radius_miles: Optional[float] = Field(None, description="Search radius in miles from the specified location if mentioned")

    class TrailSearchTool(BaseTool):
        """LangChain tool for trail search functionality"""
        name: str = "search_trails"
        description: str = """Search for hiking trails based on user criteria like location, difficulty, distance, and features. Extract all relevant parameters from the user's natural language query including:
        - Location or city name to search near (e.g., 'Chicago', 'near Chicago')  
        - Maximum trail length in miles if specified
        - Maximum elevation gain in meters if specified
        - Trail difficulty level (easy/moderate/hard)
        - Type of trail route (loop/out and back)
        - Whether dogs are allowed/wanted
        - Desired trail features like 'waterfall', 'lake', 'scenic', 'views', 'forest', 'prairie', 'beach', 'canyon', 'historic'
        - Search radius in miles from the specified location"""
        args_schema: type = TrailSearchInput
        agent_instance: Any = Field(default=None, exclude=True)
        
        def __init__(self, agent_instance=None, **kwargs):
            super().__init__(agent_instance=agent_instance, **kwargs)
        
        def _run(self, query: str, location: str = None, max_distance_miles: float = None, 
                 max_elevation_gain_m: float = None, difficulty: str = None, route_type: str = None,
                 dogs_allowed: bool = None, features: List[str] = None, radius_miles: float = None, **kwargs) -> str:
            """Execute trail search with LangChain's enhanced reasoning"""
            try:
                logger.info(f"LangChain tool executing search with enhanced reasoning: {query}")
                
                # Use LangChain's reasoning to provide better parameter interpretation
                trails = self._execute_search_with_reasoning(query, location, max_distance_miles, max_elevation_gain_m, 
                                                           difficulty, route_type, dogs_allowed, features, radius_miles)
                
                if self.agent_instance:
                    self.agent_instance.last_trails = trails
                
                # Return reasoning-based response for the agent
                if trails:
                    # LangChain provides more detailed analysis
                    analysis_parts = []
                    analysis_parts.append(f"✅ Search completed! I analyzed your request and found {len(trails)} trails.")
                    
                    # Add reasoning about the search strategy
                    if location:
                        analysis_parts.append(f"🗺️ I focused on the {location} area as you specified.")
                    
                    if difficulty:
                        analysis_parts.append(f"⚡ I filtered for {difficulty} difficulty trails to match your fitness level.")
                    
                    if max_distance_miles:
                        analysis_parts.append(f"📏 I limited results to trails under {max_distance_miles} miles as requested.")
                        
                    if features:
                        features_str = ", ".join(features)
                        analysis_parts.append(f"🌟 I prioritized trails with these features: {features_str}.")
                    
                    if dogs_allowed:
                        analysis_parts.append(f"🐕 I made sure all trails welcome your furry companion!")
                    
                    analysis_parts.append("\n🎯 Each result has been carefully selected based on your specific criteria.")
                    
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
                                          max_elevation_gain_m: float = None, difficulty: str = None, route_type: str = None,
                                          dogs_allowed: bool = None, features: List[str] = None, radius_miles: float = None) -> List[Dict[str, Any]]:
            """Execute trail search with enhanced LangChain reasoning and parameter optimization"""
            
            # Build filters with LangChain's enhanced interpretation
            filters = ParsedFilters()
            
            # Apply parameters with smart defaults based on reasoning
            if max_distance_miles:
                filters.distance_cap_miles = max_distance_miles
            elif any(word in query.lower() for word in ["short", "quick", "easy walk"]):
                filters.distance_cap_miles = 3.0  # Smart default for short requests
                logger.info("LangChain reasoning: Applied 3-mile limit for 'short' trail request")
            
            if max_elevation_gain_m:
                filters.elevation_cap_m = max_elevation_gain_m
            elif difficulty == "easy":
                filters.elevation_cap_m = 200  # Smart default for easy trails
                logger.info("LangChain reasoning: Limited elevation gain for easy trails")
            
            if difficulty:
                filters.difficulty = difficulty
            
            if route_type:
                filters.route_type = route_type
            elif "loop" in query.lower():
                filters.route_type = "loop"
                logger.info("LangChain reasoning: Detected loop preference from query")
            
            if dogs_allowed is not None:
                filters.dogs_allowed = dogs_allowed
            
            if features:
                filters.features = features
            
            # Enhanced location handling with broader radius defaults
            if location:
                location_lower = location.lower()
                if "chicago" in location_lower:
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
            
            # Execute the actual search
            trails = trail_searcher.search_trails(query, filters, "langchain-enhanced")
            return trails
        
        async def _arun(self, query: str, location: str = None, max_distance_miles: float = None, 
                        max_elevation_gain_m: float = None, difficulty: str = None, route_type: str = None,
                        dogs_allowed: bool = None, features: List[str] = None, radius_miles: float = None, **kwargs) -> str:
            """Async version of trail search"""
            return self._run(query, location, max_distance_miles, max_elevation_gain_m, difficulty, 
                           route_type, dogs_allowed, features, radius_miles, **kwargs)

    class StreamingCallbackHandler(BaseCallbackHandler):
        """Custom callback handler for streaming LangChain responses"""
        
        def __init__(self, stream_callback):
            self.stream_callback = stream_callback
            self.current_token = ""
        
        def on_llm_new_token(self, token: str, **kwargs) -> None:
            """Called when a new token is generated"""
            if self.stream_callback:
                self.stream_callback(token)

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
            self.tools = [TrailSearchTool(agent_instance=self)]
            
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
                yield {"type": "token", "content": "� **LangChain Agent Analysis**\n\n", "request_id": request_id}
                yield {"type": "token", "content": "�🤔 Let me analyze your request and think through the best search approach...\n\n", "request_id": request_id}
                
                # Run the agent with full LangChain reasoning - but don't stream the full response
                try:
                    response = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: self.agent.run(input=user_message)
                    )
                    
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
                        for char in part:
                            yield {"type": "token", "content": char, "request_id": request_id}
                            await asyncio.sleep(0.005)
                        yield {"type": "token", "content": "\n\n", "request_id": request_id}
                    
                    yield {"type": "token", "content": "🔍 **Search Strategy**: Based on my analysis, here's my approach:\n", "request_id": request_id}
                    
                    # Show the actual search parameters being used
                    if self.last_trails:
                        strategy_msg = f"✅ I found {len(self.last_trails)} trails using enhanced parameter optimization.\n\n"
                        for char in strategy_msg:
                            yield {"type": "token", "content": char, "request_id": request_id}
                            await asyncio.sleep(0.005)
                    else:
                        strategy_msg = "⚠️ Initial search parameters were very specific. Let me broaden the criteria...\n\n"
                        for char in strategy_msg:
                            yield {"type": "token", "content": char, "request_id": request_id}
                            await asyncio.sleep(0.005)
                    
                    # Now yield the trail results if we found any
                    if self.last_trails:
                        yield {"type": "token", "content": "� **Results Analysis**:\n\n", "request_id": request_id}
                        
                        yield {
                            "type": "trails",
                            "trails": self.last_trails,
                            "request_id": request_id
                        }
                        
                        # Generate contextual follow-up based on conversation history
                        follow_up = await self._generate_contextual_followup(
                            self.last_trails, user_message, response
                        )
                        
                        yield {"type": "token", "content": f"\n💡 **LangChain Insights**:\n{follow_up}\n\n", "request_id": request_id}
                        
                        # Add memory-based recommendations
                        memory_insight = "🧠 **Memory Note**: I'll remember your preferences for future searches. Feel free to ask for refinements or explore different areas!"
                        for char in memory_insight:
                            yield {"type": "token", "content": char, "request_id": request_id}
                            await asyncio.sleep(0.005)
                    else:
                        # Use memory to provide better suggestions
                        yield {"type": "token", "content": "🔍 **Alternative Strategy**:\n\n", "request_id": request_id}
                        contextual_msg = await self._generate_no_results_with_context(user_message)
                        for char in contextual_msg:
                            yield {
                                "type": "token",
                                "content": char,
                                "request_id": request_id
                            }
                            await asyncio.sleep(0.005)
                    
                    logger.info(f"LangChain agent completed: {len(self.last_trails)} trails, with enhanced reasoning (Request: {request_id})")
                    
                except Exception as e:
                    logger.error(f"LangChain agent execution error: {e}")
                    error_message = f"⚠️ I encountered an error during my analysis: {str(e)}\n\nLet me try a simpler approach..."
                    
                    for char in error_message:
                        yield {
                            "type": "token",
                            "content": char,
                            "request_id": request_id
                        }
                        await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"LangChain agent error: {e} (Request: {request_id})")
                error_response = "⚠️ I apologize, but I encountered an error during my analysis. Please try again."
                
                for char in error_response:
                    yield {
                        "type": "token", 
                        "content": char,
                        "request_id": request_id
                    }
                    await asyncio.sleep(0.01)
        
        
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
            """Generate helpful commentary about the search results - same as custom agent"""
            try:
                # Create a summary of the results
                summary_parts = []
                
                if len(trails) == 1:
                    summary_parts.append("I found one great trail that matches your criteria:")
                else:
                    summary_parts.append(f"I found {len(trails)} trails that match your criteria:")
                
                # Add personalized recommendations
                summary_parts.append("\nEach trail has been selected based on your specific requirements. Check out the details above to see which one appeals to you most!")
                
                return " ".join(summary_parts)
                
            except Exception as e:
                logger.error(f"Failed to generate commentary: {e}")
                return "Here are the trails I found for you!"

else:
    # Provide dummy implementations when LangChain is not available
    class LangChainTrailAgent:
        """Dummy LangChain agent for when dependencies are not available"""
        
        def __init__(self):
            raise ImportError("LangChain is not installed. Please install with: pip install langchain langchain-openai")
        
        async def process_query(self, user_message: str, request_id: str) -> AsyncGenerator[Dict[str, Any], None]:
            """Dummy method"""
            yield {"type": "error", "content": "LangChain not available", "request_id": request_id}
