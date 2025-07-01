"""Data models for the Deep Research System."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class SearchResult:
    """Represents a search result from DuckDuckGo"""
    title: str
    url: str
    snippet: str
    rank: int


@dataclass
class ScrapedContent:
    """Represents scraped content from a webpage"""
    url: str
    title: str = ""
    content: str = ""
    links: List[str] = field(default_factory=list)
    relevance_score: float = 0.0
    success: bool = False
    error: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchResult:
    """Final research result with all findings"""
    query: str
    initial_results: List[SearchResult] = field(default_factory=list)
    level_1_content: List[ScrapedContent] = field(default_factory=list)
    level_2_content: List[ScrapedContent] = field(default_factory=list)
    summary: str = ""
    key_findings: List[str] = field(default_factory=list)
    total_pages_crawled: int = 0
    total_links_found: int = 0
    research_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)