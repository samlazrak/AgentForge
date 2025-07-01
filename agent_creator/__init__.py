"""
Agent Creator - A Python ML Agent Creation Framework

This package provides a framework for creating and managing AI agents
with various capabilities including research and web scraping.
"""

__version__ = "1.0.0"
__author__ = "Agent Creator Framework"

from .core.base_agent import BaseAgent
from .agents.research_agent import ResearchAgent
from .agents.webscraper_agent import WebscraperAgent
from .utils.llm_interface import LLMInterface

__all__ = [
    "BaseAgent",
    "ResearchAgent", 
    "WebscraperAgent",
    "LLMInterface"
]