"""
Deep Research System - A comprehensive web research tool with recursive crawling capabilities.

This package provides tools for:
- Searching DuckDuckGo for initial results
- Recursive web crawling and content extraction
- Content relevance analysis
- PDF report generation

Main Classes:
- DeepResearcher: Main orchestrator for research operations
- WebCrawler: Handles web scraping and crawling
- ContentAnalyzer: Analyzes content relevance
- ReportGenerator: Creates summaries and reports
- PDFGenerator: Generates PDF reports

Data Models:
- SearchResult: Search result from DuckDuckGo
- ScrapedContent: Content scraped from a webpage
- ResearchResult: Complete research findings
"""

from .core.researcher import DeepResearcher
from .models.data_models import SearchResult, ScrapedContent, ResearchResult
from .core.crawler import WebCrawler
from .core.analyzer import ContentAnalyzer
from .core.report import ReportGenerator, PDFGenerator

__version__ = "1.0.0"
__author__ = "Deep Research System"
__email__ = ""
__description__ = "A comprehensive web research tool with recursive crawling capabilities"

__all__ = [
    "DeepResearcher",
    "WebCrawler", 
    "ContentAnalyzer",
    "ReportGenerator",
    "PDFGenerator",
    "SearchResult",
    "ScrapedContent", 
    "ResearchResult",
]