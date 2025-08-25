"""
AI Agents module for trail search

This module provides different AI agent implementations:
- CustomAgent: Direct OpenAI API implementation
- LangChainAgent: LangChain framework-based implementation
"""

from .custom_agent import CustomTrailAgent
from .langchain_agent import LangChainTrailAgent

__all__ = ["CustomTrailAgent", "LangChainTrailAgent"]
