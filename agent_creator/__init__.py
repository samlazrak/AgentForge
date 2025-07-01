"""
Agent Creator - A Python ML Agent Creation Framework

This package provides a framework for creating and managing AI agents
with various capabilities including research, web scraping, and data analysis.
"""

__version__ = "1.0.0"
__author__ = "Agent Creator Framework"

from .core.base_agent import BaseAgent
from .agents.research_agent import ResearchAgent
from .agents.webscraper_agent import WebscraperAgent
from .agents.data_analysis_agent import DataAnalysisAgent
from .agents.deep_researcher_agent import DeepResearcherAgent
from .utils.llm_interface import LLMInterface

__all__ = [
    "BaseAgent",
    "ResearchAgent", 
    "WebscraperAgent",
    "DataAnalysisAgent",
    "DeepResearcherAgent",
    "LLMInterface"
]