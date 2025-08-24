"""
Agent Factory for Trail Search

This module provides a factory for creating different types of AI agents
based on user preference or configuration.
"""

import logging
from typing import Union, Optional
from enum import Enum

from agents.custom_agent import CustomTrailAgent

logger = logging.getLogger("trail_search.agent_factory")

class AgentType(str, Enum):
    """Available agent types"""
    CUSTOM = "custom"
    LANGCHAIN = "langchain"

# Global agent instances
_custom_agent = None
_langchain_agent = None

def get_agent(agent_type: AgentType = AgentType.CUSTOM) -> Union[CustomTrailAgent, None]:
    """
    Get or create an agent instance based on the specified type.
    
    Args:
        agent_type: The type of agent to create (custom or langchain)
        
    Returns:
        Agent instance or None if creation fails
    """
    global _custom_agent, _langchain_agent
    
    logger.info(f"DEBUG: get_agent called with agent_type: {agent_type} (type: {type(agent_type)})")
    
    try:
        if agent_type == AgentType.CUSTOM:
            logger.info("Requested CustomTrailAgent")
            if _custom_agent is None:
                logger.info("Creating new CustomTrailAgent instance")
                _custom_agent = CustomTrailAgent()
            logger.info(f"Returning CustomTrailAgent instance for {agent_type}")
            return _custom_agent
            
        elif agent_type == AgentType.LANGCHAIN:
            logger.info("Requested LangChainTrailAgent")
            if _langchain_agent is None:
                logger.info("Creating new LangChainTrailAgent instance")
                from agents.langchain_agent import LangChainTrailAgent
                _langchain_agent = LangChainTrailAgent()
                logger.info("Successfully created LangChainTrailAgent instance")
            logger.info(f"Returning LangChainTrailAgent instance for {agent_type}")
            return _langchain_agent
        
        else:
            logger.error(f"Unknown agent type: {agent_type}")
            raise ValueError(f"Unknown agent type: {agent_type}")
            
    except Exception as e:
        logger.error(f"Failed to create {agent_type} agent: {e}")
        raise Exception(f"Failed to create {agent_type} agent: {e}")

def get_available_agents() -> dict:
    """
    Get information about available agent types.
    
    Returns:
        Dictionary with agent type information
    """
    agents = {
        "custom": {
            "name": "Custom Agent",
            "description": "Direct OpenAI API implementation with custom tool handling",
            "available": True
        }
    }
    
    # Check if LangChain is available
    try:
        from agents.langchain_agent import LANGCHAIN_AVAILABLE
        agents["langchain"] = {
            "name": "LangChain Agent", 
            "description": "LangChain framework-based agent with memory and advanced reasoning",
            "available": LANGCHAIN_AVAILABLE
        }
    except ImportError:
        agents["langchain"] = {
            "name": "LangChain Agent",
            "description": "LangChain framework-based agent (requires langchain installation)",
            "available": False
        }
    
    return agents

# Backwards compatibility
def get_trail_agent() -> Union[CustomTrailAgent, None]:
    """Legacy function for backwards compatibility - returns custom agent"""
    return get_agent(AgentType.CUSTOM)
